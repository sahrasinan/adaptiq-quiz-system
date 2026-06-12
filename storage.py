"""
storage.py — JSON tabanlı kalıcı depolama katmanı.

Tüm dosya G/Ç işlemleri DataHandler üzerinden yürütülür; böylece
uygulamanın geri kalanı doğrudan dosya sistemine erişmez.
"""

from __future__ import annotations
import json
import os
import shutil
import time
from pathlib import Path
from typing import Optional

from models import Question, StudentProfile


# ---------------------------------------------------------------------------
# Yollar
# ---------------------------------------------------------------------------

DATA_DIR       = Path("data")
QUESTIONS_FILE = DATA_DIR / "questions.json"
PROFILES_FILE  = DATA_DIR / "profiles.json"
BACKUP_DIR     = DATA_DIR / "yedekler"


# ---------------------------------------------------------------------------
# DataHandler
# ---------------------------------------------------------------------------

class DataHandler:
    """
    JSON okuma/yazma için ince bir sarmalayıcı:
    - Atomik yazma (önce .tmp'ye yaz, sonra yeniden adlandır)
    - Her yazmadan önce otomatik yedekleme
    - Yapılandırılmış hata yönetimi
    """

    def __init__(self) -> None:
        DATA_DIR.mkdir(exist_ok=True)
        BACKUP_DIR.mkdir(exist_ok=True)
        self._sorulari_yoksa_ekle()

    # ── Düşük seviye yardımcılar ───────────────────────────────────────────

    @staticmethod
    def _json_oku(path: Path) -> dict | list:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            raise FileNotFoundError(f"Veri dosyası bulunamadı: {path}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path} içindeki JSON bozuk: {exc}") from exc

    @staticmethod
    def _json_yaz(path: Path, data: dict | list) -> None:
        """Atomik yazma: önce .tmp'ye yaz, sonra asıl yere taşı."""
        tmp = path.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            shutil.move(str(tmp), str(path))
        except OSError as exc:
            tmp.unlink(missing_ok=True)
            raise OSError(f"{path} yazılamadı: {exc}") from exc

    def _yedekle(self, path: Path) -> None:
        if not path.exists():
            return
        ts   = int(time.time())
        dest = BACKUP_DIR / f"{path.stem}_{ts}{path.suffix}"
        try:
            shutil.copy2(str(path), str(dest))
        except OSError:
            pass  # Yedekleme hatası kritik değil

    # ── Sorular ───────────────────────────────────────────────────────────

    def load_questions(self) -> list[Question]:
        raw = self._json_oku(QUESTIONS_FILE)
        questions = []
        for item in raw:
            try:
                questions.append(Question.from_dict(item))
            except (KeyError, ValueError) as exc:
                print(f"[DataHandler] Bozuk soru atlandı: {exc}")
        return questions

    def save_questions(self, questions: list[Question]) -> None:
        self._yedekle(QUESTIONS_FILE)
        self._json_yaz(QUESTIONS_FILE, [q.to_dict() for q in questions])

    # ── Profiller ─────────────────────────────────────────────────────────

    def _profilleri_ham_yukle(self) -> dict[str, dict]:
        if not PROFILES_FILE.exists():
            return {}
        try:
            return self._json_oku(PROFILES_FILE)
        except (FileNotFoundError, ValueError):
            return {}

    def load_profile(self, username: str) -> Optional[StudentProfile]:
        raw = self._profilleri_ham_yukle()
        if username not in raw:
            return None
        try:
            return StudentProfile.from_dict(raw[username])
        except (KeyError, TypeError) as exc:
            raise ValueError(f"'{username}' profili bozuk: {exc}") from exc

    def save_profile(self, profile: StudentProfile) -> None:
        raw = self._profilleri_ham_yukle()
        raw[profile.username] = profile.to_dict()
        self._yedekle(PROFILES_FILE)
        self._json_yaz(PROFILES_FILE, raw)

    def list_usernames(self) -> list[str]:
        return list(self._profilleri_ham_yukle().keys())

    def profile_exists(self, username: str) -> bool:
        return username in self._profilleri_ham_yukle()

    def create_profile(self, username: str, display_name: str) -> StudentProfile:
        if self.profile_exists(username):
            raise ValueError(f"'{username}' kullanıcı adı zaten mevcut.")
        profile = StudentProfile(username=username, display_name=display_name)
        self.save_profile(profile)
        return profile

    # ── Başlangıç verisi ──────────────────────────────────────────────────

    def _sorulari_yoksa_ekle(self) -> None:
        if QUESTIONS_FILE.exists():
            return
        self._json_yaz(QUESTIONS_FILE, _BASLANGIC_SORULARI)


# ---------------------------------------------------------------------------
# Başlangıç soru bankası (questions.json yoksa ilk çalıştırmada oluşturulur)
# ---------------------------------------------------------------------------

