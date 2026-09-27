# 🧠 Generative AI Studio

Bu modül, projenin **Generative AI** aşamasını gösteren ayrı ve bağımsız çalışan
bir Streamlit uygulamasıdır. Mevcut Machine Learning / NLP pipeline'larına
dokunmaz, dataset'i değiştirmez; onların **yanında** çalışan yeni bir katmandır.

---

## 1. Generative AI nedir?

Projenin önceki aşamalarında sistemler şunları yapıyordu:

| Aşama | Ne yapar? | Sınırı |
|---|---|---|
| Kural Tabanlı Sistemler | Sabit if/else mantığıyla karar verir | Yeni durumlara uyum sağlayamaz |
| Machine Learning | Veriden öğrenir, **sınıflandırır / tahmin eder** | Sadece var olan kategoriler arasından seçim yapar |
| NLP Pipeline'ları | Metni işler, özellik çıkarır, anlamlandırır | Yeni bir içerik **üretmez** |
| **Generative AI** | Girdiyi anlar ve **sıfırdan yeni içerik üretir** | — |

**Generative AI (Üretici Yapay Zeka)**, büyük miktarda metinle eğitilmiş bir
dil modelinin (LLM), kullanıcıdan aldığı bir girdiyi (prompt) anlayarak
**daha önce hiç var olmayan, özgün bir çıktı** üretmesidir. Bu çıktı bir
açıklama, bir özet, yeniden yazılmış bir metin veya yeni fikirler olabilir.

Bu, projenin bir önceki aşamasındaki "tahmin etme" mantığından temel bir
farkla ayrılır: model artık sabit bir cevap kümesinden seçim yapmaz,
**yaratır**.

---

## 2. Bu uygulama ne yapıyor?

Kullanıcı bir metin/prompt girer, bir **mod** seçer ve `GENERATE` butonuna
basar. Uygulama bu girdiyi gerçek bir LLM API'sine gönderir ve modelin
ürettiği içeriği ekranda gösterir.

Temel akış:

```
Kullanıcı Girdisi (Prompt)
        ↓
Mod Seçimi (Explain / Summarize / Rewrite / Generate Ideas / 3 Çağ Perspektifi)
        ↓
Generative AI Modeli (Groq LLM API)
        ↓
Üretilen İçerik
        ↓
Web Arayüzü (Streamlit)
```

### Mevcut modlar

- **📘 Explain / Açıkla** — Girilen konuyu anlaşılır bir dille açıklar.
- **📝 Summarize / Özetle** — Girilen metni kısa ve net şekilde özetler.
- **✍️ Rewrite / Yeniden Yaz** — Girilen metni daha akıcı bir üslupla yeniden yazar.
- **💡 Generate Ideas / Fikir Üret** — Girilen konu için özgün fikirler üretir.
- **🕰️ AI Evrimi Perspektifi** — Aynı soruya kural tabanlı sistem, klasik ML
  modeli ve Generative AI'ın nasıl farklı yanıtlar vereceğini karşılaştırmalı
  gösterir. Bu mod, projenin genel "AI'ın evrimi" temasını doğrudan canlı bir
  örnekle gösterir.

---

## 3. Kullanılan model / API

