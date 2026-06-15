# 🧠 AdaptIQ — Uyarlanabilir Sınav Sistemi

> **Python** ve **Streamlit** ile geliştirilmiş, öğrencinin hatalarından öğrenerek soru akışını dinamik olarak yeniden düzenleyen akıllı bir sınav uygulaması.

---

## 📌 Proje Hakkında

AdaptIQ, geleneksel "rastgele soru" yaklaşımının ötesine geçer. Sistem, öğrencinin her yanlış cevabını anlık olarak analiz eder ve o konuya ait soruların seçilme olasılığını artırır. Bu sayede her sınav denemesi, öğrencinin bireysel eksikliklerine odaklanan kişiselleştirilmiş bir pekiştirme oturumuna dönüşür. Tüm öğrenci verileri, profil geçmişi ve soru bankası JSON dosyaları aracılığıyla kalıcı olarak saklanır.

---

## ✨ Temel Özellikler

### 🤖 Uyarlanabilir Öğrenme Algoritması
Sistem, her konu için bir **ağırlık puanı** tutar. Öğrenci bir soruyu yanlış yanıtladığında o konunun ağırlığı artar; doğru yanıtladığında azalır. Bir sonraki soru, bu ağırlıklarla orantılı olasılıklı bir havuzdan seçilir. Böylece zayıf konular daha sık yüzeye çıkar, ancak sistematik bir tekrar yerine doğal bir akış hissi korunur.

### ⏱️ Zamanlayıcı
Her sınav oturumu için geçen süre saniye hassasiyetiyle izlenir. Toplam süre ve soru başına harcanan zaman sonuç ekranında ve geçmiş kayıtlarında raporlanır.

### 📊 Puan ve Performans Takibi
- Doğru / yanlış cevap sayısı anlık olarak görüntülenir.
- Sınav sonunda her konu için ayrı doğruluk yüzdesi hesaplanır.
- Geçmiş oturumlar arası birikimli zayıf konu analizi profilde saklanır.
- Puan değişimi grafikle görselleştirilir.

### 🔄 Yeniden Oynanabilirlik
Soru seçimi olasılıksal olduğu için aynı sınavı tekrar alan öğrenci, her seferinde farklı bir soru sırası ve ağırlık dağılımıyla karşılaşır. Sorular ezberlenemez; her deneme gerçek bir öğrenme testidir.

### 👤 Öğrenci Profilleri
Her öğrenci için kullanıcı adı ve görünen ad içeren kalıcı bir profil oluşturulur. Tüm sınav geçmişi, ortalama puan, en yüksek puan ve birikimli zayıf konular JSON formatında saklanır.

### 🏗️ Modüler OOP Mimarisi
Kod, tek sorumluluk prensibine uygun bağımsız sınıflara ayrılmıştır. Her katman birbirinden bağımsız test edilebilir ve genişletilebilir.

---

## 🗂️ Proje Dosya Yapısı

```
adaptiq/
│
├── app.py              # Streamlit kullanıcı arayüzü ve sayfa yönlendiricisi
├── models.py           # OOP veri modelleri: Question, AdaptiveEngine, QuizSession, StudentProfile
├── storage.py          # JSON tabanlı kalıcı depolama: DataHandler sınıfı
├── requirements.txt    # Gerekli Python kütüphaneleri
│
└── data/               # İlk çalıştırmada otomatik olarak oluşturulur
    ├── questions.json      # Soru bankası (ilk çalıştırmada örnek sorularla doldurulur)
    ├── profiles.json       # Öğrenci profilleri ve sınav geçmişleri
    └── yedekler/           # Her kayıt işleminden önce otomatik yedekleme klasörü
```

### `app.py` — Kullanıcı Arayüzü ve Sayfa Yönlendiricisi

Uygulamanın Streamlit giriş noktasıdır. Altı sayfa barındırır: **Anasayfa**, **Giriş**, **Kayıt**, **Sınav Kurulumu**, **Sınav** ve **Geçmiş**. Tüm sayfa geçişleri `st.session_state` üzerinden yönetilir; harici bir çoklu sayfa mekanizmasına gerek duyulmaz. Özel CSS ile koyu tema ve dinamik bileşenler (ilerleme çubuğu, zamanlayıcı, geri bildirim kartları) uygulanır.

### `models.py` — OOP Veri Modelleri

Uygulamanın çekirdek iş mantığını barındırır; dosya sistemiyle hiçbir doğrudan etkileşimi yoktur.

| Sınıf | Sorumluluk |
|---|---|
| `Question` | Tek bir soruyu temsil eden değişmez veri sınıfı. `is_correct()`, `to_dict()`, `from_dict()` metotlarını içerir. |
| `AdaptiveEngine` | Ağırlıklı rastgele seçim motoru. `record_answer()` ile ağırlıkları günceller; `next_question()` ile bir sonraki soruyu belirler. |
| `QuizSession` | Aktif bir sınav oturumunun tüm değişken durumunu (kayıtlar, zamanlayıcı, puan, zayıf konu analizi) yönetir. |
| `StudentProfile` | Oturumlar arası kalıcı öğrenci verisi. Birikimli zayıf konu ortalamasını ağırlıklı hareketli ortalama ile günceller. |

