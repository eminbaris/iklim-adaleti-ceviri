# -*- coding: utf-8 -*-
"""
Uluslararası İklim Adaleti Forumu (15-18 Kasım 2026 - Antalya Barosu)
ÇİFT YÖNLÜ 4 KANAL (TÜRKÇE <-> İNGİLİZCE <-> FRANSIZCA <-> ALMANCA) MASTER SÖZLÜK
iklimadaleti.org (@iklimadaletiforumu) ve cevrehukuku.org (Çevre Hukuku Ağı)
"""

SESSIONS = [
    {
        "id": "15_kasim_halk_kursusu",
        "day": "15 Kasım 2026 | 14.00 - 20.00",
        "title": "Yaşam Alanları, Mücadeleler ve İklim Adaleti - Halk Kürsüsü",
        "speakers": "Yerel Ekoloji Platformları ve Yaşam Savunucuları",
        "default_lang": "tr-TR",
    },
    {
        "id": "16_kasim_1000",
        "day": "16 Kasım 2026 | 10.00 - 12.00",
        "title": "Doğanın Metalaştırılması, Büyüme ve Sermaye Birikimi",
        "speakers": "Markus Wissen, Jenny Simon, Ali Yalçın Göymen",
        "default_lang": "de-DE",
    },
    {
        "id": "16_kasim_1330",
        "day": "16 Kasım 2026 | 13.30 - 15.30",
        "title": "Ekoloji Mücadelesinde Adalet",
        "speakers": "Şükrü Kibar, Emine Büyüknohutçu, Duygu Yıldız, Ulaş Lokumcu, Öznur Tosun, Gerson Barbosa Borges (MPA Brazil)",
        "default_lang": "tr-TR",
    },
    {
        "id": "16_kasim_1600",
        "day": "16 Kasım 2026 | 16.00 - 19.30",
        "title": "Küresel Afetler, Kamuculuk ve Toplumsal Cinsiyet",
        "speakers": "Nilgün Karasu, Seda Yurtcanlı, Cihan Uzunçarşılı Baysal, Gül Işın, Doğukan Yurttaş, İlkay Öz, İbrahim Gündüz, Hayri Kozanoğlu, Tuğçe Duru",
        "default_lang": "tr-TR",
    },
    {
        "id": "17_kasim_1000",
        "day": "17 Kasım 2026 | 10.00 - 12.30",
        "title": "Uluslararası İklim Hukuku Göstergeleri, İklim Adaleti ve Kırılgan Alanlar",
        "speakers": "Prof. Dr. Michel Prieur (CIDCE), Julien Prieur, Laurent Vassallo, Elisa Le Yondre, Prof. Dr. İbrahim Özden Kaboğlu, Prof. Dr. Pasquale Policastro",
        "default_lang": "fr-FR",
    },
    {
        "id": "17_kasim_1430",
        "day": "17 Kasım 2026 | 14.30 - 17.30",
        "title": "Ekoloji Haberciliği, Şirket Suçları ve Türler Arası İklim Adaleti",
        "speakers": "Özgür Gürbüz, Pelin Cengiz, Gökay Başcan, Özer Akdemir, Av. Aylin Çiller Akbaş",
        "default_lang": "tr-TR",
    },
    {
        "id": "17_kasim_1730",
        "day": "17 Kasım 2026 | 17.30 - 19.30",
        "title": "Endüstriyel Tarımın İklim Krizine Etkileri, Gıda Egemenliği ve Enerji/Madencilik",
        "speakers": "Ali Bülent Erdem (Çiftçi-Sen), Umut Kocagöz, Halit Konanç, La Via Campesina, Adnan Çobanoğlu, Funda Öz Akcura, Alev Yılmaz, Dr. Hasan Sait Ersan Ter, Dicle Dilan Salman",
        "default_lang": "tr-TR",
    },
]