- **Sağlayıcı:** [Groq](https://groq.com)
- **Model:** `llama-3.3-70b-versatile` (açık kaynaklı, güçlü bir LLM)
- **Neden Groq?**
  - Ücretsiz katmanı cömert ve kolayca (sadece e-posta ile) alınabiliyor.
  - API'si OpenAI ile uyumlu ve **tek bir HTTP isteği** ile çalışıyor; ekstra
    ağır bir SDK gerektirmiyor (sadece `requests` kütüphanesi kullanıldı).
  - Yanıt hızı çok yüksek, bu da canlı bir demo için ideal bir kullanıcı
    deneyimi sağlıyor.
  - Streamlit Community Cloud gibi ücretsiz platformlarda sorunsuz çalışıyor.

> Kod, `generative_engine.py` içinde tek bir API isteği fonksiyonunda
> toplandığı için istenirse ileride başka bir sağlayıcıya (OpenAI, Gemini vb.)
> geçmek de kolaydır.

---

## 4. Dosya yapısı

```
genai_studio/
├── app.py                        # Streamlit arayüzü (UI)
├── generative_engine.py          # Generative AI mantığı (API çağrısı, modlar, hata yönetimi)
├── requirements.txt              # Bağımlılıklar
├── .env.example                  # Local .env şablonu (gerçek key İÇERMEZ)
├── .streamlit/secrets.toml.example  # Streamlit Cloud secrets şablonu (gerçek key İÇERMEZ)
├── .gitignore                    # .env ve secrets.toml'u repo dışında tutar
└── README.md                     # Bu dosya
```

---

## 5. Kurulum (Local)

```bash
# 1) Bu klasöre girin
cd genai_studio

# 2) Sanal ortam oluşturun (opsiyonel ama önerilir)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3) Bağımlılıkları kurun
pip install -r requirements.txt
```

---

## 6. API key nasıl eklenir?

API key **kesinlikle kod içine yazılmaz**. İki yöntemden biriyle eklenir:

### Yöntem A — Local çalıştırma için `.env`

1. `.env.example` dosyasını kopyalayıp adını `.env` yapın.
2. İçine gerçek API key'inizi yazın:
   ```
   GROQ_API_KEY=gsk_xxx...
   ```
3. API key'i şuradan ücretsiz alabilirsiniz: <https://console.groq.com>
4. `.env` dosyası `.gitignore` içinde olduğu için **GitHub'a asla gönderilmez.**

### Yöntem B — Streamlit Community Cloud secrets

1. Uygulamayı Streamlit Cloud'da deploy ettikten sonra **Settings → Secrets**
   bölümüne girin.
2. `.streamlit/secrets.toml.example` dosyasındaki formatı kullanarak şunu
   yapıştırın:
   ```toml
   GROQ_API_KEY = "gsk_xxx..."
   ```
3. Kaydedin — uygulama otomatik olarak yeniden başlar ve key'i okur.

> Uygulama, önce Streamlit secrets'a, sonra ortam değişkenine bakar. İkisi de
> yoksa **çökmez**, kullanıcıya net bir uyarı mesajı gösterir:
> *"API key bulunamadı. Lütfen deployment secrets bölümünden API key ekleyin."*

---

## 7. Local olarak çalıştırma

```bash
streamlit run app.py
```

Tarayıcıda otomatik olarak `http://localhost:8501` açılır.

---

## 8. Online deploy etme (Streamlit Community Cloud)

1. Bu klasördeki dosyaları (```.env``` **hariç**, zaten `.gitignore` içinde)
   bir GitHub reposuna push edin.
2. [share.streamlit.io](https://share.streamlit.io) adresine gidip GitHub
   hesabınızla giriş yapın.
3. **New app** deyip reponuzu, branch'i ve ana dosya olarak `app.py`'yi seçin
   (eğer `genai_studio` bir alt klasördeyse, dosya yolunu
   `genai_studio/app.py` olarak belirtin).
4. Deploy etmeden önce ya da sonra **Settings → Secrets** bölümüne
   `GROQ_API_KEY = "..."` satırını ekleyin.
5. **Deploy** butonuna basın — birkaç dakika içinde uygulamanız herkese açık
   bir linkle (`https://your-app-name.streamlit.app`) yayında olur.

Başka bir platforma (Render, Railway, Hugging Face Spaces vb.) deploy etmek
isterseniz de aynı mantık geçerlidir: `requirements.txt` ile bağımlılıkları
kurup, `GROQ_API_KEY` ortam değişkenini o platformun kendi "Environment
Variables / Secrets" bölümünden tanımlamanız yeterlidir.

---

## 9. Hata yönetimi

- **API key yoksa:** Uygulama çökmez, sayfanın üstünde şu uyarı gösterilir:
  *"API key bulunamadı. Lütfen deployment secrets bölümünden API key ekleyin."*
- **API isteği başarısız olursa** (geçersiz key, limit aşımı, zaman aşımı,
  sunucu hatası, bağlantı sorunu vb.), kullanıcıya duruma özel, anlaşılır bir
  hata mesajı gösterilir; uygulama çalışmaya devam eder.
- **Boş prompt gönderilirse:** Kullanıcıdan önce bir metin girmesi istenir.

---

## 10. Örnek kullanım

**Mod:** 📘 Explain / Açıkla
**Prompt:** `Transformer mimarisi nedir, kısaca anlat`
**Çıktı (örnek):** Modelin, "dikkat mekanizması" (attention) kavramını basit
bir dille, günlük hayattan bir benzetmeyle açıkladığı birkaç paragraflık bir
metin.

**Mod:** 🕰️ AI Evrimi Perspektifi
**Prompt:** `Bir e-postanın spam olup olmadığına nasıl karar verilir?`
**Çıktı (örnek):** Aynı soruya kural tabanlı bir filtrenin ("belirli kelimeler
geçiyorsa spam'dir"), klasik bir ML sınıflandırıcısının ("öğrenilmiş
olasılıklara göre spam/spam değil") ve Generative AI'ın (bağlamı analiz edip
gerekçeli bir açıklama üreterek) nasıl farklı yaklaştığını gösteren
karşılaştırmalı bir yanıt.

---

## ✅ Önemli Notlar

- **Dataset'e dokunulmadı.** Bu modül, mevcut Machine Learning / NLP
  pipeline'larından tamamen bağımsız çalışır.
- **API key veya secret GitHub'a eklenmedi.** Repoda yalnızca `.env.example`
  ve `secrets.toml.example` gibi **gerçek anahtar içermeyen şablon dosyalar**
  bulunur; gerçek key'ler `.gitignore` ile korunur.