_BASLANGIC_SORULARI: list[dict] = [

    # ── Python Temelleri ──────────────────────────────────────────────────
    {
        "id": "py_001", "topic": "Python Temelleri", "difficulty": 1,
        "text": "Python 3'te `type(3/2)` ifadesinin çıktısı nedir?",
        "options": ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'complex'>"],
        "answer_index": 1,
        "explanation": "Python 3'te `/` operatörü her zaman float döndürür."
    },
    {
        "id": "py_002", "topic": "Python Temelleri", "difficulty": 1,
        "text": "Python'da bir fonksiyon tanımlamak için hangi anahtar kelime kullanılır?",
        "options": ["func", "define", "def", "fun"],
        "answer_index": 2,
        "explanation": "`def` anahtar kelimesi bir fonksiyon tanımını başlatır."
    },
    {
        "id": "py_003", "topic": "Python Temelleri", "difficulty": 2,
        "text": "`*args` parametresi bir fonksiyona ne sağlar?",
        "options": [
            "Anahtar kelime argümanlarından oluşan bir sözlük",
            "İstenen sayıda konumsal argüman alabilme",
            "Yalnızca tam sayı argümanları",
            "Tek bir liste argümanı"
        ],
        "answer_index": 1,
        "explanation": "`*args`, fazladan konumsal argümanları bir demet (tuple) içinde toplar."
    },
    {
        "id": "py_004", "topic": "Python Temelleri", "difficulty": 2,
        "text": "Aşağıdakilerden hangisi Python'da değiştirilebilir (mutable) bir veri tipidir?",
        "options": ["str", "tuple", "int", "list"],
        "answer_index": 3,
        "explanation": "Listeler değiştirilebilir; str, tuple ve int değiştirilemez (immutable)."
    },
    {
        "id": "py_005", "topic": "Python Temelleri", "difficulty": 3,
        "text": "`[x**2 for x in range(4) if x % 2 == 0]` ifadesinin çıktısı nedir?",
        "options": ["[1, 9]", "[0, 4]", "[0, 4, 16]", "[0, 2, 4]"],
        "answer_index": 1,
        "explanation": "range(4) içindeki çift sayılar 0 ve 2'dir; kareleri 0 ve 4'tür."
    },

    # ── Veri Yapıları ─────────────────────────────────────────────────────
    {
        "id": "ds_001", "topic": "Veri Yapıları", "difficulty": 1,
        "text": "Bir hash map'te bir elemana erişmenin ortalama zaman karmaşıklığı nedir?",
        "options": ["O(n)", "O(log n)", "O(1)", "O(n²)"],
        "answer_index": 2,
        "explanation": "Hash map'ler, hash fonksiyonu sayesinde ortalama O(1) erişim sağlar."
    },
    {
        "id": "ds_002", "topic": "Veri Yapıları", "difficulty": 2,
        "text": "LIFO (Son Giren İlk Çıkar) prensibini hangi veri yapısı izler?",
        "options": ["Kuyruk", "Yığın (Stack)", "Deque", "Bağlı Liste"],
        "answer_index": 1,
        "explanation": "Son Giren İlk Çıkar (LIFO) prensibi yığın (stack) yapısını tanımlar."
    },
    {
        "id": "ds_003", "topic": "Veri Yapıları", "difficulty": 2,
        "text": "İkili arama ağacında (BST) en küçük eleman nerede bulunur?",
        "options": ["Kök düğümde", "En sağdaki düğümde", "En soldaki düğümde", "Herhangi bir yaprakta"],
        "answer_index": 2,
        "explanation": "BST özelliği: tüm sol alt ağaç düğümleri kök düğümden küçüktür."
    },
    {
        "id": "ds_004", "topic": "Veri Yapıları", "difficulty": 3,
        "text": "QuickSort'un en kötü durum zaman karmaşıklığı nedir?",
        "options": ["O(n log n)", "O(n)", "O(n²)", "O(log n)"],
        "answer_index": 2,
        "explanation": "Pivot her seferinde en küçük/büyük eleman seçilirse QuickSort O(n²)'ye düşer."
    },
    {
        "id": "ds_005", "topic": "Veri Yapıları", "difficulty": 3,
        "text": "BST'nin hangi dolaşım yöntemi elemanları sıralı biçimde verir?",
        "options": ["Ön-sıra (Pre-order)", "Art-sıra (Post-order)", "İç-sıra (In-order)", "Seviye-sıra (Level-order)"],
        "answer_index": 2,
        "explanation": "İç-sıra dolaşımı (sol → kök → sağ) düğümleri artan sırada ziyaret eder."
    },

    # ── Nesne Yönelimli Programlama ────────────────────────────────────────
    {
        "id": "oop_001", "topic": "Nesne Yönelimli Programlama", "difficulty": 1,
        "text": "OOP'ta kapsülleme (encapsulation) nedir?",
        "options": [
            "Bir üst sınıftan metot miras almak",
            "Veri ve bu veri üzerinde çalışan metotları bir arada paketlemek",
            "Aynı ada sahip birden fazla metot tanımlamak",
            "Aynı arayüzü farklı türler üzerinde çalıştırmak"
        ],
        "answer_index": 1,
        "explanation": "Kapsülleme, durum (state) ve davranışı (behaviour) tek bir birim olan sınıf içinde bir araya getirir."
    },
    {
        "id": "oop_002", "topic": "Nesne Yönelimli Programlama", "difficulty": 2,
        "text": "Python'da bir üst sınıftan kalıtım almak için nasıl bir sözdizimi kullanılır?",
        "options": ["implements anahtar kelimesi", "extends anahtar kelimesi", "inherits anahtar kelimesi", "Özel kelime yok — üst sınıf parantez içine yazılır"],
        "answer_index": 3,
        "explanation": "`class Alt(Ust):` — Python parantez kullanır, özel bir anahtar kelime gerekmez."
    },
    {
        "id": "oop_003", "topic": "Nesne Yönelimli Programlama", "difficulty": 2,
        "text": "Aynı metodun farklı nesneler üzerinde farklı davranmasını sağlayan OOP ilkesi hangisidir?",
        "options": ["Kapsülleme", "Soyutlama", "Çok biçimlilik (Polimorfizm)", "Kalıtım"],
        "answer_index": 2,
        "explanation": "Polimorfizm, tek bir arayüzün farklı altta yatan türler üzerinde çalışmasına olanak tanır."
    },
    {
        "id": "oop_004", "topic": "Nesne Yönelimli Programlama", "difficulty": 3,
        "text": "Python'da Metot Çözümleme Sırası (MRO) ne işe yarar?",
        "options": [
            "Fonksiyonların başlangıçta hangi sırayla çalışacağını belirler",
            "Çoklu kalıtımda hangi sınıfın metodunun çağrılacağına karar verir",
            "Sınıf niteliklerini alfabetik sıralar",
            "Çöp toplama (garbage collection) sırasını denetler"
        ],
        "answer_index": 1,
        "explanation": "MRO (C3 doğrusallaştırması), elmas kalıtım hiyerarşisinde hangi metodun önce çağrılacağını tanımlar."
    },

    # ── Algoritmalar ──────────────────────────────────────────────────────
    {
        "id": "algo_001", "topic": "Algoritmalar", "difficulty": 1,
        "text": "Sıralı bir dizide ikili aramanın (binary search) zaman karmaşıklığı nedir?",
        "options": ["O(n)", "O(n²)", "O(log n)", "O(1)"],
        "answer_index": 2,
        "explanation": "İkili arama her adımda arama alanını yarıya indirir → O(log n)."
    },
    {
        "id": "algo_002", "topic": "Algoritmalar", "difficulty": 2,
        "text": "Ağırlıksız bir grafta en kısa yolu bulmayı garanti eden algoritma hangisidir?",
        "options": ["DFS", "BFS", "Dijkstra", "A*"],
        "answer_index": 1,
        "explanation": "BFS katman katman keşfeder ve minimum kenar sayısını garanti eder."
    },
    {
        "id": "algo_003", "topic": "Algoritmalar", "difficulty": 2,
        "text": "Dinamik programlama (DP) öncelikli olarak hangi tekniğe dayanır?",
        "options": ["Hafızasız özyineleme", "Açgözlü seçimler", "Ezber (memoization) / örtüşen alt problemler", "Rastgele pivot seçimi"],
        "answer_index": 2,
        "explanation": "DP, gereksiz tekrarı önlemek için örtüşen alt problemlerin çözümlerini saklar."
    },
    {
        "id": "algo_004", "topic": "Algoritmalar", "difficulty": 3,
        "text": "Birleştirme sıralamasının (Merge Sort) alan karmaşıklığı nedir?",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
        "answer_index": 2,
        "explanation": "Merge Sort, birleştirme adımı için O(n) yardımcı alan gerektirir."
    },

    # ── Veritabanları ─────────────────────────────────────────────────────
    {
        "id": "db_001", "topic": "Veritabanları", "difficulty": 1,
        "text": "SQL'in açılımı nedir?",
        "options": [
            "Simple Query Language",
            "Structured Query Language",
            "Standard Query Logic",
            "Sequential Query Layer"
        ],
        "answer_index": 1,
        "explanation": "SQL = Structured Query Language (Yapılandırılmış Sorgulama Dili)."
    },
    {
        "id": "db_002", "topic": "Veritabanları", "difficulty": 2,
        "text": "Kısmi bağımlılıkları ortadan kaldıran normal form hangisidir?",
        "options": ["1NF", "2NF", "3NF", "BCNF"],
        "answer_index": 1,
        "explanation": "2NF, bileşik birincil anahtara yönelik kısmi bağımlılıkları kaldırır."
    },
    {
        "id": "db_003", "topic": "Veritabanları", "difficulty": 3,
        "text": "ACID özelliğindeki 'İzolasyon' (Isolation) ne garantiler?",
        "options": [
            "Veriler commit sonrasında hiçbir zaman kaybolmaz",
            "Eş zamanlı işlemler birbirinin ara durumlarını görmez",
            "Bir işlemdeki tüm operasyonlar ya hep başarılı olur ya da hiç olmaz",
            "Her işlem sonrasında veritabanı geçerli bir durumda kalır"
        ],
        "answer_index": 1,
        "explanation": "İzolasyon, tamamlanmamış değişiklikleri diğer eş zamanlı işlemlerden gizler."
    },
]
