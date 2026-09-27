"""
generative_engine.py
=====================
Bu modul, projenin "Generative AI" katmanini olusturur.

Onceki asamalardan farki:
    - Kural tabanli sistem   -> sabit if/else mantigiyla calisir, yeni bir sey URETMEZ.
    - Klasik Machine Learning -> veriden ogrenir, ama sadece SINIFLANDIRIR / TAHMIN EDER.
    - Generative AI (burasi) -> kullanicinin girdisini anlayip SIFIRDAN, OZGUN, YENI
      bir metin ICERIK URETIR (aciklama, ozet, yeniden yazim, fikir, vb.).

Kullanilan API: Groq (https://groq.com)
    - OpenAI ile uyumlu bir REST API sunar (ekstra SDK gerekmez, sadece `requests`).
    - Ucretsiz katmani cok cömert ve kolay erisilebilir (sadece e-posta ile hesap acilir).
    - Cok hizli calisir (LPU altyapisi sayesinde), bu da canli demo icin idealdir.

ONEMLI GUVENLIK NOTU:
    Bu dosyada API key ASLA sabit (hardcoded) olarak yazilmaz.
    API key sirasiyla su kaynaklardan okunur:
        1) Streamlit secrets  (st.secrets["GROQ_API_KEY"])      -> Streamlit Cloud icin
        2) Ortam degiskeni    (os.environ["GROQ_API_KEY"])      -> local / .env / diger platformlar
    Bu dosya hicbir zaman bir key OLUSTURMAZ ya da dosyaya YAZMAZ; sadece OKUR.
"""

from __future__ import annotations

import os
from typing import Optional

import requests

# --- Sabitler -----------------------------------------------------------

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# NOT: "llama-3.3-70b-versatile" Groq tarafindan 16 Agustos 2026'da deprecated
# edildigi icin guncel, aktif bir production modeline gecildi.
GROQ_MODEL = "openai/gpt-oss-120b"
REQUEST_TIMEOUT_SECONDS = 30


class GenAIError(Exception):
    """Kullaniciya dogrudan gosterilebilecek, anlasilir Generative AI hatalari."""


# --- API key yonetimi ----------------------------------------------------

def get_api_key() -> Optional[str]:
    """
    API key'i asagidaki oncelik sirasiyla okur. Hicbirinde bulunamazsa None doner
    (uygulama COKMEZ, sadece kullaniciya bilgilendirici bir mesaj gosterilir).

    1. Streamlit secrets (Streamlit Community Cloud deploy senaryosu)
    2. Ortam degiskeni GROQ_API_KEY (.env, local calisma, diger deployment ortamlari)
    """
    try:
        import streamlit as st  # local import: bu modul Streamlit disinda da kullanilabilsin
        if hasattr(st, "secrets"):
            try:
                value = st.secrets.get("GROQ_API_KEY")
                if value:
                    return value
            except Exception:
                # st.secrets dosyasi hic tanimlanmamissa Streamlit exception atabilir.
                pass
    except Exception:
        pass

    return os.environ.get("GROQ_API_KEY")


# --- Mod tanimlari ---------------------------------------------------------
# Her mod, modele farkli bir "sistem talimati" (system prompt) verir.
# Boylece ayni model, kullanicinin secimine gore FARKLI TURDE icerik uretir.

