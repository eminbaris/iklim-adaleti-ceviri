# -*- coding: utf-8 -*-
import asyncio
import hashlib
import hmac
import io
import json
import os
import re
import socket
import time
from typing import Dict, List, Optional, Set

import edge_tts
import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, Response

from glossary import (
    DEMO_SPEECHES,
    FORBIDDEN_TR,
    QUADRILINGUAL_TERMS,
    SESSIONS,
    build_quadrilingual_system_prompt,
)

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)

# Disable public Swagger/OpenAPI endpoints (/docs, /redoc, /openapi.json) against scanners
app = FastAPI(
    title="COP31 İklim Adaleti Forumu - 4 Dilli Simultane Sistemi",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
router = APIRouter()

VOICES = {
    "tr": "tr-TR-EmelNeural",
    "en": "en-US-AriaNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
}

_raw_pin = os.environ.get("OPERATOR_PIN", "1092")
if _raw_pin in ("", "cop31"):
    _raw_pin = "1092"

STATE = {
    "session": SESSIONS[0],
    "source_lang": "tr-TR",
    "operator_pin": _raw_pin,
    "preferred_llm": os.environ.get("PREFERRED_LLM", "auto"),
    "claude_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
    "claude_model": os.environ.get("ANTHROPIC_MODEL", ""),
    "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
    "deepgram_api_key": os.environ.get("DEEPGRAM_API_KEY", ""),
    "history": [],
    "full_transcript": [],
}

# Security: Brute-force lockout & TTS whitelist
FAILED_PIN_BY_IP: Dict[str, List[float]] = {}
ALLOWED_TTS_TEXTS: Set[str] = {
    "Türkçe simultane ses kanalı aktif.",
    "English simultaneous audio channel active.",
    "Canal audio simultané français actif.",
    "Deutscher Simultanaudiokanal aktiv.",
}
for _demo in DEMO_SPEECHES:
    for _k in ("tr", "en", "fr", "de"):
        ALLOWED_TTS_TEXTS.add(_demo[_k])

TTS_CACHE: Dict[str, bytes] = {}
HTTP_CLIENT = httpx.AsyncClient(timeout=8.0)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


def get_client_ip(headers, client_host: str = "") -> str:
    fwd = headers.get("x-forwarded-for") or headers.get("x-real-ip")
    if fwd:
        return fwd.split(",")[0].strip()
    return client_host or "unknown"


def verify_operator_pin(pin: Optional[str], ip: str) -> bool:
    now = time.time()
    attempts = [t for t in FAILED_PIN_BY_IP.get(ip, []) if now - t < 600]
    FAILED_PIN_BY_IP[ip] = attempts
    if len(attempts) >= 5:
        return False
    candidate = (pin or "").strip()
    if not candidate:
        return False
    ok = hmac.compare_digest(candidate.encode("utf-8"), STATE["operator_pin"].encode("utf-8"))
    if not ok:
        attempts.append(now)
        FAILED_PIN_BY_IP[ip] = attempts
    else:
        FAILED_PIN_BY_IP.pop(ip, None)
    return ok


def save_env_key(key_name: str, value: str) -> None:
    try:
        lines = []
        if os.path.exists(ENV_PATH):
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                lines = [ln for ln in f.read().splitlines() if not ln.startswith(f"{key_name}=")]
        lines.append(f"{key_name}={value}")
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass


async def resolve_claude_model(api_key: str) -> str:
    if STATE["claude_model"]:
        return STATE["claude_model"]
    try:
        resp = await HTTP_CLIENT.get(
            "https://api.anthropic.com/v1/models",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
        )
        if resp.status_code == 200:
            models = [m["id"] for m in resp.json().get("data", [])]
            for m in models:
                if "sonnet" in m.lower():
                    STATE["claude_model"] = m
                    return m
            if models:
                STATE["claude_model"] = models[0]
                return models[0]
    except Exception:
        pass
    return "claude-sonnet-4-20250514"


def get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def apply_quadrilingual_fixes(source_text: str, tr_text: str, en_text: str, fr_text: str, de_text: str) -> Dict[str, str]:
    src_low = source_text.lower()

    for bad, good in FORBIDDEN_TR:
        tr_text = re.sub(rf"\b{re.escape(bad)}\b", good, tr_text, flags=re.IGNORECASE)

    for tr_term, en_term, fr_term, de_term in QUADRILINGUAL_TERMS:
        if any(t.lower() in src_low for t in (tr_term, en_term, fr_term, de_term)):
            if "commons" in en_term.lower():
                en_text = re.sub(r"\b(partners|joint owners|house of commons)\b", "the commons", en_text, flags=re.IGNORECASE)
                fr_text = re.sub(r"\b(associés|partenaires|chambre des communes)\b", "les biens communs", fr_text, flags=re.IGNORECASE)
                de_text = re.sub(r"\b(Partner|Gesellschafter|Unterhaus)\b", "Gemeingüter", de_text, flags=re.IGNORECASE)
            if "non-regression" in en_term.lower():
                en_text = re.sub(r"\b(ban on going back|prohibition of regression)\b", "principle of non-regression", en_text, flags=re.IGNORECASE)
                fr_text = re.sub(r"\b(interdiction de reculer|interdiction de régression)\b", "principe de non-régression", fr_text, flags=re.IGNORECASE)

    return {"tr": tr_text, "en": en_text, "fr": fr_text, "de": de_text}


async def free_translate_single(text: str, src_short: str, tgt_short: str) -> str:
    if src_short == tgt_short:
        return text
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": src_short, "tl": tgt_short, "dt": "t", "q": text}
        resp = await HTTP_CLIENT.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            return "".join(seg[0] for seg in data[0] if seg[0])
    except Exception:
        pass
    return text


async def call_claude_json(clean: str, sys_prompt: str) -> Optional[str]:
    if not STATE["claude_api_key"]:
        return None
    model_id = await resolve_claude_model(STATE["claude_api_key"])
    resp = await HTTP_CLIENT.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": STATE["claude_api_key"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model_id,
            "max_tokens": 600,
            "temperature": 0.1,
            "system": sys_prompt,
            "messages": [{"role": "user", "content": clean}],
        },
    )
    if resp.status_code == 200:
        return resp.json()["content"][0]["text"].strip()
    return None