### `storage.py` — JSON Kalıcı Depolama

`DataHandler` sınıfı, tüm dosya G/Ç işlemlerini merkezi olarak yönetir.

- **Atomik yazma:** Veriler önce `.tmp` uzantılı geçici bir dosyaya yazılır, ardından asıl dosyaya taşınır. Bu yöntem, yarım yazılmış ve bozuk JSON dosyası riskini sıfıra indirir.
- **Otomatik yedekleme:** Her yazma işleminden önce mevcut dosya `data/yedekler/` klasörüne zaman damgasıyla kopyalanır.
- **Başlangıç verisi:** `data/questions.json` dosyası bulunamazsa uygulama, 5 konuda 21 örnek sorudan oluşan Türkçe bir soru bankasını otomatik olarak oluşturur.
- **Hata yönetimi:** Tüm dosya işlemleri `try-except` blokları içinde sarmalanmıştır; bozuk soru kayıtları uygulamayı çökertmeden atlanır.

### `requirements.txt` — Bağımlılıklar

Projenin ihtiyaç duyduğu tek harici kütüphaneyi listeler. Python standart kütüphanesi dışında yalnızca **Streamlit** kullanılmaktadır.

---

## 🚀 Kurulum ve Çalıştırma

### Ön Koşullar

- Python **3.10** veya üzeri
- `pip` paket yöneticisi

### Adım 1 — Depoyu Klonla

```bash
git clone https://github.com/kullanici-adiniz/adaptiq.git
cd adaptiq
```

### Adım 2 — Sanal Ortam Oluştur (Önerilen)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Adım 3 — Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### Adım 4 — Uygulamayı Başlat

```bash
streamlit run app.py
```

Uygulama varsayılan olarak **http://localhost:8501** adresinde açılır.

> **Not:** İlk çalıştırmada `data/` klasörü ve içindeki `questions.json` dosyası otomatik olarak oluşturulur. Herhangi bir ön kurulum gerekmez.

---

## 📝 Özel Soru Ekleme

`data/questions.json` dosyasını bir metin editörüyle açarak aşağıdaki şemaya uygun yeni soru nesneleri ekleyebilirsiniz:

```json
{
  "id": "benzersiz_id",
  "topic": "Konu Adı",
  "difficulty": 2,
  "text": "Sorunuzu buraya yazın?",
  "options": ["Seçenek A", "Seçenek B", "Seçenek C", "Seçenek D"],
  "answer_index": 1,
  "explanation": "Bu cevabın neden doğru olduğunu açıklayın."
}
```

| Alan | Açıklama |
|---|---|
| `id` | Tüm sorular arasında benzersiz olmalıdır (örn. `"mat_001"`). |
| `topic` | Soru konusu — filtre ve uyarlama algoritmasında kullanılır. |
| `difficulty` | `1` = Kolay · `2` = Orta · `3` = Zor |
| `answer_index` | `options` dizisinde doğru cevabın 0 tabanlı indeksi. |
| `explanation` | Öğrenciye cevap sonrası gösterilecek açıklama metni. |

---

## 🏗️ Mimari Özet

```
┌─────────────────────────────────────────────┐
│                  app.py                     │
│         Streamlit Kullanıcı Arayüzü         │
│  (Sayfa yönlendirme · CSS · session_state)  │
└────────────────────┬────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
┌─────────▼──────────┐ ┌───────▼────────────┐
│     models.py      │ │    storage.py       │
│  ─────────────── │ │  ──────────────── │
│  Question          │ │  DataHandler       │
│  AdaptiveEngine    │ │  · Atomik yazma    │
│  QuizSession       │ │  · Otomatik yedek  │
│  StudentProfile    │ │  · Başlangıç verisi│
└────────────────────┘ └────────────────────┘
                                │
                     ┌──────────▼──────────┐
                     │      data/          │
                     │  questions.json     │
                     │  profiles.json      │
                     │  yedekler/          │
                     └─────────────────────┘
```

### Uyarlanabilir Algoritma — Adım Adım

```
Başlangıç: tüm konular için ağırlık = 1.0

Yanlış cevap → konu_ağırlığı += 2.0
Doğru cevap  → konu_ağırlığı  = max(1.0, konu_ağırlığı − 0.5)

Sonraki soru = random.choices(
    kalan_sorular,
    weights=[konu_ağırlığı[q.topic] for q in kalan_sorular]
)
```

Yüksek ağırlık → daha yüksek seçilme olasılığı.
Zayıf konular öne çıkar; ancak kesinleşmiş bir sıra olmadığından öğrenci soruları ezberleyemez.

---

## 🤝 Katkıda Bulunma

Her türlü katkı memnuniyetle karşılanır!

1. Bu depoyu **fork**'layın.
2. Yeni bir dal oluşturun: `git checkout -b ozellik/yeni-ozellik`
3. Değişikliklerinizi yapın ve commit'leyin: `git commit -m "Yeni özellik eklendi"`
4. Dalınızı gönderin: `git push origin ozellik/yeni-ozellik`
5. Bir **Pull Request** açın.

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında lisanslanmıştır.