# 4 Dilli Eşdeğerlik Tablosu (TR <-> EN <-> FR <-> DE)
QUADRILINGUAL_TERMS = [
    ("iklim adaleti", "climate justice", "justice climatique", "Klimagerechtigkeit"),
    ("ekolojik adalet", "ecological justice", "justice écologique", "ökologische Gerechtigkeit"),
    ("doğanın metalaştırılması", "commodification of nature", "marchandisation de la nature", "Kommodifizierung (Inwertsetzung) der Natur"),
    ("sermaye birikimi", "capital accumulation", "accumulation du capital", "Kapitalakkumulation"),
    ("emperyal yaşam tarzı", "imperial mode of living", "mode de vie impérial", "imperiale Lebensweise"),
    ("müşterekler", "the commons", "les biens communs", "Gemeingüter (Allmende)"),
    ("küresel müşterekler", "global commons", "biens communs mondiaux", "globale Gemeingüter"),
    ("yeşil aklama", "greenwashing", "écoblanchiment", "Grünfärberei (Greenwashing)"),
    ("yeşil kapitalizm", "green capitalism", "capitalisme vert", "grüner Kapitalismus"),
    ("ekokırım", "ecocide", "écocide", "Ökozid"),
    ("ekokırım suçu", "crime of ecocide", "crime d'écocide", "Verbrechen des Ökozids"),
    ("şirket suçları", "corporate crimes", "crimes d'entreprise", "Unternehmensverbrechen"),
    ("kazanılmış çevre haklarında geriye gidiş yasağı", "principle of non-regression", "principe de non-régression", "Nicht-Regressionsprinzip (Rückschrittsverbot im Umweltrecht)"),
    ("gerilememe ilkesi", "principle of non-regression", "principe de non-régression", "Nicht-Regressionsprinzip"),
    ("hukuki etkililik göstergeleri", "legal indicators of effectiveness", "indicateurs juridiques d'effectivité", "Rechtsindikatoren der Wirksamkeit"),
    ("ihtiyat ilkesi", "precautionary principle", "principe de précaution", "Vorsorgeprinzip"),
    ("önleme ilkesi", "prevention principle", "principe de prévention", "Präventionsprinzip"),
    ("kirleten öder ilkesi", "polluter pays principle", "principe pollueur-payeur", "Verursacherprinzip"),
    ("Çevresel Etki Değerlendirmesi (ÇED)", "Environmental Impact Assessment (EIA)", "Étude d'impact environnemental (EIE)", "Umweltverträglichkeitsprüfung (UVP)"),
    ("stratejik davalar", "strategic litigation", "contentieux stratégique", "strategische Prozessführung"),
    ("çevre hakkı", "right to a healthy environment", "droit à l'environnement", "Recht auf eine intakte Umwelt"),
    ("çevre devleti", "environmental state", "État environnemental", "Umweltstaat"),
    ("çevresel anayasacılık", "environmental constitutionalism", "constitutionnalisme environnemental", "ökologischer Konstitutionalismus"),
    ("küresel anayasacılık", "global constitutionalism", "constitutionnalisme global", "globaler Konstitutionalismus"),
    ("kolektif haklar", "collective rights", "droits collectifs", "Kollektivrechte"),
    ("kırılgan alanlar", "vulnerable areas", "zones vulnérables", "vulnerable Gebiete"),
    ("kırılgan gruplar", "vulnerable groups", "populations vulnérables", "vulnerable Gruppen"),
    ("iklim nedeniyle yerinden edilmiş kişiler", "climate-displaced persons", "personnes déplacées climatiques", "klimabedingt Vertriebene"),
    ("Sürdürülebilir Kalkınma Amacı 14 (SKA 14)", "Sustainable Development Goal 14 (SDG 14)", "Objectif de développement durable 14 (ODD 14)", "Nachhaltigkeitsziel 14 (SDG 14)"),
    ("gıda egemenliği", "food sovereignty", "souveraineté alimentaire", "Ernährungssouveränität"),
    ("gıda güvencesi", "food security", "sécurité alimentaire", "Ernährungssicherheit"),
    ("köylü tarımı", "peasant agriculture", "agriculture paysanne", "bäuerliche Landwirtschaft"),
    ("agroekoloji", "agroecology", "agroécologie", "Agrarökologie"),
    ("endüstriyel tarım", "industrial agriculture", "agriculture industrielle", "industrielle Landwirtschaft"),
    ("şirket tarımı", "agribusiness", "agro-industrie", "Agrarindustrie"),
    ("tarım zehirleri (pestisitler)", "toxic pesticides / agrochemicals", "pesticides / produits phytosanitaires", "Pestizide (Agrargifte)"),
    ("tohum egemenliği", "seed sovereignty", "souveraineté semencière", "Saatgutsouveränität"),
    ("türler arası iklim adaleti", "interspecies climate justice", "justice climatique inter-espèces", "speziesübergreifende Klimagerechtigkeit"),
    ("hayvan özgürlüğü", "animal liberation", "libération animale", "Tierbefreiung"),
    ("yaşam savunucuları", "environmental and land defenders", "défenseurs de l'environnement et du vivant", "Umwelt- und Lebensraumverteidiger"),
    ("yaşam alanları", "living spaces and habitats", "espaces de vie", "Lebensräume"),
    ("doğa talanı (ekstraktivizm)", "plunder of nature / extractivism", "pillage de la nature / extractivisme", "Naturplünderung (Extraktivismus)"),
    ("kamuculuk", "public ownership and publicness", "service public et appropriation publique", "Gemeinwirtschaft und öffentliches Eigentum"),
    ("bakım emeği", "care labor", "travail du soin (care)", "Sorgearbeit (Care-Arbeit)"),
    ("adil geçiş", "just transition", "transition juste", "gerechter Übergang (Just Transition)"),
    ("zaman adaleti", "time justice", "justice temporelle", "Zeitgerechtigkeit"),
]