async def call_gemini_json(clean: str, sys_prompt: str) -> Optional[str]:
    if not STATE["gemini_api_key"]:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={STATE['gemini_api_key']}"
    payload = {
        "system_instruction": {"parts": [{"text": sys_prompt}]},
        "contents": [{"parts": [{"text": clean}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 600,
            "responseMimeType": "application/json",
        },
    }
    resp = await HTTP_CLIENT.post(url, json=payload)
    if resp.status_code == 200:
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    return None


async def translate_quadrilingual(text: str, source_lang: str, is_final: bool = True) -> Dict[str, str]:
    clean = text.strip()[:600]
    if not clean:
        return {"tr": "", "en": "", "fr": "", "de": ""}

    for item in DEMO_SPEECHES:
        if item["source"].lower() == clean.lower():
            return {"tr": item["tr"], "en": item["en"], "fr": item["fr"], "de": item["de"]}

    src_short = source_lang.split("-")[0].lower()  # tr | en | fr | de
    session = STATE["session"]
    sys_prompt = build_quadrilingual_system_prompt(session["title"], session["speakers"])

    if is_final and (STATE["claude_api_key"] or STATE["gemini_api_key"]):
        try:
            raw_json = None
            pref = STATE["preferred_llm"]
            if pref == "gemini":
                raw_json = await call_gemini_json(clean, sys_prompt) or await call_claude_json(clean, sys_prompt)
            else:
                raw_json = await call_claude_json(clean, sys_prompt) or await call_gemini_json(clean, sys_prompt)

            if raw_json:
                m = re.search(r"\{.*\}", raw_json, flags=re.DOTALL)
                parsed = json.loads(m.group(0) if m else raw_json)
                return apply_quadrilingual_fixes(
                    clean,
                    parsed.get("tr", clean),
                    parsed.get("en", clean),
                    parsed.get("fr", clean),
                    parsed.get("de", clean),
                )
        except Exception:
            pass

    tr_out, en_out, fr_out, de_out = await asyncio.gather(
        free_translate_single(clean, src_short, "tr"),
        free_translate_single(clean, src_short, "en"),
        free_translate_single(clean, src_short, "fr"),
        free_translate_single(clean, src_short, "de"),
    )
    return apply_quadrilingual_fixes(clean, tr_out, en_out, fr_out, de_out)


async def synthesize_tts_bytes(text: str, lang_short: str) -> bytes:
    use_voice = VOICES.get(lang_short, VOICES["tr"])
    cache_key = hashlib.md5(f"{use_voice}:{text}".encode("utf-8")).hexdigest()
    if cache_key in TTS_CACHE:
        return TTS_CACHE[cache_key]

    communicate = edge_tts.Communicate(text=text, voice=use_voice, rate="+8%")
    audio_stream = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])

    audio_bytes = audio_stream.getvalue()
    if len(TTS_CACHE) > 300:
        TTS_CACHE.clear()
    TTS_CACHE[cache_key] = audio_bytes
    return audio_bytes


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for d in dead:
            self.disconnect(d)


manager = ConnectionManager()


