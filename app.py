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
from collections import deque
from typing import Deque, Dict, List, Optional, Set, Tuple

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
    "en": "en-US-AvaMultilingualNeural",
    "fr": "fr-FR-VivienneMultilingualNeural",
    "de": "de-DE-SeraphinaMultilingualNeural",
}

_raw_pin = os.environ.get("OPERATOR_PIN", "1092")
if _raw_pin in ("", "cop31"):
    _raw_pin = "1092"

STATE = {
    "session": SESSIONS[0],
    "source_lang": "tr-TR",
    "operator_pin": _raw_pin,
    "preferred_llm": os.environ.get("PREFERRED_LLM", "auto"),
    "tts_mode": os.environ.get("TTS_MODE", "openai"),
    "claude_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
    "claude_model": os.environ.get("ANTHROPIC_MODEL", ""),
    "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
    "gemini_model": os.environ.get("GEMINI_MODEL", ""),
    "gemini_models": [],
    "deepgram_api_key": os.environ.get("DEEPGRAM_API_KEY", ""),
    "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
    "speaker_notes": "",
    "last_llm_engine": "",
    "last_llm_error": "",
    "history": [],
    "full_transcript": [],
}

# Security: Brute-force lockout & bounded TTS whitelist for 250+ hall listeners
FAILED_PIN_BY_IP: Dict[str, List[float]] = {}
PERMANENT_TTS_TEXTS: Set[str] = {
    "Türkçe simultane ses kanalı aktif.",
    "English simultaneous audio channel active.",
    "Canal audio simultané français actif.",
    "Deutscher Simultanaudiokanal aktiv.",
}
for _demo in DEMO_SPEECHES:
    for _k in ("tr", "en", "fr", "de"):
        PERMANENT_TTS_TEXTS.add(_demo[_k].strip())

RECENT_TTS_TEXTS: Deque[str] = deque(maxlen=1200)
TTS_CACHE: Dict[str, bytes] = {}
TTS_INFLIGHT_LOCKS: Dict[str, asyncio.Lock] = {}
HTTP_CLIENT = httpx.AsyncClient(timeout=20.0)


def allow_tts_text(text: str) -> None:
    clean = (text or "").strip()
    if clean:
        RECENT_TTS_TEXTS.append(clean)


def is_tts_text_allowed(text: str) -> bool:
    clean = (text or "").strip()
    return clean in PERMANENT_TTS_TEXTS or clean in RECENT_TTS_TEXTS


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


def build_contextual_user_prompt(clean: str) -> str:
    """Includes the last 3 finalized sentences and any live speaker slide notes for grammatical & pronoun continuity."""
    parts = []
    notes = (STATE.get("speaker_notes") or "").strip()
    if notes:
        parts.append(f"[KONUŞMACI CANLI SUNUM / SLAYT NOTU (Sadece referans bağlamı)]:\n{notes[:1500]}")

    recent = [
        item for item in STATE["history"][-3:]
        if item.get("is_final") and item.get("source")
    ]
    if recent:
        ctx_lines = []
        for idx, r in enumerate(recent, 1):
            ctx_lines.append(f"  {idx}. Orijinal: {r.get('source', '')} -> TR: {r.get('tr', '')}")
        parts.append(
            "[ÖNCEKİ CÜMLELER (Sadece zamir, özne-yüklem ve anlam bütünlüğü için referans; bunları tekrar çevirme!)]:\n"
            + "\n".join(ctx_lines)
        )

    parts.append(
        "[ŞİMDİ SADECE AŞAĞIDAKİ YENİ CÜMLEYİ 4 DİLE (tr, en, fr, de) EKSİKSİZ, DOĞAL VE AKADEMİK OLARAK ÇEVİR VE SADECE GEÇERLİ JSON DÖNDÜR]:\n"
        + clean
    )
    return "\n\n".join(parts)