FORBIDDEN_TR = [
    ("yeşil yıkama", "yeşil aklama"),
    ("tarım ilacı", "tarım zehri (pestisit)"),
    ("tarım ilaçları", "tarım zehirleri (pestisitler)"),
    ("zirai ilaç", "tarım zehri"),
    ("bitki sağlığı ürünleri", "tarım zehirleri (pestisitler)"),
    ("avam kamarası", "müşterekler"),
    ("ortak mallar", "müşterekler"),
    ("ortaklar", "müşterekler"),
    ("gıda hakimiyeti", "gıda egemenliği"),
    ("yemek egemenliği", "gıda egemenliği"),
    ("besin egemenliği", "gıda egemenliği"),
    ("regresyon olmama", "geriye gidiş yasağı (gerilememe)"),
    ("çevreciler", "yaşam savunucuları"),
    ("ekolojik cinayet", "ekokırım"),
    ("savunmasız gruplar", "kırılgan gruplar"),
    ("hassas alanlar", "kırılgan alanlar"),
]

# 4 Dilli Örnek Konuşmalar (TR, DE, FR, EN)
DEMO_SPEECHES = [
    {
        "source_lang": "tr-TR",
        "source": "[TR - Türk Konuşmacı] COP31 şirketlerin değil, emeğin ve halklarındır; doğanın metalaştırılmasına ve yeşil aklamaya karşı müştereklerimizi ve yaşam alanlarımızı savunuyoruz.",
        "tr": "COP31 şirketlerin değil, emeğin ve halklarındır; doğanın metalaştırılmasına ve yeşil aklamaya karşı müştereklerimizi ve yaşam alanlarımızı savunuyoruz.",
        "en": "COP31 belongs to labor and the peoples, not corporations; we defend our commons and living spaces against the commodification of nature and greenwashing.",
        "fr": "La COP31 appartient aux travailleurs et aux peuples, pas aux entreprises ; nous défendons nos biens communs et nos espaces de vie contre la marchandisation de la nature et l'écoblanchiment.",
        "de": "Die COP31 gehört den Arbeitenden und den Völkern, nicht den Konzernen; wir verteidigen unsere Gemeingüter und Lebensräume gegen die Kommodifizierung der Natur und Greenwashing.",
    },
    {
        "source_lang": "de-DE",
        "source": "[DE - Markus Wissen & Jenny Simon] Die imperiale Lebensweise, die Kommodifizierung der Natur und die endlose Kapitalakkumulation zerstören die globalen Gemeingüter.",
        "tr": "Emperyal yaşam tarzı, doğanın metalaştırılması ve sınırsız sermaye birikimi küresel müşterekleri tahrip ediyor.",
        "en": "The imperial mode of living, the commodification of nature, and endless capital accumulation are destroying the global commons.",
        "fr": "Le mode de vie impérial, la marchandisation de la nature et l'accumulation sans fin du capital détruisent les biens communs mondiaux.",
        "de": "Die imperiale Lebensweise, die Kommodifizierung der Natur und die endlose Kapitalakkumulation zerstören die globalen Gemeingüter.",
    },
    {
        "source_lang": "fr-FR",
        "source": "[FR - Prof. Dr. Michel Prieur] Le principe de non-régression et les indicateurs juridiques d'effectivité sont essentiels pour protéger les déplacés climatiques et les zones vulnérables dans le cadre de l'ODD 14.",
        "tr": "Kazanılmış çevre haklarında geriye gidiş yasağı (gerilememe ilkesi) ve hukuki etkililik göstergeleri, SKA 14 kapsamında iklim nedeniyle yerinden edilmiş kişileri ve kırılgan alanları korumak için hayati önemdedir.",
        "en": "The principle of non-regression and legal indicators of effectiveness are essential to protect climate-displaced persons and vulnerable areas under SDG 14.",
        "fr": "Le principe de non-régression et les indicateurs juridiques d'effectivité sont essentiels pour protéger les déplacés climatiques et les zones vulnérables dans le cadre de l'ODD 14.",
        "de": "Das Nicht-Regressionsprinzip und die Rechtsindikatoren der Wirksamkeit sind von entscheidender Bedeutung, um klimabedingt Vertriebene und vulnerable Gebiete im Rahmen von SDG 14 zu schützen.",
    },
    {
        "source_lang": "en-US",
        "source": "[EN - La Via Campesina] Peasant movements and environmental defenders demand food sovereignty and agroecology against agribusiness, pesticides, corporate crimes, and ecocide of the commons.",
        "tr": "Köylü hareketleri ve yaşam savunucuları; şirket tarımına, tarım zehirlerine, şirket suçlarına ve müştereklerin ekokırımına karşı gıda egemenliği ve agroekoloji talep ediyor.",
        "en": "Peasant movements and environmental defenders demand food sovereignty and agroecology against agribusiness, pesticides, corporate crimes, and ecocide of the commons.",
        "fr": "Les mouvements paysans et les défenseurs de l'environnement exigent la souveraineté alimentaire et l'agroécologie contre l'agro-industrie, les pesticides, les crimes d'entreprise et l'écocide des biens communs.",
        "de": "Bäuerliche Bewegungen und Umweltverteidiger fordern Ernährungssouveränität und Agrarökologie gegen Agrarindustrie, Pestizide, Unternehmensverbrechen und den Ökozid an den Gemeingüter.",
    },
]


