"""
app.py
======
Generative AI Studio - Streamlit arayuzu.

Bu dosya, projenin "Generative AI" asamasini gosteren AYRI ve BAGIMSIZ bir
uygulamadir. Mevcut Machine Learning / NLP pipeline'larina dokunmaz; sadece
onlarin yaninda calisan yeni bir katmandir.

Temel akis:
    Kullanici girdisi (prompt) -> Mod secimi -> Generative AI (Groq LLM API)
    -> Uretilen icerik -> Web arayuzunde goruntuleme

Calistirma:
    streamlit run app.py
"""

import streamlit as st

try:
    # Local gelistirme icin .env dosyasini yukler (varsa). Streamlit Cloud'da
    # zaten st.secrets kullanildigi icin bu adim orada bir etkisi olmaz ve
    # dosya yoksa sessizce gecilir.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from generative_engine import (
    DEFAULT_MODE,
    MODE_PROMPTS,
    GenAIError,
    generate_content,
    get_api_key,
)

# --------------------------------------------------------------------------
# Sayfa yapilandirmasi
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="Generative AI Studio",
    page_icon="🧠",
    layout="centered",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 2.5rem; max-width: 780px;}
        .genai-badge {
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            color: white;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        .result-box {
            border: 1px solid rgba(139, 92, 246, 0.35);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            background: rgba(139, 92, 246, 0.06);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Baslik ve tanitim
# --------------------------------------------------------------------------

st.markdown('<span class="genai-badge">GENERATIVE AI</span>', unsafe_allow_html=True)
st.title("🧠 Generative AI Studio")
st.caption("Kural Tabanlı Sistemler → Machine Learning → NLP → **Generative AI**")

with st.expander("ℹ️ Bu uygulama ne yapıyor? / Generative AI nedir?", expanded=False):
    st.markdown(
        """
Önceki aşamalarda sistem **var olan veriden** öğrenip bir sınıflandırma ya da
tahmin yapıyordu (örn. bir metnin spam olup olmadığına karar vermek).

**Generative AI** ise bir adım öteye geçer: sistem artık sadece mevcut
seçenekler arasından seçim yapmaz, kullanıcının girdisini **anlayarak
sıfırdan yeni bir içerik üretir** — bir açıklama, bir özet, yeni bir metin
veya özgün fikirler gibi.

Bu demo, gerçek bir büyük dil modeli (LLM) API'sine bağlanarak bu üretim
sürecini canlı olarak gösterir. Aşağıdan bir mod seçip bir prompt girerek
modelin gerçek zamanlı olarak nasıl yeni içerik ürettiğini görebilirsiniz.
        """
    )

# API key kontrolu - uygulama COKMEZ, sadece bilgilendirir.
if not get_api_key():
    st.warning(
        "⚠️ **API key bulunamadı.** Lütfen deployment secrets bölümünden "
        "API key ekleyin. (Streamlit Cloud kullanıyorsanız: *Settings → Secrets* "
        "içine `GROQ_API_KEY = \"...\"` satırını ekleyin. Local çalışıyorsanız "
        "proje köküne bir `.env` dosyası ekleyip `GROQ_API_KEY=...` yazın.)"
    )

# --------------------------------------------------------------------------
# Kullanici girdisi
# --------------------------------------------------------------------------

st.subheader("Ne üretmek istiyorsunuz?")

mode_key = st.selectbox(
    "Mod seçimi",
    options=list(MODE_PROMPTS.keys()),
    index=list(MODE_PROMPTS.keys()).index(DEFAULT_MODE),
    format_func=lambda key: MODE_PROMPTS[key]["label"],
)

prompt = st.text_area(
    "Prompt'unuzu girin",
    height=160,
    placeholder=MODE_PROMPTS[mode_key]["placeholder"],
)

generate_clicked = st.button("🚀 GENERATE", type="primary", use_container_width=True)

# --------------------------------------------------------------------------
# Uretim akisi
# --------------------------------------------------------------------------

if generate_clicked:
    with st.spinner("Generative AI içerik üretiyor..."):
        try:
            result = generate_content(prompt, mode_key)
            st.session_state["last_result"] = result
            st.session_state["last_mode_label"] = MODE_PROMPTS[mode_key]["label"]
        except GenAIError as error:
            st.session_state.pop("last_result", None)
            st.error(f"❌ {error}")

if "last_result" in st.session_state:
    st.subheader("✨ Üretilen İçerik")
    st.caption(f"Mod: {st.session_state.get('last_mode_label', '')}")
    st.markdown(
        f'<div class="result-box">{st.session_state["last_result"]}</div>',
        unsafe_allow_html=True,
    )
    st.download_button(
        "📄 Sonucu indir (.txt)",
        data=st.session_state["last_result"],
        file_name="generative_ai_output.txt",
        mime="text/plain",
    )

# --------------------------------------------------------------------------
# Kenar cubugu - proje baglami ve model bilgisi
# --------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🧭 Projenin Evrimi")
    st.markdown(
        """
        1. Kural Tabanlı Sistemler
        2. Machine Learning
        3. NLP & Klasik Pipeline'lar
        4. **Generative AI** ← *buradasınız*
        """
    )
    st.divider()
    st.markdown("### ⚙️ Kullanılan Model")
    st.markdown(
        """
        **Sağlayıcı:** [Groq](https://groq.com) API
        **Model:** `llama-3.3-70b-versatile`

        Groq, açık kaynaklı büyük dil modellerini çok hızlı ve
        ücretsiz bir katmanla sunan bir API sağlayıcısıdır.
        """
    )
    st.divider()
    st.caption(
        "API key kod içine yazılmaz; yalnızca ortam değişkeni veya "
        "Streamlit secrets üzerinden okunur."
    )