async def resolve_gemini_models(api_key: str) -> List[str]:
    if STATE["gemini_models"]:
        return STATE["gemini_models"]
    if STATE["gemini_model"]:
        STATE["gemini_models"] = [STATE["gemini_model"]]
        return STATE["gemini_models"]
    try:
        resp = await HTTP_CLIENT.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        )
        if resp.status_code == 200:
            candidates = []
            for m in resp.json().get("models", []):
                methods = m.get("supportedGenerationMethods") or []
                if "generateContent" not in methods:
                    continue
                name = m.get("name", "").replace("models/", "")
                low = name.lower()
                if any(bad in low for bad in ("embedding", "tts", "image", "audio", "robotics", "computer-use", "omni", "customtools", "thinking", "deep-research")):
                    continue
                if "flash" in low and "lite" not in low:
                    candidates.append(name)
            if candidates:
                stable = [c for c in candidates if "exp" not in c and "preview" not in c]
                pool = stable if stable else candidates
                def _ver_key(name: str):
                    nums = [int(x) for x in re.findall(r"\d+", name)]
                    return (1 if name.startswith("gemini-3") else 0, nums, name)
                ordered = sorted(pool, key=_ver_key, reverse=True)
                STATE["gemini_models"] = ordered[:3]
                STATE["gemini_model"] = ordered[0]
                return STATE["gemini_models"]
    except Exception:
        pass
    return ["gemini-3.8-flash", "gemini-3.0-flash"]


async def resolve_gemini_model(api_key: str) -> str:
    models = await resolve_gemini_models(api_key)
    return models[0]


