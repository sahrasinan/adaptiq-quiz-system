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
/* ── Renk paleti — Açık Tema ──────────────────────────────────── */
:root {
  --bg:          #F0F4FB;
  --surface:     #FFFFFF;
  --surface2:    #DDE6F8;
  --accent:      #4A6CF7;
  --accent2:     #0EA5A0;
  --success:     #16A34A;
  --danger:      #DC2626;
  --warn:        #D97706;
  --text:        #1A1F36;
  --text-muted:  #6B7280;
  --radius:      12px;
  --shadow:      0 2px 8px rgba(74,108,247,0.10);
}

/* ── Temel ────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--text);
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ── Kartlar ──────────────────────────────────────────────────── */
.iq-card {
  background: var(--surface);
  border: 1px solid #C7D9F5;
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow);
}
.iq-card-accent {
  border-left: 4px solid var(--accent);
}

/* ── Hero banner ──────────────────────────────────────────────── */
.iq-hero {
  background: linear-gradient(135deg, #E8EFFD 0%, #D5E3FA 100%);
  border: 1px solid #C7D9F5;
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
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0.3rem 0 0.2rem;
}
.iq-subtitle { color: var(--text-muted); font-size: 1rem; }

/* ── Ilerleme cubugu ──────────────────────────────────────────── */
.iq-progress-wrap {
  background: var(--surface2);
  border-radius: 99px;
  height: 8px;
  overflow: hidden;
  margin: 0.6rem 0 1.2rem;
}
.iq-progress-fill {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  transition: width 0.4s ease;
}

/* ── Soru karti ───────────────────────────────────────────────── */
.iq-question-text {
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1.6;
  color: var(--text);
}
.iq-topic-badge {
  display: inline-block;
  background: #E8EFFD;
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.2rem 0.7rem;
  border-radius: 99px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 0.8rem;
  border: 1px solid #C7D9F5;
}
.iq-diff-badge {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.2rem 0.7rem;
  border-radius: 99px;
  margin-left: 0.4rem;
}
.iq-diff-1 { background: #DCFCE7; color: #15803D; border: 1px solid #BBF7D0; }
.iq-diff-2 { background: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }
.iq-diff-3 { background: #FEE2E2; color: #B91C1C; border: 1px solid #FECACA; }

/* ── Cevap geri bildirimi ─────────────────────────────────────── */
.iq-feedback-correct {
  background: #F0FDF4;
  border: 1.5px solid #86EFAC;
  border-radius: var(--radius);
  padding: 0.9rem 1.1rem;
  color: var(--success);
  font-weight: 600;
}
.iq-feedback-wrong {
  background: #FFF1F2;
  border: 1.5px solid #FCA5A5;
  border-radius: var(--radius);
  padding: 0.9rem 1.1rem;
  color: var(--danger);
  font-weight: 600;
}
.iq-explanation {
  color: var(--text-muted);
  font-size: 0.93rem;
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
  background: var(--surface);
  border: 1px solid #C7D9F5;
  border-radius: var(--radius);
  padding: 0.8rem 1rem;
  text-align: center;
  box-shadow: var(--shadow);
}
.iq-metric-value { font-size: 1.9rem; font-weight: 800; line-height: 1; }
.iq-metric-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ── Not harfi ────────────────────────────────────────────────── */
.iq-grade {
  font-size: 5rem;
  font-weight: 900;
  text-align: center;
  line-height: 1;
  margin: 0.5rem 0;
}

/* ── Kenar cubugu ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: #E8EFFD !important;
  border-right: 1px solid #C7D9F5;
}

/* ── Streamlit gecersiz kilmalari ─────────────────────────────── */
div.stButton > button {
  background: linear-gradient(135deg, var(--accent), #3451C4);
  color: #FFFFFF !important;
  border: none;
  border-radius: var(--radius);
  font-weight: 600;
  padding: 0.55rem 1.4rem;
  width: 100%;
  transition: opacity .2s, box-shadow .2s;
  box-shadow: 0 2px 6px rgba(74,108,247,0.25);
}
div.stButton > button:hover  { opacity: 0.88; box-shadow: 0 4px 12px rgba(74,108,247,0.35); }
div.stButton > button:active { opacity: 0.72; }

div[data-testid="stRadio"] label {
  background: #F4F8FE;
  border: 1px solid #C7D9F5;
  border-radius: 8px;
  padding: 0.6rem 0.9rem;
  margin: 0.25rem 0;
  cursor: pointer;
  transition: background .15s, border-color .15s;
  display: block;
  color: var(--text);
}
div[data-testid="stRadio"] label:hover {
  background: #E8EFFD;
  border-color: var(--accent);
}

[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select {
  background: #F4F8FE !important;
  color: var(--text) !important;
  border: 1px solid #C7D9F5 !important;
  border-radius: 8px !important;
}

/* ── Zamanlayici ──────────────────────────────────────────────── */
.iq-timer {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--accent2);
  font-variant-numeric: tabular-nums;
}

hr { border-color: #C7D9F5; }
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
    if pct >= 90: return "A+", "#2ECC71"
    if pct >= 80: return "A",  "#2ECC71"
    if pct >= 70: return "B",  "#4ECDC4"
    if pct >= 60: return "C",  "#F39C12"
    if pct >= 50: return "D",  "#E67E22"
    return            "F",  "#E74C3C"


def topic_colour(accuracy: float) -> str:
    if accuracy >= 75: return "#2ECC71"
    if accuracy >= 50: return "#F39C12"
    return "#E74C3C"


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
        " · ".join(f"<span style='color:var(--danger)'>{t}</span> ({a}%)"
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
        <div class="iq-metric-value" style="color:#2ECC71">{session.correct_count}</div>
        <div class="iq-metric-label">Doğru</div>
      </div>
      <div class="iq-metric">
        <div class="iq-metric-value" style="color:#E74C3C">{session.incorrect_count}</div>
        <div class="iq-metric-label">Yanlış</div>
      </div>
      <div class="iq-metric">
        <div class="iq-metric-value" style="color:#4ECDC4">{fmt_time(session.elapsed)}</div>
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
                <span style="font-weight:600">{topic}</span>
                <span style="color:{col};font-weight:700">{acc}%
                  &nbsp;<small style="color:var(--text-muted)">({stats['correct']}/{stats['total']})</small>
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
            <div class="iq-metric-value" style="color:#2ECC71">{profile.best_score}%</div>
            <div class="iq-metric-label">En Yüksek</div>
          </div>
          <div class="iq-metric">
            <div class="iq-metric-value" style="color:#7C6BFF">{profile.sessions_count}</div>
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
