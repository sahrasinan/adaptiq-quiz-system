"""
app.py — AdaptIQ Uyarlanabilir Sınav Sistemi için Streamlit giriş noktası.

Çalıştırmak için:  streamlit run app.py
"""

from __future__ import annotations
import time
import streamlit as st

from models import AdaptiveEngine, QuizSession
from storage import DataHandler

# ──────────────────────────────────────────────────────────────────────────
# Sayfa yapılandırması (ilk Streamlit çağrısı olmalı)
# ──────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AdaptIQ — Uyarlanabilir Sınav",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────
# Özel CSS
# ──────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ════════════════════════════════════════════════════════════════
   RENK PALETI — Kahve / Krem / Amber (Acik Tema)
   ════════════════════════════════════════════════════════════════ */
:root {
  --bg:          #FBF3E7;   /* krem zemin */
  --surface:     #FFFDF9;   /* kart yuzeyi - off-white */
  --surface2:    #F0E2CC;   /* ikincil yuzey - acik krem/bej */
  --border:      #E0C9A6;   /* yumusak kahve kenar cizgisi */
  --accent:      #C1531B;   /* sicak turuncu/amber - ana vurgu */
  --accent2:     #8C5A2B;   /* kahve - ikincil vurgu */
  --success:     #2F7D32;   /* koyu yesil (krem uzerinde okunakli) */
  --danger:      #B3261E;   /* koyu kirmizi (krem uzerinde okunakli) */
  --warn:        #B45309;   /* amber/kahve uyari rengi */
  --text:        #000000;   /* TUM metin siyah - tam okunabilirlik */
  --text-muted:  #5C4631;   /* ikincil metin - koyu kahve (gri degil) */
  --radius:      12px;
  --shadow:      0 2px 8px rgba(139,90,43,0.12);
}

/* ── Genel zemin ve govde metni ──────────────────────────────────
   Not: Streamlit'in dahili koyu tema algilamasini gecersiz kilmak
   icin renkler 'var()' yerine de tekrar sabit deger olarak yazilir. */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background-color: #FBF3E7 !important;
  color: #000000 !important;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Streamlit'in govde/blok kapsayicilari da zemin rengini almali */
[data-testid="stMain"],
[data-testid="block-container"],
.main .block-container {
  background-color: #FBF3E7 !important;
}

/* ── TUM metin elemanlari icin siyah renk garantisi ──────────────
   Bu blok, Streamlit'in kendi varsayilan stillerinin (p, span, label,
   markdown, caption vb.) eski mavi/karanlik temadan kalan renkleri
   gecersiz kilmasini saglar. */
p, span, label, li, div,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stText"],
[data-testid="stCaptionContainer"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
h1, h2, h3, h4, h5, h6 {
  color: #000000 !important;
}

/* st.caption() varsayilan olarak soluk gri kullanir; okunabilirlik
   icin koyu kahveye ceviriyoruz (siyahtan biraz daha yumusak). */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
  color: #5C4631 !important;
}

