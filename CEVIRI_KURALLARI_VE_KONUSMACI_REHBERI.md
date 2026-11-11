# COP31 Uluslararası İklim Adaleti Forumu (15–17 Kasım 2026, Antalya Barosu)
## Yapay Zeka Simultane Çeviri Sistemine Eklenen Kurallar, Konuşmacı Brifingleri ve Terminoloji Düzeni

Bu belge, **`https://ceviri.iklimadaleti.org`** adresinde çalışan 4 kanallı (`TR ↔ EN ↔ FR ↔ DE`) canlı çeviri ve altyazı sistemine ([`glossary.py`](file:///d:/yeni%20uygulama/simultane_/glossary.py) ve [`static/operator.html`](file:///d:/yeni%20uygulama/simultane_/static/operator.html)) entegre edilen tüm kuralların, yasaklı çevirilerin ve konuşmacı özel brifinglerinin tam listesidir.

---

## 1. Sistem Genel Mimari ve Güvenlik Kuralları

1. **Çift Yönlü 4 Kanal Çeviri (`TR ↔ EN ↔ FR ↔ DE`):** Kürsüdeki konuşmacı veya soru-cevap kısmındaki dinleyici Türkçe, İngilizce, Fransızca veya Almanca konuştuğunda sistem aynı anda 4 dilde altyazı (`/ekran`) ve kulaklık sesi (`/dinle`) üretir.
2. **Çift Motorlu Yedekli Çeviri (Failover):**
   - **Birincil Motor:** Claude Sonnet (`claude-sonnet-4-5` / `5-5`)
   - **Otomatik Yedek Motor:** Gemini 2.5 Flash (Birincil motorda gecikme veya kesinti olursa milisaniyeler içinde devreye girer).
3. **Canlı Ses Tanıma (STT) Özel Kelime Koruması (Deepgram Nova-2):**
   - Konuşmacı soyadları, mahkeme kısaltmaları ve teknik terimler (`Prieur`, `CIDCE`, `Vassallo`, `Brouwer`, `Mekouar`, `Bastin`, `Limoges`, `Montpellier`, `Schrijer`, `Policastro`, `Szczecin`, `Vernadsky`, `Noosphere`, `Biosphere`, `Bundesverfassungsgericht`, `Grundgesetz`, `Klimabeschluss`, `KlimaSeniorinnen`, `Aarhus`, `Escazu`, `ITLOS`, `CEDH`, `CIJ`, `TIDM`, `CJUE`, `PNUE`, `MARPOL`, `MEPC`, `CNUDM`, `UNCLOS`, `EEXI`, `SEEMP`, `FuelEU`, `REMPEC`, `CDMO`, `Minamata`, `Gaillard`, `Fromageau`, `Armandoni`, `UNOC`, `Belem`, `Mutirao`, `Caatinga`, `TFFF`, `NCQG`, `CCNUCC`, `UNFCCC`, `Wissen`, `COP30`, `COP31`) ses tanıma motoruna yüksek ağırlıkla (`:2`) tanımlanmıştır.
4. **Operatör Güvenliği ve Kayıt:**
   - **Operatör PIN (`1092`):** PIN girilmeden mikrofon açılamaz, ayar değiştirilemez ve tutanak indirilemez (IP bazlı brute-force korumalı).
   - **Oturum Ses ve Tutanak Kaydı:** Canlı yayın başladığında salon sesi `.webm` olarak, 4 dilli çeviriler ise zaman damgalı `.txt` tutanağı olarak kaydedilir.

---

## 2. Kesinlikle Yasaklanan Hatalı Türkçe Çeviriler (`FORBIDDEN_TR` — 26 Kural)

Yapay zekanın kelimesi kelimesine (literal) çeviri yaparken düşebileceği aşağıdaki **26 hata** sistem tarafından kesin olarak yasaklanmıştır:

| ❌ Yasaklı / Hatalı Çeviri | ✅ Zorunlu Doğru Karşılık |
| :--- | :--- |
| *yeşil yıkama* | **yeşil aklama** (*greenwashing*) |
| *doğanın finansmanı* | **doğanın finansallaşması** (*financialisation of nature*) |
| *gıdanın finansmanı* | **gıdanın finansallaşması** (*financialisation of food*) |
| *toprağın finansmanı* | **toprağın finansallaşması** (*financialisation of land*) |
| *sahte sermaye / kurgusal sermaye* | **hayali sermaye (fiktif sermaye)** (*fictitious capital*) |
| *arazi kapma* | **toprak gaspı (arazi gaspı)** (*land grabbing*) |
| *tarım ilacı / zirai ilaç / bitki sağlığı ürünleri* | **tarım zehri (pestisit) / tarım zehirleri (pestisitler)** |
| *avam kamarası / ortak mallar / ortaklar* | **müşterekler** (*the commons / biens communs*) |
| *gıda hakimiyeti / yemek egemenliği / besin egemenliği* | **gıda egemenliği** (*food sovereignty*) |
| *regresyon olmama / gerilememe ilkesi* | **çevre hukukunda geriye gidiş yasağı ilkesi** (*principle of non-regression*) |
| *çevreciler* | **yaşam savunucuları / çevre savunucuları** (*environmental defenders*) |
| *ekolojik cinayet* | **ekokırım** (*ecocide*) |
| *evrensel suç* | **evrensel zarar** (*universal harm / danno universale*) |
| *hukuki itaat* | **hukuki nitelendirme / norm kapsamına alma** (*legal subsumption*) |
| *hukuki endeksler* | **hukuki göstergeler** (*legal indicators / indicateurs juridiques*) |
| *savunmasız gruplar* | **kırılgan gruplar** (*vulnerable groups*) |
| *hassas alanlar* | **kırılgan alanlar** (*vulnerable areas*) |

---

## 3. Yedi Yabancı Konuşmacı İçin Eklenen Özel Hazırlık Kuralları (`SPEAKER_BRIEFS`)

### Konuşmacı 1: Dr. Jenny Simon & Prof. Dr. Markus Wissen (HWR Berlin)
* **Oturum:** 16 Kasım 2026, 10.30 – 12.00 (I. Oturum — Konuşma Dili: İngilizce)
* **Başlık:** *Kapitalist Kriz Çağında Doğanın Metalaştırılması, Büyüme ve Sermaye Birikimi*
* **Zorunlu Çeviri Kuralları:**
  1. `Financialisation` → ASLA *"finansman"* veya *"fon sağlama"* diye çevrilmez; mutlaka **finansallaşma** olarak çevrilir.
  2. `Fictitious capital` → **hayali sermaye (fiktif sermaye)**.
  3. `Land grabbing` → **toprak gaspı (arazi gaspı)**.
  4. `Imperial mode of living` → **emperyal yaşam tarzı**.
  5. `Green hydrogen` → **yeşil hidrojen**, `industrial decarbonisation` → **endüstriyel karbonsuzlaşma**, `externalisation of environmental costs` → **çevresel maliyetlerin dışsallaştırılması**.
  6. `Konzentration im Kommando über Kapital` → **sermaye üzerindeki kumandanın yoğunlaşması**.

---

### Konuşmacı 2: Prof. Dr. Michel Prieur (CIDCE Başkanı, Limoges Üniversitesi)
* **Oturum:** 17 Kasım 2026, 10.30 – 12.30 (I. Oturum — Konuşma Dili: Fransızca / İngilizce)
* **Başlık:** *İklim ve Çevre Hukukunda Hâkimlerin ve Avukatların Rolü: Adalet, İklim ve İnsan Hakları*
* **Zorunlu Çeviri Kuralları:**
  1. **Doğrudan Fransızca → Türkçe Hukuki Çeviri:** Konuşmacı Fransızca konuştuğunda İngilizce ara çeviri yapmadan doğrudan Fransız kamu hukuku kavramlarından Türkçeye çevrilir.
  2. **`Effectivité` ≠ `Efficacité` ≠ `Efficience` Ayrımı:**
     - `Effectivité du droit / Effectivity of law` → **hukukun fiilî işlerliği (hukuk kurallarının fiilen uygulanması)** (ASLA sıradan *"etkinlik"* denmez).
     - `Efficacité / Effectiveness` → **etkililik (amaçlanan sonuca ulaşma derecesi)**.
     - `Efficience / Efficiency` → **verimlilik (kaynak-sonuç oranı)**.
  3. **`Non-régression` ≠ `Non-rétroactivité` Ayrımı:**
     - `Principe de non-régression` → **çevre hukukunda geriye gidiş yasağı ilkesi** (*acquis environnementaux* → **çevre hukukunda kazanılmış koruma düzeyi**).
     - `Principe de non-rétroactivité` → **geriye yürümezlik ilkesi** (kanunların geçmişe etkili olmaması).
  4. **Usul Hukuku ve Yargı Ayrımları:**
     - `Accès à la justice` (**adalete erişim**), `Accès au juge` (**hâkime / yargı merciine erişim**), `Accès au tribunal` (**mahkemeye erişim hakkı**).
     - `Qualité pour agir / Legal standing` (**dava açma ehliyeti / yetkisi**) vs `Intérêt à agir` (**dava açmada menfaat**) vs `Recevabilité / Irrecevabilité` (**kabul edilebilirlik / kabul edilemezlik**).
     - `Jurisprudence` (**içtihat**) vs `Doctrine juridique` (**hukuk öğretisi / doktrin**).
     - `Arrêt / Jugement contentieux` (**çekişmeli yargı kararı**) vs `Avis consultatif` (**danışma görüşü**).
  5. **Uluslararası İklim İçtihatları (2024–2025):**
     - **AİHM (CEDH / ECtHR) Büyük Daire — *Verein KlimaSeniorinnen Schweiz ve Diğerleri / İsviçre* (9 Nisan 2024):** Derneğin dava açma ehliyeti (*qualité pour agir*) kabul edilmiş, bireysel başvurular kabul edilemez (*irrecevables*) bulunmuştur.
     - **BMDHGM (TIDM / ITLOS) Danışma Görüşü (21 Mayıs 2024)**, **Amerikalılar Arası İnsan Hakları Mahkemesi OC-32/25 Danışma Görüşü (2025)** ve **UAD (CIJ / ICJ) İklim Değişikliği Danışma Görüşü (23 Temmuz 2025)**.

---

### Konuşmacı 3: Dr. Julien Prieur (CIDCE, Limoges Üniversitesi)
* **Oturum:** 17 Kasım 2026, 10.30 – 12.30 (I. Oturum — Konuşma Dili: Fransızca / İngilizce)
* **Başlık:** *2026 Antalya COP31 Perspektifinden İklim Adaleti Açısından COP30 (Belém) Değerlendirmesi*
* **Zorunlu Çeviri Kuralları:**
  1. **COP30 (10–22 Kasım 2025, Belém, Brezilya) Kararları:**
     - `Belém Political Package / Paquet politique de Belém` → **Belém Siyasi Paketi**.
     - `Global Mutirão Decision` → **Küresel Mutirão Kararı (Kolektif Seferberlik Kararı)**.
  2. **1,3 Trilyon Dolarlık Bakü–Belém Yol Haritası (`Baku to Belém Roadmap to 1.3T`):**
     - Fransızca `1 300 milliards` = İngilizce `1.3 trillion` = **1,3 trilyon dolar**.
     - Bu tutar bir finansman seferberliği hedefidir; ASLA *"hâlihazırda ödenmiş / kasaya girmiş para"* gibi çevrilmez.
  3. **`Indicateurs d'adaptation` ≠ `Indicateurs juridiques` Ayrımı:**
     - COP30'da kabul edilen **59 Belém Uyum Göstergesi** (*adaptation indicators* — gönüllü ve cezai olmayan nitelikte) ile CIDCE'nin **hukuki göstergeleri** (*legal indicators / indicateurs juridiques*) birbirine karıştırılmaz.
  4. **Fosil Yakıt Terminolojisi (3 Farklı Hukuki Derece):**
     - `Sortie progressive / Phase-out` → **fosil yakıtların aşamalı olarak tamamen terk edilmesi**.
     - `Réduction progressive / Phase-down` → **fosil yakıt kullanımının aşamalı olarak azaltılması**.
     - `Transition hors des combustibles fossiles / Transitioning away` → **fosil yakıtlardan uzaklaşma / geçiş**.
  5. **Özel Kavramlar:** `Tropical Forest Forever Facility (TFFF)` → **Tropikal Ormanları Kalıcı Olarak Koruma Finansman Mekanizması (TFFF)**, `Caatinga` → **Caatinga ekosistemi (Brezilya)**, `fonction socio-environnementale de la propriété` → **mülkiyetin sosyo-ekolojik işlevi**.

---

### Konuşmacı 4: Dr. Laurent Vassallo (CIDCE Saymanı, Montpellier Üniversitesi)
* **Oturum:** 17 Kasım 2026, 10.30 – 12.30 (I. Oturum — Konuşma Dili: Fransızca / İngilizce)
* **Başlık:** *Çevre Hukukunun Fiilî İşlerliğini Ölçmeye Yönelik Hukuki Göstergeler: İklim Eylemi İçin*
* **Zorunlu Çeviri Kuralları:**
  1. **CIDCE Hukuki Fiilî İşlerlik Ölçümünün 6 Yapısal Sorusu:**
     - (1) *Existence* (**hukuk kuralının varlığı**), (2) *Applicabilité / Applicability* (**uygulanabilirlik**) vs *Caractère exécutoire / Enforceability* (**hukuken icra edilebilirlik**), (3) *Cadre institutionnel* (**kurumsal çerçeve ve yetkili makam** — *autorité compétente*), (4) *Contenu normatif* (**normatif içerik**), (5) *Application effective / Enforcement* (**fiilî uygulama ve yaptırım**), (6) *Facteurs extrajuridiques* (**hukuk dışı — siyasi, ekonomik, sosyal, kültürel — engeller**).
  2. **Gösterge Türlerinin Ayrımı:**
     - `Indicateurs juridiques / Legal indicators` (**hukuki göstergeler**) ile `indicateurs environnementaux / écologiques` (**çevresel/ekolojik göstergeler**) karıştırılmaz. Emisyonların düşmesi çevresel bir sonuçtur; tek başına hukuk kuralının fiilî işlerliğini ölçmez.
  3. **Metodolojik ve İstatistiksel Terimler:**
     - `Indicateur / Indicator` (**gösterge**) ≠ `Indice / Index` (**endeks** — her göstergeye *"endeks"* denmez!).
     - `Référentiel / Reference framework` (**referans çerçevesi**), `Qualification des données` (**verilerin nitelendirilmesi**), `Quantification des données` (**verilerin nicelleştirilmesi**), `Agrégation des données` (**verilerin birleştirilmesi / toplulaştırılması**), `Pondération / Weighting` (**ağırlıklandırma**), `Système de notation / Scoring system` (**puanlama sistemi**), `Questionnaire juridique` (**hukuki soru formu / anket**), `Panel d'experts` (**uzman paneli**), `Tableau de bord / Dashboard` (**gösterge paneli**), `Diagramme radar` (**radar grafiği**).
  4. **Nedensellik ve Boşluk Ayrımları:**
     - `Corrélation / Correlation` (**korelasyon / ilişki**) ≠ `Causalité / Causation` (**nedensellik**).
     - `Lacune de mise en œuvre / Implementation gap` (**uygulama açığı**) ≠ `Lacune juridique / Legal gap` (**hukuki boşluk**).
     - **Saha Çalışmaları:** **UNOC 2025** (SKA 14 / ODD 14 kapsamında 9 ülke değerlendirmesi), **Cıvaya İlişkin Minamata Sözleşmesi** (*Minamata Convention on Mercury*), **sağlık kuruluşlarında sürdürülebilir kalkınma hukuku** (*établissements de santé*).

---

### Konuşmacı 5: Lucie Brouwer (CIDCE, CDMO Nantes Üniversitesi, SKEMA Business School)
* **Oturum:** 17 Kasım 2026, 10.30 – 12.30 (I. Oturum — Konuşma Dili: İngilizce / Fransızca)
* **Başlık:** *Devletlerin İklim Yükümlülüklerinin Fiilî İşlerliğini Değerlendirmeye Yönelik Hukuki Göstergeler: Deniz Taşımacılığı ve İklim Adaleti Sorunları*
* **Zorunlu Çeviri Kuralları:**
  1. **`Legal Indicators` ≠ `Carbon Intensity Indicator (CII)` Ayrımı:**
     - CIDCE'nin **hukuki göstergeleri** (*legal indicators / indicateurs juridiques*) ile Uluslararası Denizcilik Örgütü'nün (IMO/OMI) teknik göstergesi olan **Karbon Yoğunluğu Göstergesi (CII)** birbirine karıştırılmaz.
  2. **`Maritime Law` ≠ `Law of the Sea` Ayrımı:**
     - `Maritime law / Droit maritime` → **deniz ticaret hukuku / denizcilik hukuku**.
     - `Law of the sea / Droit de la mer` → **uluslararası deniz hukuku** (UNCLOS / CNUDM / BMDHS md. 192, 194, 206).
  3. **Devlet ve Denizcilik Aktörleri Ayrımları:**
     - `Flag State / État du pavillon` (**bayrak devleti**), `Port State / État du port` (**liman devleti**), `Coastal State / État côtier` (**kıyı devleti**).
     - `Shipowner / Armateur` (**donatan / gemi sahibi**), `Ship operator / Exploitant du navire` (**gemi işletmecisi**), `Charterer / Affréteur` (**çarterer / gemi kiralayan**).
  4. **Denizcilik Emisyon Zinciri ve Ölçümleri:**
     - `Well-to-wake emissions` → **yakıtın üretiminden gemide kullanımına kadar oluşan yaşam döngüsü emisyonları**.
     - `Tank-to-wake emissions` → **yakıtın gemide kullanımından kaynaklanan emisyonlar**.
     - `Gross tonnage / Jauge brute` (**gros tonaj — geminin iç hacim ölçüsü**) ≠ `Cargo weight` (**yük ağırlığı**).
  5. **IMO Net-Zero Framework ve AB Düzenlemeleri:**
     - **IMO Net Sıfır Çerçevesi (*IMO Net-Zero Framework*):** Nisan 2025'te **MEPC 83**'te onaylandı (*approved / approuvé*), ancak Ekim 2025'te kabul edilmedi (*not adopted*) ve Kasım 2026 itibarıyla henüz yürürlüğe girmedi (*not yet in force*). `Approval` (**onaylama**), `adoption` (**kabul edilme**) ve `entry into force` (**yürürlüğe girme**) aşamaları karıştırılmaz.
     - **Teknik ve Bölgesel Araçlar:** **MARPOL Ek VI**, **EEXI**, **SEEMP**, **IMO DCS**, **EU MRV**, **EU ETS / SEQE-UE** (2024 %40, 2025 %70, 2026 %100), **FuelEU Maritime** (1 Ocak 2025), **Barselona Sözleşmesi 2002 Önleme ve Acil Durum Protokolü** (*25 madde için 117 hukuki gösterge*, **REMPEC**).

---

### Konuşmacı 6: Prof. Dr. Pasquale Policastro (Szczecin Üniversitesi)
* **Oturum:** 17 Kasım 2026, 13.30 – 15.30 (II. Oturum — Konuşma Dili: İngilizce)
* **Başlık:** *Biyosferik İlişkiler ve Hukuk Devleti (Biospheric Relations and the Rule of Law)*
* **Zorunlu Çeviri Kuralları:**
  1. **`Biosphere` ≠ `Environment` ve `Rights of the Biosphere` ≠ `Rights of Nature` Ayrımı:**
     - `Biosphere / Biosfera` → **biyosfer** (ASLA sıradan *"çevre"* diye çevrilmez; Vladimir Vernadsky'nin **Biyosfer** ve **Noosfer** kavramlarına dayanır).
     - `Rights of the Biosphere / Diritti della Biosfera` (**biyosferin hakları**) ile `Rights of Nature / Diritti della Natura` (**doğanın hakları**) analitik olarak iki farklı kavramdır; eşanlamlı çevrilmez.
  2. **Anayasal Kavramlar:**
     - `Biospheric constitutionalism` → **biyosferik anayasacılık**.
     - `Constitutionalism` (**anayasacılık**) ≠ `Constitution` (**anayasa**) ≠ `Constitutional law` (**anayasa hukuku**).
     - `Rule of law / Stato di diritto / Państwo prawa` (**hukuk devleti ilkesi / hukukun üstünlüğü**) ≠ `Rule by law` (**hukuk aracılığıyla yönetim**).
  3. **`Legal Subsumption` ve Bilimsel Düzenlilikler:**
     - `Biospheric regularities / Regolarità della Biosfera` → **biyosferin işleyiş düzenlilikleri** (doğadaki bilimsel olgular ile hukuki normlar birbirine karıştırılmaz).
     - `Legal subsumption / Sussunzione giuridica` → **hukuki nitelendirme / hukuk normu kapsamına alma** (ASLA *"hukuki itaat"* veya *"tabi kılma"* diye çevrilmez!).
  4. **Ormanların Anayasal Hukuki Kişiliği ve Evrensel Zarar:**
     - `Constitutional legal personality of forests` → **ormanların anayasal düzeyde hukuki kişiliği** (doktriner öneri olarak korunur; `legal personality` [**hukuki kişilik**], `legal subjectivity` [**hukuk öznesi olma niteliği**] ve `legal standing` [**dava açma ehliyeti**] ayrımları korunur).
     - `Universal harm / Danno universale` → **evrensel zarar** (ASLA *"evrensel suç"* veya *"insanlığa karşı suç"* diye çevrilmez).
     - `Symbiosis` (**simbiyoz / ortakyaşam**) ≠ `Coexistence` (**bir arada var olma**); `Climate migrant` (**iklim göçmeni**) ≠ `Refugee` (**mülteci**).

---

### Konuşmacı 7: Dr. Markus Johannes Theodorus Schrijer (Humboldt Üniversitesi Berlin / Akdeniz Üniv.)
* **Oturum:** 17 Kasım 2026, 13.30 – 15.30 (II. Oturum — Konuşma Dili: İngilizce)
* **Başlık:** *Temsil Olmadan Dağıtım Olmaz: Alman İklim Kararında Zamanlar Arası Özgürlük ve Eşitlik Sorunu*
* **Zorunlu Çeviri Kuralları:**
  1. **Alman Federal Anayasa Mahkemesi (`Bundesverfassungsgericht / BVerfG`) 24 Mart 2021 İklim Kararı (`Klimabeschluss`):**
     - `Bundes-Klimaschutzgesetz (KSG)` → **Alman Federal İklim Koruma Kanunu**.
  2. **`Intertemporal` ≠ `Intergenerational` ve `Freedom` ≠ `Equality` Ayrımı:**
     - `Intertemporal freedom / Intertemporale Freiheit` → **zamanlar arası özgürlük**.
     - `Intergenerational freedom` → **kuşaklar arası özgürlük**.
     - `Intergenerational equality` → **kuşaklar arası eşitlik**.
     - `Intertemporale Freiheitssicherung / Intertemporal safeguarding of freedom` → **zamanlar arası özgürlük güvencesi**.
     - `Eingriffsähnliche Vorwirkung / Advance interference-like effect` → **temel haklara müdahaleye benzer ön etki**.
  3. **`Distribution` ≠ `Redistribution` ve Karbon Bütçesi:**
     - `Distribution` → **dağılım / dağıtım (yüklerin ve özgürlük olanaklarının dağılımı)** vs `Redistribution` → **yeniden dağıtım** (ikisi de *"gelir dağılımı"* diye çevrilmez).
     - `Minderungslast / Reduction burden` → **emisyon azaltım yükü**, `Lastenverteilung` → **yüklerin dağılımı**.
     - `CO₂-Restbudget / Remaining carbon budget` → **kalan karbon bütçesi** (mali bütçe değil, atmosferik emisyon bütçesidir).
  4. **Demokratik Temsil, Kurucu İktidar ve Ölçülülük Testi:**
     - `Political representation` (**siyasal/demokratik temsil**) ≠ `Political participation` (**siyasal katılım**) ≠ `Legal representation` (**hukuki/avukatla temsil**).
     - `Constituent power / Verfassungsgebende Gewalt` (**kurucu iktidar**) ≠ `Constituted power / Verfasste Gewalt` (**kurulu iktidar**).
     - `Formal legality` (**biçimsel hukuka uygunluk**) ≠ `Democratic / Substantive legitimacy` (**demokratik / maddi meşruiyet**).
     - **3 Aşamalı Ölçülülük Testi (`Proportionality / Verhältnismäßigkeit`):** (1) `Suitability / Geeignetheit` (**elverişlilik**), (2) `Necessity / Erforderlichkeit` (**gereklilik**), (3) `Proportionality in the strict sense / Angemessenheit` (**dar anlamda ölçülülük / orantılılık**, `Abwägung` → **dengeleme**).
  5. **Alman Temel Yasası (`Grundgesetz / GG`) Maddeleri ve Karar Türleri:**
     - `Article 20a GG` (`Staatszielbestimmung`) → **Alman Temel Yasası md. 20a — devlet hedefini düzenleyen anayasal hüküm** (`natürliche Lebensgrundlagen` → **yaşamın doğal temelleri**; doğrudan sübjektif temel hak değil, yargısal denetime tabi anayasal devlet ödevidir).
     - `Unvereinbarkeitserklärung / Declaration of incompatibility` (**anayasayla bağdaşmazlık kararı**) ≠ `Nichtigerklärung / Declaration of nullity` (**hükümsüzlük / iptal kararı**).