async def call_claude_json(user_prompt: str, sys_prompt: str) -> Tuple[Optional[str], str]:
    if not STATE["claude_api_key"]:
        return None, "Claude API key eksik"
    model_id = await resolve_claude_model(STATE["claude_api_key"])
    try:
        resp = await HTTP_CLIENT.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": STATE["claude_api_key"],
                "anthropic-version": "2023-06-01",
                "anthropic-beta": "prompt-caching-2024-07-31",
                "content-type": "application/json",
            },
            json={
                "model": model_id,
                "max_tokens": 1100,
                "system": [
                    {
                        "type": "text",
                        "text": sys_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                "messages": [{"role": "user", "content": user_prompt}],
            },
        )
        if resp.status_code == 200:
            return resp.json()["content"][0]["text"].strip(), ""
        err = f"Claude HTTP {resp.status_code}: {resp.text[:180]}"
        print(err)
        return None, err
    except Exception as e:
        err = f"Claude Exception: {type(e).__name__}: {str(e)[:150]}"
        print(err)
        return None, err


async def call_gemini_json(user_prompt: str, sys_prompt: str) -> Tuple[Optional[str], str]:
    if not STATE["gemini_api_key"]:
        return None, "Gemini API key eksik"
    models = await resolve_gemini_models(STATE["gemini_api_key"])
    last_err = ""
    for model_id in models[:2]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={STATE['gemini_api_key']}"
        thinking_cfg = {"thinkingLevel": "MINIMAL"} if "gemini-3" in model_id.lower() else {"thinkingBudget": 0}
        payload = {
            "system_instruction": {"parts": [{"text": sys_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1100,
                "responseMimeType": "application/json",
                "thinkingConfig": thinking_cfg,
            },
        }
        try:
            resp = await HTTP_CLIENT.post(url, json=payload)
            if resp.status_code == 400 and "thinking" in resp.text.lower():
                payload["generationConfig"].pop("thinkingConfig", None)
                resp = await HTTP_CLIENT.post(url, json=payload)
            if resp.status_code == 200:
                STATE["gemini_model"] = model_id
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip(), ""
            last_err = f"Gemini ({model_id}) HTTP {resp.status_code}: {resp.text[:180]}"
            print(last_err)
            if resp.status_code in (404, 429, 503):
                continue
            return None, last_err
        except Exception as e:
            last_err = f"Gemini ({model_id}) Exception: {type(e).__name__}: {str(e)[:150]}"
            print(last_err)
            continue
    return None, last_err


async def call_openai_json(user_prompt: str, sys_prompt: str) -> Tuple[Optional[str], str]:
    if not STATE["openai_api_key"]:
        return None, "OpenAI API key eksik"
    model_id = os.environ.get("OPENAI_TRANSLATE_MODEL", "gpt-4o-mini")
    try:
        resp = await HTTP_CLIENT.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {STATE['openai_api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_id,
                "temperature": 0.1,
                "max_tokens": 1100,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip(), ""
        err = f"OpenAI ({model_id}) HTTP {resp.status_code}: {resp.text[:180]}"
        print(err)
        return None, err
    except Exception as e:
        err = f"OpenAI ({model_id}) Exception: {type(e).__name__}: {str(e)[:150]}"
        print(err)
        return None, err


def parse_llm_json(raw_json: str) -> Optional[dict]:
    if not raw_json:
        return None
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_json.strip(), flags=re.IGNORECASE)
    m = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    candidate = m.group(0) if m else cleaned
    return json.loads(candidate)


async def translate_quadrilingual(text: str, source_lang: str, is_final: bool = True) -> Tuple[Dict[str, str], str]:
    clean = text.strip()[:900]
    if not clean:
        return {"tr": "", "en": "", "fr": "", "de": ""}, "empty"

    for item in DEMO_SPEECHES:
        if item["source"].lower() == clean.lower():
            return {"tr": item["tr"], "en": item["en"], "fr": item["fr"], "de": item["de"]}, "Demo"

    src_short = source_lang.split("-")[0].lower()  # tr | en | fr | de
    session = STATE["session"]
    sys_prompt = build_quadrilingual_system_prompt(session["title"], session["speakers"])
    user_prompt = build_contextual_user_prompt(clean)

    if is_final and (STATE["claude_api_key"] or STATE["openai_api_key"] or STATE["gemini_api_key"]):
        errors = []
        pref = STATE["preferred_llm"]
        if pref == "gemini":
            order = [("Gemini", call_gemini_json), ("OpenAI", call_openai_json), ("Claude", call_claude_json)]
        elif pref == "openai":
            order = [("OpenAI", call_openai_json), ("Claude", call_claude_json), ("Gemini", call_gemini_json)]
        else:
            order = [("Claude", call_claude_json), ("OpenAI", call_openai_json), ("Gemini", call_gemini_json)]

        for engine_name, fn in order:
            try:
                raw_json, err_msg = await fn(user_prompt, sys_prompt)
                if err_msg:
                    errors.append(err_msg)
                if raw_json:
                    parsed = parse_llm_json(raw_json)
                    if parsed and all(k in parsed for k in ("tr", "en", "fr", "de")):
                        STATE["last_llm_engine"] = engine_name
                        STATE["last_llm_error"] = " | ".join(errors)
                        fixed = apply_quadrilingual_fixes(
                            clean,
                            parsed.get("tr", clean),
                            parsed.get("en", clean),
                            parsed.get("fr", clean),
                            parsed.get("de", clean),
                        )
                        return fixed, engine_name
                    else:
                        errors.append(f"{engine_name} JSON parse eksik: {raw_json[:100]}")
            except Exception as e:
                errors.append(f"{engine_name} ParseErr: {str(e)[:100]}")

        STATE["last_llm_error"] = " | ".join(errors)

    tr_out, en_out, fr_out, de_out = await asyncio.gather(
        free_translate_single(clean, src_short, "tr"),
        free_translate_single(clean, src_short, "en"),
        free_translate_single(clean, src_short, "fr"),
        free_translate_single(clean, src_short, "de"),
    )
    engine_label = "Interim" if not is_final else "GTX Yedek"
    if is_final:
        STATE["last_llm_engine"] = engine_label
    return apply_quadrilingual_fixes(clean, tr_out, en_out, fr_out, de_out), engine_label


async def _synthesize_edge_tts(text: str, use_voice: str) -> bytes:
    communicate = edge_tts.Communicate(text=text, voice=use_voice, rate="+4%")
    audio_stream = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])
    return audio_stream.getvalue()


async def _synthesize_openai_tts(text: str, lang_short: str = "tr") -> bytes:
    if not STATE.get("openai_api_key"):
        return b""
    headers = {
        "Authorization": f"Bearer {STATE['openai_api_key']}",
        "Content-Type": "application/json",
    }
    lang_names = {"tr": "Turkish", "en": "English", "fr": "French", "de": "German"}
    lang_label = lang_names.get(lang_short, "Turkish")
    instructions = (
        f"Speak in natural, idiomatic {lang_label} like an experienced human simultaneous conference interpreter. "
        "Use warm, calm, authoritative broadcast intonation, subtle natural pauses at commas, "
        "clear emphasis on key climate and legal terms, and natural rising intonation on questions. "
        "Never sound robotic or monotonous."
    )
    resp = await HTTP_CLIENT.post(
        "https://api.openai.com/v1/audio/speech",
        headers=headers,
        json={
            "model": "gpt-4o-mini-tts",
            "voice": "coral",
            "input": text[:650],
            "instructions": instructions,
            "speed": 1.02,
        },
    )
    if resp.status_code == 200:
        return resp.content
    # Fallback to tts-1 if gpt-4o-mini-tts is unavailable on the account
    resp2 = await HTTP_CLIENT.post(
        "https://api.openai.com/v1/audio/speech",
        headers=headers,
        json={"model": "tts-1", "voice": "nova", "input": text[:650], "speed": 1.04},
    )
    if resp2.status_code == 200:
        return resp2.content
    return b""


async def _synthesize_google_fallback_tts(text: str, lang_short: str) -> bytes:
    resp = await HTTP_CLIENT.get(
        "https://translate.google.com/translate_tts",
        params={"ie": "UTF-8", "client": "tw-ob", "tl": lang_short, "q": text[:200]},
        headers={"User-Agent": "Mozilla/5.0"},
    )
    if resp.status_code == 200:
        return resp.content
    return b""


async def synthesize_tts_bytes(text: str, lang_short: str) -> bytes:
    use_voice = VOICES.get(lang_short, VOICES["tr"])
    use_openai_first = (STATE.get("tts_mode", "openai") == "openai") and bool(STATE.get("openai_api_key"))
    mode_tag = "oai" if use_openai_first else "edge"
    cache_key = hashlib.md5(f"{mode_tag}:{use_voice}:{text}".encode("utf-8")).hexdigest()
    if cache_key in TTS_CACHE:
        return TTS_CACHE[cache_key]

    lock = TTS_INFLIGHT_LOCKS.setdefault(cache_key, asyncio.Lock())
    async with lock:
        if cache_key in TTS_CACHE:
            return TTS_CACHE[cache_key]

        audio_bytes = b""
        if use_openai_first:
            try:
                audio_bytes = await _synthesize_openai_tts(text, lang_short)
            except Exception:
                audio_bytes = b""
            if not audio_bytes:
                try:
                    audio_bytes = await _synthesize_edge_tts(text, use_voice)
                except Exception:
                    audio_bytes = b""
        else:
            try:
                audio_bytes = await _synthesize_edge_tts(text, use_voice)
            except Exception:
                audio_bytes = b""
            if not audio_bytes and STATE.get("openai_api_key"):
                try:
                    audio_bytes = await _synthesize_openai_tts(text, lang_short)
                except Exception:
                    audio_bytes = b""

        if not audio_bytes:
            try:
                audio_bytes = await _synthesize_google_fallback_tts(text, lang_short)
            except Exception:
                audio_bytes = b""

        if audio_bytes:
            if len(TTS_CACHE) > 500:
                for k in list(TTS_CACHE.keys())[:250]:
                    TTS_CACHE.pop(k, None)
            TTS_CACHE[cache_key] = audio_bytes

    TTS_INFLIGHT_LOCKS.pop(cache_key, None)
    return audio_bytes


async def prewarm_tts_for_hall(quad: Dict[str, str], src_lang: str) -> None:
    src_short = src_lang.split("-")[0].lower()
    targets = [ch for ch in ("tr", "en", "fr", "de") if ch != src_short and quad.get(ch)]
    await asyncio.gather(
        *(synthesize_tts_bytes(quad[ch].strip(), ch) for ch in targets),
        return_exceptions=True,
    )


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def _send_one(self, conn: WebSocket, message: dict) -> Optional[WebSocket]:
        try:
            await asyncio.wait_for(conn.send_json(message), timeout=2.5)
            return None
        except Exception:
            return conn

    async def broadcast(self, message: dict):
        conns = list(self.active_connections)
        if not conns:
            return
        results = await asyncio.gather(*(self._send_one(c, message) for c in conns))
        for dead in results:
            if dead is not None:
                self.disconnect(dead)


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
            "tts_mode": STATE["tts_mode"],
            "has_claude_key": bool(STATE["claude_api_key"]),
            "claude_model": STATE["claude_model"] or "claude-sonnet-4-20250514",
            "has_gemini_key": bool(STATE["gemini_api_key"]),
            "has_deepgram_key": bool(STATE["deepgram_api_key"]),
            "has_openai_key": bool(STATE["openai_api_key"]),
            "deepgram_api_key": STATE["deepgram_api_key"] if authorized else "",
            "speaker_notes": STATE["speaker_notes"] if authorized else "",
            "last_llm_engine": STATE["last_llm_engine"] if authorized else "",
            "last_llm_error": STATE["last_llm_error"] if authorized else "",
            "active_listeners": len(manager.active_connections),
            "glossary_count": len(QUADRILINGUAL_TERMS),
            "forbidden_count": len(FORBIDDEN_TR),
            "transcript_count": len(STATE["full_transcript"]),
            "history": STATE["history"][-15:],
        }
    )