/* ── Kartlar ──────────────────────────────────────────────────── */
.iq-card {
  background: #FFFDF9;
  border: 1px solid #E0C9A6;
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow);
  color: #000000;
}
.iq-card * { color: #000000; }
.iq-card-accent {
  border-left: 5px solid #C1531B;
}

/* ── Hero banner ──────────────────────────────────────────────── */
.iq-hero {
  background: linear-gradient(135deg, #F7E6CC 0%, #F0D6AE 100%);
  border: 1px solid #E0C9A6;
  border-radius: 16px;
  padding: 2.5rem 2rem 2rem;
  text-align: center;
  margin-bottom: 2rem;
  box-shadow: var(--shadow);
}
.iq-logo { font-size: 3.2rem; line-height: 1; }
.iq-title {
  font-size: 2.4rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  background: linear-gradient(90deg, #C1531B, #8C5A2B);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0.3rem 0 0.2rem;
}
.iq-subtitle { color: #5C4631 !important; font-size: 1rem; }

/* ── Ilerleme cubugu ──────────────────────────────────────────── */
.iq-progress-wrap {
  background: #F0E2CC;
  border: 1px solid #E0C9A6;
  border-radius: 99px;
  height: 10px;
  overflow: hidden;
  margin: 0.6rem 0 1.2rem;
}
.iq-progress-fill {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, #C1531B, #E08938);
  transition: width 0.4s ease;
}

/* ── Soru karti ───────────────────────────────────────────────── */
.iq-question-text {
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.6;
  color: #000000 !important;
}
.iq-topic-badge {
  display: inline-block;
  background: #F7E6CC;
  color: #8C5A2B !important;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 99px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 0.8rem;
  border: 1px solid #E0C9A6;
}
.iq-diff-badge {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 99px;
  margin-left: 0.4rem;
}
.iq-diff-1 { background: #E3F0E1; color: #205723 !important; border: 1px solid #BEDBB8; }
.iq-diff-2 { background: #FBE8CF; color: #8A4A0E !important; border: 1px solid #F0CB94; }
.iq-diff-3 { background: #F6DAD6; color: #8C231C !important; border: 1px solid #ECB5AC; }

/* ── Cevap geri bildirimi ─────────────────────────────────────── */
.iq-feedback-correct {
  background: #E9F4E7;
  border: 1.5px solid #9CCB95;
  border-radius: var(--radius);
  padding: 0.9rem 1.1rem;
  color: #1E4D20 !important;
  font-weight: 700;
}
.iq-feedback-correct * { color: #1E4D20 !important; }
.iq-feedback-wrong {
  background: #FBE7E4;
  border: 1.5px solid #E3A39B;
  border-radius: var(--radius);
  padding: 0.9rem 1.1rem;
  color: #8C231C !important;
  font-weight: 700;
}
.iq-feedback-wrong * { color: #8C231C !important; }
.iq-feedback-wrong b { color: #6B1A14 !important; }
.iq-explanation {
  color: #3D2E1F !important;
  font-size: 0.93rem;
  font-weight: 500;
  margin-top: 0.5rem;
}

/* ── Metrik kutucuklari ───────────────────────────────────────── */
.iq-metric-row {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}
.iq-metric {
  flex: 1;
  min-width: 100px;
  background: #FFFDF9;
  border: 1px solid #E0C9A6;
  border-radius: var(--radius);
  padding: 0.9rem 1rem;
  text-align: center;
  box-shadow: var(--shadow);
}
.iq-metric-value { font-size: 1.9rem; font-weight: 800; line-height: 1; }
.iq-metric-label {
  font-size: 0.75rem;
  color: #5C4631 !important;
  margin-top: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

/* ── Not harfi ────────────────────────────────────────────────── */
.iq-grade {
  font-size: 5rem;
  font-weight: 900;
  text-align: center;
  line-height: 1;
  margin: 0.5rem 0;
}

/* ── Kenar cubugu (sidebar) ───────────────────────────────────── */
[data-testid="stSidebar"] {
  background-color: #F0E2CC !important;
  border-right: 1px solid #E0C9A6;
}
[data-testid="stSidebar"] * {
  color: #000000 !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
  color: #5C4631 !important;
}

/* ── Streamlit buton gecersiz kilmalari ───────────────────────── */
div.stButton > button {
  background: linear-gradient(135deg, #C1531B, #9C4416);
  color: #FFFFFF !important;
  border: none;
  border-radius: var(--radius);
  font-weight: 700;
  padding: 0.6rem 1.4rem;
  width: 100%;
  transition: opacity .2s, box-shadow .2s, transform .1s;
  box-shadow: 0 2px 6px rgba(193,83,27,0.30);
}
div.stButton > button p { color: #FFFFFF !important; }
div.stButton > button:hover  {
  opacity: 0.92;
  box-shadow: 0 4px 12px rgba(193,83,27,0.40);
}
div.stButton > button:active { opacity: 0.8; transform: scale(0.99); }

/* ── Radyo buton secenekleri (cevap siklari) ──────────────────── */
div[data-testid="stRadio"] label {
  background: #FFFDF9;
  border: 1px solid #E0C9A6;
  border-radius: 8px;
  padding: 0.65rem 0.95rem;
  margin: 0.25rem 0;
  cursor: pointer;
  transition: background .15s, border-color .15s;
  display: block;
}
div[data-testid="stRadio"] label * { color: #000000 !important; }
/* Radyo etiketi icindeki `code` parcalarinin acik zeminli kalmasini
   kesin olarak garantilemek icin burada da tekrar tanimliyoruz
   (CSS sira/oncelik catismalarina karsi ekstra guvence). */
div[data-testid="stRadio"] label code {
  background-color: #F0E2CC !important;
  color: #000000 !important;
  border: 1px solid #E0C9A6 !important;
}
div[data-testid="stRadio"] label:hover {
  background: #F7E6CC;
  border-color: #C1531B;
}
/* Secili radyo dugmesinin rengi */
div[data-testid="stRadio"] input[type="radio"]:checked + div {
  color: #C1531B !important;
}

/* ── Metin / Secim girdileri ──────────────────────────────────── */
[data-testid="stTextInput"] input {
  background-color: #FFFDF9 !important;
  color: #000000 !important;
  border: 1px solid #E0C9A6 !important;
  border-radius: 8px !important;
}
[data-testid="stTextInput"] input::placeholder {
  color: #8A765C !important;
}

/* ── Selectbox / Dropdown (kapali kutu) ────────────────────────
   st.selectbox, secili deger gosterilen ana kutu */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  background-color: #FFFDF9 !important;
  color: #000000 !important;
  border: 1px solid #E0C9A6 !important;
  border-radius: 8px !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div * {
  color: #000000 !important;
}
/* Secili deger metni (bazi Streamlit surumlerinde ayri span/div) */
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] div {
  color: #000000 !important;
}
/* Dropdown ok ikonu da gorunur olsun */
[data-testid="stSelectbox"] svg {
  fill: #000000 !important;
}

/* ── Selectbox / Dropdown (acilan liste — BaseWeb popover) ──────
   BaseWeb, acilir listeyi genelde bir portal icinde dokumana ayri
   olarak ekler (sayfanin govdesine en yakin seviyede), bu nedenle
   bu kurallar [data-testid="stSelectbox"] kapsayicisinin DISINDA,
   global olarak tanimlanir. Streamlit'in koyu tema sinifi/degiskeni
   buraya sizdigi icin her seviyede !important ile zorla eziyoruz. */
div[data-baseweb="popover"],
div[data-baseweb="popover"] div,
ul[role="listbox"],
ul[data-testid="stSelectboxVirtualDropdown"] {
  background-color: #FFFDF9 !important;
  color: #000000 !important;
  border: 1px solid #E0C9A6 !important;
}
/* Tek tek liste ogeleri (her secenek satiri) */
li[role="option"],
ul[role="listbox"] li,
div[data-baseweb="popover"] li {
  background-color: #FFFDF9 !important;
  color: #000000 !important;
}
li[role="option"] *,
ul[role="listbox"] li *,
div[data-baseweb="popover"] li * {
  color: #000000 !important;
}
/* Uzerine gelinen / klavye ile secili olan secenek */
li[role="option"]:hover,
li[aria-selected="true"],
ul[role="listbox"] li:hover {
  background-color: #F7E6CC !important;
  color: #000000 !important;
}
/* Streamlit'in BaseWeb tema saglayicisi data-baseweb="select"
   icindeki her olasi alt katmani da kapsayalim */
[data-baseweb="select"] * ,
[data-baseweb="menu"] * ,
[data-baseweb="popover"] * {
  color: #000000 !important;
}
[data-baseweb="menu"] {
  background-color: #FFFDF9 !important;
}

/* ── Satir-ici kod blocklari (`code`) ─────────────────────────────
   Radyo secenekleri, markdown ve aciklama metinlerindeki ` ` ile
   sarili kod parcalari. Streamlit varsayilan olarak koyu/siyah
   zemin + acik metin kullanir; burada acik zemin + siyah metne
   ceviriyoruz. */
code,
pre code,
span[data-testid="stMarkdownContainer"] code,
[data-testid="stMarkdownContainer"] code,
[data-testid="stMarkdownContainer"] pre code,
div[data-testid="stRadio"] code,
p code {
  background-color: #F0E2CC !important;
  color: #000000 !important;
  border: 1px solid #E0C9A6 !important;
  border-radius: 4px !important;
  padding: 0.15rem 0.4rem !important;
  font-weight: 600;
}
/* Coklu satirli kod bloklari (```...```) icin de ayni acik zemin */
pre {
  background-color: #F0E2CC !important;
  border: 1px solid #E0C9A6 !important;
  border-radius: 8px !important;
}
pre, pre * {
  color: #000000 !important;
}

/* st.slider sayisal etiketleri ve track rengi */
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
  color: #000000 !important;
}

/* ── Genisletilebilir bolumler (st.expander) ──────────────────── */
[data-testid="stExpander"] {
  background-color: #FFFDF9 !important;
  border: 1px solid #E0C9A6 !important;
  border-radius: var(--radius) !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] p {
  color: #000000 !important;
}
/* Expander icindeki kod bloklarinin da acik zeminli olmasi icin */
[data-testid="stExpander"] code {
  background-color: #F0E2CC !important;
  color: #000000 !important;
}

/* ── Bilgi / uyari / hata / basari kutulari (st.info, st.error...) */
[data-testid="stAlert"] {
  border-radius: var(--radius) !important;
}
[data-testid="stAlert"] p {
  color: #000000 !important;
  font-weight: 500;
}

/* ── Zamanlayici ──────────────────────────────────────────────── */
.iq-timer {
  font-size: 1.15rem;
  font-weight: 800;
  color: #8C5A2B !important;
  font-variant-numeric: tabular-nums;
}

hr { border-color: #E0C9A6 !important; }

/* ── Cizgi grafik arka plani (st.line_chart) acik tonda kalsin ── */
[data-testid="stVegaLiteChart"] { background-color: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# Yardımcı fonksiyonlar
# ──────────────────────────────────────────────────────────────────────────

def fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def grade_label(pct: float) -> tuple[str, str]:
    """Puan yüzdesine göre (harf notu, renk) döndür."""
    if pct >= 90: return "A+", "#2F7D32"
    if pct >= 80: return "A",  "#2F7D32"
    if pct >= 70: return "B",  "#8C5A2B"
    if pct >= 60: return "C",  "#B45309"
    if pct >= 50: return "D",  "#C1531B"
    return            "F",  "#B3261E"


def topic_colour(accuracy: float) -> str:
    if accuracy >= 75: return "#2F7D32"
    if accuracy >= 50: return "#B45309"
    return "#B3261E"


# ──────────────────────────────────────────────────────────────────────────
# Oturum durumu başlatma
# ──────────────────────────────────────────────────────────────────────────

def _init_state() -> None:
    defaults = {
        "page":           "anasayfa",  # anasayfa | giris | kayit | kurulum | sinav | sonuc | gecmis
        "username":       None,
        "profile":        None,
        "questions":      [],
        "engine":         None,
        "session":        None,
        "current_q":      None,
        "q_start_time":   None,
        "answered":       False,
        "chosen_index":   None,
        "quiz_length":    10,
        "topic_filter":   "Tüm Konular",
        "data_handler":   DataHandler(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()
dh: DataHandler = st.session_state["data_handler"]


# ──────────────────────────────────────────────────────────────────────────
# Kenar çubuğu
# ──────────────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### 🧠 AdaptIQ")
        st.markdown("---")

        if st.session_state["username"]:
            profile = st.session_state["profile"]
            st.markdown(f"**👤 {profile.display_name}**")
            st.caption(f"@{profile.username}")
            st.markdown(f"Sınav sayısı: **{profile.sessions_count}**")
            st.markdown(f"En yüksek puan: **{profile.best_score}%**")
            st.markdown(f"Ortalama puan: **{profile.avg_score}%**")
            st.markdown("---")

            if st.button("📊 Geçmişim"):
                st.session_state["page"] = "gecmis"
                st.rerun()
            if st.button("🚪 Çıkış Yap"):
                for key in ["username", "profile", "engine", "session",
                            "current_q", "q_start_time", "answered", "chosen_index"]:
                    st.session_state[key] = None
                st.session_state["page"] = "anasayfa"
                st.rerun()
        else:
            st.caption("Oturum açılmadı.")

        st.markdown("---")
        st.caption("AdaptIQ v1.0 · Streamlit ile geliştirildi")


# ──────────────────────────────────────────────────────────────────────────
# Sayfalar
# ──────────────────────────────────────────────────────────────────────────

# ── ANASAYFA ──────────────────────────────────────────────────────────────

def page_anasayfa() -> None:
    st.markdown("""
    <div class="iq-hero">
      <div class="iq-logo">🧠</div>
      <div class="iq-title">AdaptIQ</div>
      <div class="iq-subtitle">Hatalarından öğrenen akıllı sınav sistemi</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑  Giriş Yap", use_container_width=True):
            st.session_state["page"] = "giris"
            st.rerun()
    with col2:
        if st.button("✨  Hesap Oluştur", use_container_width=True):
            st.session_state["page"] = "kayit"
            st.rerun()

    st.markdown("---")
    st.markdown("""
    <div class="iq-card iq-card-accent">
      <b>Nasıl çalışır?</b><br>
      AdaptIQ, hangi konularda zorlandığını takip eder ve soru havuzunu
      anlık olarak o konulara doğru yönlendirir. Her yeni deneme,
      aynı soru dizisini ezberlemeni önleyen kişiselleştirilmiş
      bir pekiştirme seansına dönüşür.
    </div>
    """, unsafe_allow_html=True)


# ── GİRİŞ ─────────────────────────────────────────────────────────────────

def page_giris() -> None:
    st.markdown("## 🔑 Giriş Yap")
    users = dh.list_usernames()
    if not users:
        st.warning("Henüz kayıtlı hesap yok. Önce bir hesap oluşturun.")
        if st.button("← Geri"):
            st.session_state["page"] = "anasayfa"; st.rerun()
        return

    username = st.selectbox("Hesap seçin", users)
    if st.button("Giriş Yap"):
        try:
            profile = dh.load_profile(username)
            st.session_state.update(username=username, profile=profile, page="kurulum")
            st.rerun()
        except Exception as exc:
            st.error(f"Profil yüklenemedi: {exc}")

    if st.button("← Geri"):
        st.session_state["page"] = "anasayfa"; st.rerun()


# ── KAYIT ─────────────────────────────────────────────────────────────────

def page_kayit() -> None:
    st.markdown("## ✨ Hesap Oluştur")
    username     = st.text_input("Kullanıcı adı (boşluk içermemeli)", max_chars=30)
    display_name = st.text_input("Görünen ad", max_chars=50)

    if st.button("Oluştur"):
        if not username.strip():
            st.error("Kullanıcı adı boş olamaz.")
        elif " " in username:
            st.error("Kullanıcı adı boşluk içermemelidir.")
        elif not display_name.strip():
            st.error("Görünen ad boş olamaz.")
        else:
            try:
                profile = dh.create_profile(username.strip(), display_name.strip())
                st.session_state.update(username=username.strip(),
                                        profile=profile, page="kurulum")
                st.success("Hesap başarıyla oluşturuldu!")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    if st.button("← Geri"):
        st.session_state["page"] = "anasayfa"; st.rerun()


# ── SINAV KURULUMU ────────────────────────────────────────────────────────

def page_kurulum() -> None:
    st.markdown(f"## 👋 Merhaba, {st.session_state['profile'].display_name}!")
    st.markdown("Aşağıdan sınav ayarlarını yapılandır ve **Başlat**'a bas.")

    all_qs = dh.load_questions()
    st.session_state["questions"] = all_qs

    topics = ["Tüm Konular"] + sorted({q.topic for q in all_qs})
    col1, col2 = st.columns(2)
    with col1:
        topic = st.selectbox("Konu filtresi", topics)
    with col2:
        length = st.slider("Soru sayısı", 5, 10, 10)

    st.session_state["topic_filter"] = topic
    st.session_state["quiz_length"]  = length

    # Zayıf konu uyarısı
    profile = st.session_state["profile"]
    if profile.cumulative_weak_topics:
        weakest = sorted(
            profile.cumulative_weak_topics.items(), key=lambda x: x[1]
        )[:3]
        st.markdown("""<div class="iq-card iq-card-accent">
        <b>⚠️ Çalışman gereken konular</b> (geçmiş sınavlardan):<br>""" +
        " · ".join(f"<span style='color:#B3261E;font-weight:700'>{t}</span> ({a}%)"
                   for t, a in weakest) + "</div>", unsafe_allow_html=True)

    if st.button("🚀  Sınavı Başlat"):
        _start_quiz(all_qs, topic, length)

    if st.button("📊  Geçmişi Görüntüle"):
        st.session_state["page"] = "gecmis"; st.rerun()


def _start_quiz(all_qs, topic_filter, length) -> None:
    pool = all_qs if topic_filter == "Tüm Konular" \
           else [q for q in all_qs if q.topic == topic_filter]

    if len(pool) < length:
        st.error(
            f"Bu konuda yeterli soru yok "
            f"({len(pool)} mevcut, {length} istendi)."
        )
        return

    engine  = AdaptiveEngine(pool)
    session = QuizSession(questions_total=length)
    first_q = engine.next_question()

    st.session_state.update(
        engine=engine,
        session=session,
        current_q=first_q,
        q_start_time=time.time(),
        answered=False,
        chosen_index=None,
        page="sinav",
    )
    st.rerun()


# ── SINAV ─────────────────────────────────────────────────────────────────

def page_sinav() -> None:
    session: QuizSession    = st.session_state["session"]
    engine:  AdaptiveEngine = st.session_state["engine"]
    q                       = st.session_state["current_q"]
    total                   = st.session_state["quiz_length"]

    if q is None:
        _finish_quiz()
        return

    answered_so_far = session.answered
    if answered_so_far >= total:
        _finish_quiz()
        return

    # ── Başlık satırı ──────────────────────────────────────────────────────
    hcol1, hcol2, hcol3 = st.columns([2, 2, 1])
    with hcol1:
        st.markdown(f"**Soru {answered_so_far + 1} / {total}**")
    with hcol2:
        elapsed = time.time() - session.started_at
        st.markdown(
            f'<span class="iq-timer">⏱ {fmt_time(elapsed)}</span>',
            unsafe_allow_html=True,
        )
    with hcol3:
        st.markdown(f"✅ {session.correct_count}", unsafe_allow_html=True)

    # ── İlerleme çubuğu ────────────────────────────────────────────────────
    pct = answered_so_far / total * 100
    st.markdown(f"""
    <div class="iq-progress-wrap">
      <div class="iq-progress-fill" style="width:{pct}%"></div>
    </div>""", unsafe_allow_html=True)

    # ── Soru kartı ─────────────────────────────────────────────────────────
    diff_label = {1: "Kolay", 2: "Orta", 3: "Zor"}[q.difficulty]
    st.markdown(f"""
    <div class="iq-card iq-card-accent">
      <span class="iq-topic-badge">{q.topic}</span>
      <span class="iq-diff-badge iq-diff-{q.difficulty}">{diff_label}</span>
      <div class="iq-question-text">{q.text}</div>
    </div>""", unsafe_allow_html=True)

    # ── Cevap seçenekleri ──────────────────────────────────────────────────
    disabled = st.session_state["answered"]

    chosen_label = st.radio(
        "Cevabınızı seçin:",
        q.options,
        index=st.session_state["chosen_index"] if disabled else 0,
        disabled=disabled,
        key=f"radio_{q.id}",
    )
    chosen_index = q.options.index(chosen_label)

    # ── Gönder veya Sonraki ────────────────────────────────────────────────
    if not disabled:
        if st.button("Cevabı Gönder"):
            time_taken = time.time() - st.session_state["q_start_time"]
            correct    = session.record_answer(q, chosen_index, time_taken)
            engine.record_answer(q, correct)
            st.session_state.update(answered=True, chosen_index=chosen_index)
            st.rerun()
    else:
        correct = q.is_correct(chosen_index)
        if correct:
            st.markdown(f"""
            <div class="iq-feedback-correct">✅ Doğru!
              <div class="iq-explanation">{q.explanation}</div>
            </div>""", unsafe_allow_html=True)
        else:
            correct_text = q.options[q.answer_index]
            st.markdown(f"""
            <div class="iq-feedback-wrong">❌ Yanlış — Doğru cevap: <b>{correct_text}</b>
              <div class="iq-explanation">{q.explanation}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        next_label = "Sınavı Bitir" if (session.answered >= total) else "Sonraki Soru →"
        if st.button(next_label):
            if session.answered >= total:
                _finish_quiz()
            else:
                next_q = engine.next_question()
                st.session_state.update(
                    current_q=next_q,
                    q_start_time=time.time(),
                    answered=False,
                    chosen_index=None,
                )
                st.rerun()


def _finish_quiz() -> None:
    session: QuizSession = st.session_state["session"]
    session.finish()

    profile = st.session_state["profile"]
    profile.add_session(session)
    try:
        dh.save_profile(profile)
    except OSError as exc:
        st.warning(f"Sonuçlar kaydedilemedi: {exc}")

    st.session_state["page"] = "sonuc"
    st.rerun()


# ── SONUÇ ─────────────────────────────────────────────────────────────────

def page_sonuc() -> None:
    session: QuizSession = st.session_state["session"]
    if session is None:
        st.session_state["page"] = "kurulum"; st.rerun(); return

    letter, colour = grade_label(session.score_pct)

    st.markdown("## 🏁 Sınav Tamamlandı!")

    st.markdown(f'<div class="iq-grade" style="color:{colour}">{letter}</div>',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="iq-metric-row">
      <div class="iq-metric">
        <div class="iq-metric-value" style="color:{colour}">{session.score_pct}%</div>
        <div class="iq-metric-label">Puan</div>
      </div>
      <div class="iq-metric">
        <div class="iq-metric-value" style="color:#2F7D32">{session.correct_count}</div>
        <div class="iq-metric-label">Doğru</div>
      </div>
      <div class="iq-metric">
        <div class="iq-metric-value" style="color:#B3261E">{session.incorrect_count}</div>
        <div class="iq-metric-label">Yanlış</div>
      </div>
      <div class="iq-metric">
        <div class="iq-metric-value" style="color:#8C5A2B">{fmt_time(session.elapsed)}</div>
        <div class="iq-metric-label">Süre</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Konu bazlı analiz
    weak = session.weak_topics()
    if weak:
        st.markdown("### 📚 Konu Analizi")
        for topic, stats in weak.items():
            acc   = stats["accuracy"]
            col   = topic_colour(acc)
            bar_w = int(acc)
            st.markdown(f"""
            <div style="margin-bottom:0.7rem">
              <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                <span style="font-weight:600;color:#000000">{topic}</span>
                <span style="color:{col};font-weight:700">{acc}%
                  &nbsp;<small style="color:#5C4631">({stats['correct']}/{stats['total']})</small>
                </span>
              </div>
              <div class="iq-progress-wrap">
                <div class="iq-progress-fill" style="width:{bar_w}%;background:{col}"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    # Soru soru özet
    with st.expander("📋 Soru soru özet"):
        all_qs_map = {q.id: q for q in st.session_state["questions"]}
        for i, rec in enumerate(session.records, 1):
            q = all_qs_map.get(rec["question_id"])
            icon  = "✅" if rec["correct"] else "❌"
            label = q.text if q else rec["question_id"]
            st.markdown(f"**{i}. {icon} {label}**")
            if q and not rec["correct"]:
                st.caption(
                    f"Verdiğin cevap: {q.options[rec['chosen_index']]}  "
                    f"| Doğru cevap: {q.options[q.answer_index]}"
                )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁  Tekrar Çöz"):
            _start_quiz(
                st.session_state["questions"],
                st.session_state["topic_filter"],
                st.session_state["quiz_length"],
            )
    with col2:
        if st.button("🏠  Kuruluma Dön"):
            st.session_state.update(page="kurulum", session=None,
                                    engine=None, current_q=None)
            st.rerun()


# ── GEÇMİŞ ───────────────────────────────────────────────────────────────

def page_gecmis() -> None:
    profile = st.session_state["profile"]
    if not profile:
        st.session_state["page"] = "anasayfa"; st.rerun(); return

    st.markdown(f"## 📊 Geçmiş — {profile.display_name}")

    if not profile.history:
        st.info("Henüz tamamlanmış sınav yok. Önce bir sınav çöz!")
    else:
        letter, colour = grade_label(profile.avg_score)
        st.markdown(f"""
        <div class="iq-metric-row">
          <div class="iq-metric">
            <div class="iq-metric-value" style="color:{colour}">{profile.avg_score}%</div>
            <div class="iq-metric-label">Ort. Puan</div>
          </div>
          <div class="iq-metric">
            <div class="iq-metric-value" style="color:#2F7D32">{profile.best_score}%</div>
            <div class="iq-metric-label">En Yüksek</div>
          </div>
          <div class="iq-metric">
            <div class="iq-metric-value" style="color:#C1531B">{profile.sessions_count}</div>
            <div class="iq-metric-label">Sınav</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 📈 Puan değişimi")
        scores = [s["score_pct"] for s in profile.history]
        st.line_chart(scores)

        st.markdown("### 🗂️ Sınav günlüğü")
        for idx, sess in enumerate(reversed(profile.history), 1):
            import datetime as dt
            ts = dt.datetime.fromtimestamp(sess["started_at"]).strftime("%d.%m.%Y %H:%M")
            letter2, col2 = grade_label(sess["score_pct"])
            sira = len(profile.history) - idx + 1
            with st.expander(f"Sınav #{sira} — {ts} — {sess['score_pct']}% ({letter2})"):
                st.markdown(f"""
                **Doğru:** {sess['correct']} / {sess['answered']}  
                **Süre:** {fmt_time(sess['elapsed'])}  
                **Soru sayısı:** {sess['answered']}
                """)
                if sess.get("weak_topics"):
                    st.markdown("**Bu sınavdaki zayıf konular:**")
                    for t, s2 in sess["weak_topics"].items():
                        col3 = topic_colour(s2["accuracy"])
                        st.markdown(
                            f"- **{t}**: <span style='color:{col3}'>{s2['accuracy']}%</span> "
                            f"({s2['correct']}/{s2['total']})",
                            unsafe_allow_html=True,
                        )

        if profile.cumulative_weak_topics:
            st.markdown("### 🎯 Birikimli zayıf konular")
            for topic, acc in sorted(
                profile.cumulative_weak_topics.items(), key=lambda x: x[1]
            ):
                col4 = topic_colour(acc)
                st.markdown(
                    f"- **{topic}**: <span style='color:{col4}'>{acc}%</span>",
                    unsafe_allow_html=True,
                )

    if st.button("← Kuruluma Dön"):
        st.session_state["page"] = "kurulum"; st.rerun()


# ──────────────────────────────────────────────────────────────────────────
# Sayfa yönlendirici
# ──────────────────────────────────────────────────────────────────────────

render_sidebar()

PAGE = st.session_state["page"]

if   PAGE == "anasayfa": page_anasayfa()
elif PAGE == "giris":    page_giris()
elif PAGE == "kayit":    page_kayit()
elif PAGE == "kurulum":  page_kurulum()
elif PAGE == "sinav":    page_sinav()
elif PAGE == "sonuc":    page_sonuc()
elif PAGE == "gecmis":   page_gecmis()
else:
    st.error(f"Bilinmeyen sayfa: {PAGE}")
    st.session_state["page"] = "anasayfa"
    st.rerun()