def build_quadrilingual_system_prompt(session_title: str = "", speakers: str = "") -> str:
    table_lines = "\n".join(f"- TR: {tr} | EN: {en} | FR: {fr} | DE: {de}" for tr, en, fr, de in QUADRILINGUAL_TERMS)
    forbidden_lines = "\n".join(f"- Türkçe çeviride ASLA '{bad}' deme -> mutlaka '{good}' kullan" for bad, good in FORBIDDEN_TR)
    return (
        "Sen COP31 Uluslararası İklim Adaleti Forumu (iklimadaleti.org) ve Çevre Hukuku Ağı (cevrehukuku.org) "
        "için Antalya Barosu'nda görev yapan 4 dilli (Türkçe <-> İngilizce <-> Fransızca <-> Almanca) simultane tercümansın.\n"
        f"Aktif Oturum: {session_title}\n"
        f"Konuşmacılar: {speakers}\n\n"
        "GÖREVİN:\n"
        "Sana gelen konuşma metni TÜRKÇE, İNGİLİZCE, FRANSIZCA veya ALMANCA olabilir.\n"
        "Metni aynı anda her 4 dile (tr, en, fr, de) çevirerek SADECE geçerli bir JSON nesnesi döndür:\n"
        '{"tr": "Türkçe metin", "en": "English text", "fr": "Texte français", "de": "Deutscher Text"}\n\n'
        "YASAKLI TÜRKÇE İFADELER:\n"
        f"{forbidden_lines}\n\n"
        "4 DİLLİ ZORUNLU TERMİNOLOJİ TABLOSU (TR | EN | FR | DE):\n"
        f"{table_lines}"
    )