@router.get("/api/info")
async def api_info(request: Request, pin: Optional[str] = Query(None)):
    lan_ip = get_lan_ip()
    if STATE["claude_api_key"] and not STATE["claude_model"]:
        await resolve_claude_model(STATE["claude_api_key"])
    client_ip = get_client_ip(request.headers, request.client.host if request.client else "")
    authorized = verify_operator_pin(pin, client_ip) if pin else False
    return JSONResponse(
        {
            "lan_ip": lan_ip,
            "listen_url": f"http://{lan_ip}:8000/dinle",
            "screen_url": f"http://{lan_ip}:8000/ekran",
            "authorized": authorized,
            "sessions": SESSIONS,
            "current_session": STATE["session"],
            "source_lang": STATE["source_lang"],
            "preferred_llm": STATE["preferred_llm"],
            "has_claude_key": bool(STATE["claude_api_key"]),
            "claude_model": STATE["claude_model"] or "claude-sonnet-5-5",
            "has_gemini_key": bool(STATE["gemini_api_key"]),
            "has_deepgram_key": bool(STATE["deepgram_api_key"]),
            "deepgram_api_key": STATE["deepgram_api_key"] if authorized else "",
            "glossary_count": len(QUADRILINGUAL_TERMS),
            "forbidden_count": len(FORBIDDEN_TR),
            "transcript_count": len(STATE["full_transcript"]),
            "history": STATE["history"][-15:],
        }
    )