MODE_PROMPTS = {
    "explain": {
        "label": "📘 Explain / Açıkla",
        "placeholder": "Örn: Kuantum bilgisayarları 12 yaşındaki bir çocuğa açıkla",
        "system": (
            "Sen deneyimli ve sabirli bir egitmensin. Kullanicinin verdigi konuyu, "
            "anlasilir bir Turkce ile, gerekirse gunluk hayattan ornekler kullanarak acikla. "
            "Karmasik terimleri basitlestir, ama bilgiyi yanlis veya eksik aktarma."
        ),
    },
    "summarize": {
        "label": "📝 Summarize / Özetle",
        "placeholder": "Özetlemek istediğiniz metni buraya yapıştırın",
        "system": (
            "Sen profesyonel bir editorsun. Kullanicinin verdigi metni, ana fikirleri "
            "koruyarak kisa, net ve akici bir sekilde ozetle. Uygunsa madde isaretleri kullan."
        ),
    },
    "rewrite": {
        "label": "✍️ Rewrite / Yeniden Yaz",
        "placeholder": "Yeniden yazılmasını istediğiniz metni girin",
        "system": (
            "Sen yaratici bir metin yazarisin. Kullanicinin verdigi metni anlamini koruyarak, "
            "daha akici, daha etkileyici ve daha profesyonel bir uslupla yeniden yaz."
        ),
    },
    "ideas": {
        "label": "💡 Generate Ideas / Fikir Üret",
        "placeholder": "Örn: Bir kahve dükkanı için pazarlama fikirleri üret",
        "system": (
            "Sen yaratici bir strateji danismanisin. Kullanicinin verdigi konu icin ozgun, "
            "uygulanabilir ve cesitli fikirler uret. Fikirleri numarali liste halinde sun ve "
            "her birine bir cumlelik kisa bir aciklama ekle."
        ),
    },
    "evolution": {
        "label": "🕰️ AI Evrimi Perspektifi / Three Ages Perspective",
        "placeholder": "Örn: Bir e-postanın spam olup olmadığına nasıl karar verilir?",
        "system": (
            "Kullanicinin verdigi konu/soru karsisinda uc farkli yapay zeka yaklasiminin "
            "nasil davranacagini kisa ve ogretici sekilde goster:\n\n"
            "1) KURAL TABANLI SISTEM ne yapardi? (sabit if/else mantigiyla, kati ve sinirli bir yanit)\n"
            "2) KLASIK MACHINE LEARNING modeli ne yapardi? (veriden ogrenilmis bir siniflandirma/tahmin, "
            "ama yeni icerik URETEMEZ, sadece var olan kategoriler arasinda secim yapar)\n"
            "3) GENERATIVE AI (sen) ne yapar? (baglami anlayip ozgun, akici, yeni bir icerik uretir)\n\n"
            "Bu uc yaklasimi net baslıklarla ayirarak karsilastir. Kisa ve carpici tut."
        ),
    },
}

DEFAULT_MODE = "explain"


# --- Ana fonksiyon ---------------------------------------------------------

def generate_content(prompt: str, mode: str) -> str:
    """
    Verilen prompt ve moda gore Groq API uzerinden generative AI ciktisi uretir.

    Args:
        prompt: Kullanicinin girdigi metin.
        mode:   MODE_PROMPTS icindeki anahtarlardan biri.

    Returns:
        Modelin urettigi metin.

    Raises:
        GenAIError: API key eksikse, istek basarisiz olursa veya gecersiz
                    bir girdi varsa; her zaman kullaniciya gosterilebilecek
                    anlasilir bir mesajla birlikte.
    """
    if not prompt or not prompt.strip():
        raise GenAIError("Lütfen önce bir metin/prompt girin.")

    api_key = get_api_key()
    if not api_key:
        raise GenAIError(
            "API key bulunamadı. Lütfen deployment secrets bölümünden API key ekleyin."
        )

    mode_config = MODE_PROMPTS.get(mode, MODE_PROMPTS[DEFAULT_MODE])

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": mode_config["system"]},
            {"role": "user", "content": prompt.strip()},
        ],
        "temperature": 0.7,
        # Groq'un guncel API'sinde token limiti "max_completion_tokens" ile
        # verilir (eski "max_tokens" alani artik desteklenmiyor / hataya yol aciyor).
        "max_completion_tokens": 1024,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            GROQ_API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
        )
    except requests.exceptions.Timeout:
        raise GenAIError("İstek zaman aşımına uğradı. Lütfen tekrar deneyin.") from None
    except requests.exceptions.ConnectionError:
        raise GenAIError(
            "API'ye bağlanılamadı. İnternet bağlantınızı kontrol edip tekrar deneyin."
        ) from None
    except requests.exceptions.RequestException as exc:
        raise GenAIError(f"Beklenmeyen bir bağlantı hatası oluştu: {exc}") from None

    if response.status_code == 404:
        raise GenAIError(
            "İstenen model Groq tarafından bulunamadı (muhtemelen kaldırılmış/"
            "deprecated bir model adı kullanılıyor). Lütfen GROQ_MODEL değerini "
            "güncel bir Groq production modeliyle değiştirin."
        )
    if response.status_code == 401:
        raise GenAIError(
            "API key geçersiz görünüyor. Lütfen doğru bir GROQ_API_KEY girdiğinizden emin olun."
        )
    if response.status_code == 429:
        raise GenAIError("API istek limiti aşıldı. Lütfen bir süre sonra tekrar deneyin.")
    if response.status_code >= 500:
        raise GenAIError("API sağlayıcısında geçici bir sorun var. Lütfen tekrar deneyin.")
    if response.status_code != 200:
        raise GenAIError(
            f"API isteği başarısız oldu (kod: {response.status_code}). Lütfen tekrar deneyin."
        )

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, ValueError):
        raise GenAIError("API yanıtı işlenemedi. Lütfen tekrar deneyin.") from None