@router.get("/api/test-llm")
async def api_test_llm(request: Request, pin: Optional[str] = Query(None)):
    client_ip = get_client_ip(request.headers, request.client.host if request.client else "")
    if not verify_operator_pin(pin, client_ip):
        return JSONResponse({"ok": False, "error": "Operatör PIN gerekli"}, status_code=403)
    sys_prompt = build_quadrilingual_system_prompt(STATE["session"]["title"], STATE["session"]["speakers"])
    user_prompt = build_contextual_user_prompt("The real test of climate leadership is delivery, not declarations.")
    t0 = time.perf_counter()
    c_raw, c_err = await call_claude_json(user_prompt, sys_prompt)
    c_ms = int((time.perf_counter() - t0) * 1000)
    t1 = time.perf_counter()
    o_raw, o_err = await call_openai_json(user_prompt, sys_prompt)
    o_ms = int((time.perf_counter() - t1) * 1000)
    t2 = time.perf_counter()
    g_raw, g_err = await call_gemini_json(user_prompt, sys_prompt)
    g_ms = int((time.perf_counter() - t2) * 1000)
    return JSONResponse(
        {
            "claude": {"ok": bool(c_raw), "ms": c_ms, "model": STATE["claude_model"], "error": c_err, "sample": (c_raw or "")[:160]},
            "openai": {"ok": bool(o_raw), "ms": o_ms, "model": os.environ.get("OPENAI_TRANSLATE_MODEL", "gpt-4o-mini"), "error": o_err, "sample": (o_raw or "")[:160]},
            "gemini": {"ok": bool(g_raw), "ms": g_ms, "model": STATE["gemini_model"], "error": g_err, "sample": (g_raw or "")[:160]},
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
        lines.append(f"[{idx}] Saat: {item.get('timestamp', '')} | Kaynak Dil: {item.get('source_lang', '')} | Motor: {item.get('engine', '')} | Oturum: {item.get('session_title', STATE['session']['title'])}")
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
async def api_tts(text: str = Query(..., min_length=1, max_length=700), lang: str = Query("tr")):
    clean_text = text.strip()
    if not is_tts_text_allowed(clean_text):
        return Response(status_code=403, content=b"Forbidden")
    lang_short = lang.split("-")[0].lower()
    audio_bytes = await synthesize_tts_bytes(clean_text, lang_short)
    if not audio_bytes:
        return Response(status_code=503, content=b"TTS unavailable")
    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Cache-Control": "public, max-age=3600"},
    )


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
            if len(raw_msg) > 6144:
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
                if "tts_mode" in data:
                    STATE["tts_mode"] = data["tts_mode"]
                    save_env_key("TTS_MODE", STATE["tts_mode"])
                if "speaker_notes" in data:
                    STATE["speaker_notes"] = (data.get("speaker_notes") or "").strip()[:2000]
                if not os.environ.get("ANTHROPIC_API_KEY") and "claude_api_key" in data and data["claude_api_key"].strip():
                    STATE["claude_api_key"] = data["claude_api_key"].strip()
                    STATE["claude_model"] = ""
                    save_env_key("ANTHROPIC_API_KEY", STATE["claude_api_key"])
                    await resolve_claude_model(STATE["claude_api_key"])
                if not os.environ.get("GEMINI_API_KEY") and "gemini_api_key" in data and data["gemini_api_key"].strip():
                    STATE["gemini_api_key"] = data["gemini_api_key"].strip()
                    STATE["gemini_model"] = ""
                    STATE["gemini_models"] = []
                    save_env_key("GEMINI_API_KEY", STATE["gemini_api_key"])
                    await resolve_gemini_model(STATE["gemini_api_key"])
                if not os.environ.get("DEEPGRAM_API_KEY") and "deepgram_api_key" in data and data["deepgram_api_key"].strip():
                    STATE["deepgram_api_key"] = data["deepgram_api_key"].strip()
                    save_env_key("DEEPGRAM_API_KEY", STATE["deepgram_api_key"])
                if not os.environ.get("OPENAI_API_KEY") and "openai_api_key" in data and data["openai_api_key"].strip():
                    STATE["openai_api_key"] = data["openai_api_key"].strip()
                    save_env_key("OPENAI_API_KEY", STATE["openai_api_key"])

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
                        "has_openai_key": bool(STATE["openai_api_key"]),
                        "active_listeners": len(manager.active_connections),
                    }
                )

            elif msg_type == "speech":
                src_text = data.get("text", "").strip()[:900]
                is_final = bool(data.get("is_final", False))
                src_lang = data.get("source_lang") or STATE["source_lang"]
                if not src_text:
                    continue
                t0 = time.perf_counter()
                quad, engine_name = await translate_quadrilingual(src_text, src_lang, is_final=is_final)
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
                    "engine": engine_name,
                    "llm_error": STATE["last_llm_error"] if is_final else "",
                    "is_final": is_final,
                    "latency_ms": latency_ms,
                    "timestamp": time.strftime("%H:%M:%S"),
                }
                if is_final:
                    for _k in ("tr", "en", "fr", "de"):
                        if quad.get(_k):
                            allow_tts_text(quad[_k])
                    asyncio.create_task(prewarm_tts_for_hall(quad, src_lang))
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
                    allow_tts_text(sample[_k])
                asyncio.create_task(prewarm_tts_for_hall(sample, sample["source_lang"]))
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
                    "engine": "Demo",
                    "llm_error": "",
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