@router.get("/api/transcript")
async def api_transcript(request: Request, pin: Optional[str] = Query(None)):
    client_ip = get_client_ip(request.headers, request.client.host if request.client else "")
    if not verify_operator_pin(pin, client_ip):
        return Response(status_code=403, content="Operatör PIN gerekli.".encode("utf-8"))
    lines = [
        "======================================================================",
        "COP31 ULUSLARARASI İKLİM ADALETİ FORUMU — 4 DİLLİ SİMULTANE TUTANAĞI",
        f"Aktif Oturum: {STATE['session']['day']} | {STATE['session']['title']}",
        f"Konuşmacılar: {STATE['session']['speakers']}",
        "======================================================================",
        "",
    ]
    items = STATE["full_transcript"] or STATE["history"]
    for idx, item in enumerate(items, 1):
        lines.append(f"[{idx}] Saat: {item.get('timestamp', '')} | Kaynak Dil: {item.get('source_lang', '')} | Oturum: {item.get('session_title', STATE['session']['title'])}")
        lines.append(f"  🎙️ Orijinal: {item.get('source', '')}")
        lines.append(f"  🇹🇷 TR: {item.get('tr', '')}")
        lines.append(f"  🇬🇧 EN: {item.get('en', '')}")
        lines.append(f"  🇫🇷 FR: {item.get('fr', '')}")
        lines.append(f"  🇩🇪 DE: {item.get('de', '')}")
        lines.append("-" * 70)
    content = "\n".join(lines).encode("utf-8")
    filename = f"COP31_Simultane_Tutanak_{time.strftime('%Y-%m-%d_%H-%M')}.txt"
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/api/tts")
async def api_tts(text: str = Query(..., min_length=1, max_length=600), lang: str = Query("tr")):
    clean_text = text.strip()
    if clean_text not in ALLOWED_TTS_TEXTS:
        return Response(status_code=403, content=b"Forbidden")
    lang_short = lang.split("-")[0].lower()
    audio_bytes = await synthesize_tts_bytes(clean_text, lang_short)
    return Response(content=audio_bytes, media_type="audio/mpeg")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    client_ip = get_client_ip(websocket.headers, websocket.client.host if websocket.client else "")
    unauthorized_attempts = 0
    await websocket.send_json(
        {
            "type": "init",
            "session": STATE["session"],
            "source_lang": STATE["source_lang"],
            "history": STATE["history"][-10:],
        }
    )
    try:
        while True:
            raw_msg = await websocket.receive_text()
            if len(raw_msg) > 4096:
                continue
            data = json.loads(raw_msg)
            msg_type = data.get("type")

            if msg_type in ("config", "speech", "demo", "clear"):
                if not verify_operator_pin(data.get("pin", ""), client_ip):
                    unauthorized_attempts += 1
                    if unauthorized_attempts >= 5:
                        await websocket.close(code=1008)
                        break
                    continue

            if msg_type == "config":
                session_id = data.get("session_id")
                for s in SESSIONS:
                    if s["id"] == session_id:
                        STATE["session"] = s
                        break
                if "source_lang" in data:
                    STATE["source_lang"] = data["source_lang"]
                if "preferred_llm" in data:
                    STATE["preferred_llm"] = data["preferred_llm"]
                    save_env_key("PREFERRED_LLM", STATE["preferred_llm"])
                if not os.environ.get("ANTHROPIC_API_KEY") and "claude_api_key" in data and data["claude_api_key"].strip():
                    STATE["claude_api_key"] = data["claude_api_key"].strip()
                    STATE["claude_model"] = ""
                    save_env_key("ANTHROPIC_API_KEY", STATE["claude_api_key"])
                    await resolve_claude_model(STATE["claude_api_key"])
                if not os.environ.get("GEMINI_API_KEY") and "gemini_api_key" in data and data["gemini_api_key"].strip():
                    STATE["gemini_api_key"] = data["gemini_api_key"].strip()
                    save_env_key("GEMINI_API_KEY", STATE["gemini_api_key"])
                if not os.environ.get("DEEPGRAM_API_KEY") and "deepgram_api_key" in data and data["deepgram_api_key"].strip():
                    STATE["deepgram_api_key"] = data["deepgram_api_key"].strip()
                    save_env_key("DEEPGRAM_API_KEY", STATE["deepgram_api_key"])

                await manager.broadcast(
                    {
                        "type": "session_update",
                        "session": STATE["session"],
                        "source_lang": STATE["source_lang"],
                        "preferred_llm": STATE["preferred_llm"],
                        "has_claude_key": bool(STATE["claude_api_key"]),
                        "claude_model": STATE["claude_model"],
                        "has_gemini_key": bool(STATE["gemini_api_key"]),
                        "has_deepgram_key": bool(STATE["deepgram_api_key"]),
                    }
                )

            elif msg_type == "speech":
                src_text = data.get("text", "").strip()[:600]
                is_final = bool(data.get("is_final", False))
                src_lang = data.get("source_lang") or STATE["source_lang"]
                if not src_text:
                    continue
                t0 = time.perf_counter()
                quad = await translate_quadrilingual(src_text, src_lang, is_final=is_final)
                latency_ms = int((time.perf_counter() - t0) * 1000)

                payload = {
                    "type": "subtitle",
                    "id": int(time.time() * 1000),
                    "session_title": STATE["session"]["title"],
                    "source_lang": src_lang,
                    "source": src_text,
                    "tr": quad["tr"],
                    "en": quad["en"],
                    "fr": quad["fr"],
                    "de": quad["de"],
                    "is_final": is_final,
                    "latency_ms": latency_ms,
                    "timestamp": time.strftime("%H:%M:%S"),
                }
                if is_final:
                    for _k in ("tr", "en", "fr", "de"):
                        if quad.get(_k):
                            ALLOWED_TTS_TEXTS.add(quad[_k].strip())
                    if len(ALLOWED_TTS_TEXTS) > 600:
                        ALLOWED_TTS_TEXTS.clear()
                    STATE["history"].append(payload)
                    if len(STATE["history"]) > 50:
                        STATE["history"] = STATE["history"][-50:]
                    STATE["full_transcript"].append(payload)
                    if len(STATE["full_transcript"]) > 5000:
                        STATE["full_transcript"] = STATE["full_transcript"][-5000:]

                await manager.broadcast(payload)

            elif msg_type == "demo":
                idx = int(data.get("index", 0)) % len(DEMO_SPEECHES)
                sample = DEMO_SPEECHES[idx]
                for _k in ("tr", "en", "fr", "de"):
                    ALLOWED_TTS_TEXTS.add(sample[_k].strip())
                payload = {
                    "type": "subtitle",
                    "id": int(time.time() * 1000),
                    "session_title": STATE["session"]["title"],
                    "source_lang": sample["source_lang"],
                    "source": sample["source"],
                    "tr": sample["tr"],
                    "en": sample["en"],
                    "fr": sample["fr"],
                    "de": sample["de"],
                    "is_final": True,
                    "latency_ms": 220,
                    "timestamp": time.strftime("%H:%M:%S"),
                }
                STATE["history"].append(payload)
                STATE["full_transcript"].append(payload)
                await manager.broadcast(payload)

            elif msg_type == "clear":
                STATE["history"].clear()
                await manager.broadcast({"type": "clear"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@router.get("/", response_class=HTMLResponse)
async def operator_page():
    with open(os.path.join(os.path.dirname(__file__), "static", "operator.html"), encoding="utf-8") as f:
        return f.read()


@router.get("/ekran", response_class=HTMLResponse)
async def screen_page():
    with open(os.path.join(os.path.dirname(__file__), "static", "ekran.html"), encoding="utf-8") as f:
        return f.read()


@router.get("/dinle", response_class=HTMLResponse)
async def listen_page():
    with open(os.path.join(os.path.dirname(__file__), "static", "dinle.html"), encoding="utf-8") as f:
        return f.read()


@app.get("/ceviri", response_class=HTMLResponse)
async def operator_page_no_slash():
    return await operator_page()


app.include_router(router, prefix="")
app.include_router(router, prefix="/ceviri")
