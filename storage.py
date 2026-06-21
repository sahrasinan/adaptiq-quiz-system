"""
storage.py — JSON tabanli kalici depolama katmani.

Tum dosya G/C islemleri DataHandler uzerinden yurutulur; boylece
uygulamanin geri kalani dogrudan dosya sistemine erismez.
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
    JSON okuma/yazma icin ince bir sarmalayici:
    - Atomik yazma (once .tmp'ye yaz, sonra yeniden adlandir)
    - Her yazmadan once otomatik yedekleme
    - Yapilandirilmis hata yonetimi
    """

    def __init__(self) -> None:
        DATA_DIR.mkdir(exist_ok=True)
        BACKUP_DIR.mkdir(exist_ok=True)
        self._sorulari_yoksa_ekle()

    # -- Dusuk seviye yardimcilar ---------------------------------------------

    @staticmethod
    def _json_oku(path: Path) -> dict | list:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            raise FileNotFoundError(f"Veri dosyasi bulunamadi: {path}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path} icindeki JSON bozuk: {exc}") from exc

    @staticmethod
    def _json_yaz(path: Path, data: dict | list) -> None:
        """Atomik yazma: once .tmp'ye yaz, sonra asil yere tasi."""
        tmp = path.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            shutil.move(str(tmp), str(path))
        except OSError as exc:
            tmp.unlink(missing_ok=True)
            raise OSError(f"{path} yazilamadi: {exc}") from exc

    def _yedekle(self, path: Path) -> None:
        if not path.exists():
            return
        ts   = int(time.time())
        dest = BACKUP_DIR / f"{path.stem}_{ts}{path.suffix}"
        try:
            shutil.copy2(str(path), str(dest))
        except OSError:
            pass  # Yedekleme hatasi kritik degil

    # ── Sorular ───────────────────────────────────────────────────────────

    def load_questions(self) -> list[Question]:
        raw = self._json_oku(QUESTIONS_FILE)
        questions = []
        for item in raw:
            try:
                questions.append(Question.from_dict(item))
            except (KeyError, ValueError) as exc:
                print(f"[DataHandler] Bozuk soru atlandi: {exc}")
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
            raise ValueError(f"'{username}' kullanici adi zaten mevcut.")
        profile = StudentProfile(username=username, display_name=display_name)
        self.save_profile(profile)
        return profile

    # -- Baslangic verisi -------------------------------------------------------

    def _sorulari_yoksa_ekle(self) -> None:
        if QUESTIONS_FILE.exists():
            return
        self._json_yaz(QUESTIONS_FILE, _BASLANGIC_SORULARI)


# ---------------------------------------------------------------------------
# Baslangic soru bankasi (questions.json yoksa ilk calistirmada olusturulur)
# ---------------------------------------------------------------------------

_BASLANGIC_SORULARI: list[dict] = [

    # =========================================================================
    # KONU 1: Nesne Yonelimli Programlama (10 soru)
    # =========================================================================
    {
        "id": "oop_001", "topic": "Nesne Yonelimli Programlama", "difficulty": 1,
        "text": "Kapsulleme (encapsulation) kavrami OOP'ta neyi ifade eder?",
        "options": [
            "Bir ust siniftan metot miras almak",
            "Veri ve bu veri uzerinde calisan metotlari bir sinif icerisinde bir arada tutmak",
            "Ayni ada sahip birden fazla metot tanimlamak",
            "Ayni arayuzu farkli turler uzerinde calistirmak"
        ],
        "answer_index": 1,
        "explanation": "Kapsulleme, durum ve davranisi tek bir birim olan sinif icinde bir araya getirir."
    },
    {
        "id": "oop_002", "topic": "Nesne Yonelimli Programlama", "difficulty": 1,
        "text": "Python'da bir sinif tanimlamak icin hangi anahtar kelime kullanilir?",
        "options": ["object", "class", "struct", "type"],
        "answer_index": 1,
        "explanation": "`class` anahtar kelimesi Python'da sinif tanimlamak icin kullanilir."
    },
    {
        "id": "oop_003", "topic": "Nesne Yonelimli Programlama", "difficulty": 1,
        "text": "Python'da bir sinifin yapici (constructor) metodunun adi nedir?",
        "options": ["__start__", "__init__", "__new__", "__create__"],
        "answer_index": 1,
        "explanation": "`__init__` metodu, bir nesne olusturulurken otomatik olarak cagrilan yapici metoddur."
    },
    {
        "id": "oop_004", "topic": "Nesne Yonelimli Programlama", "difficulty": 2,
        "text": "Python'da ust sinifin metodunu alt siniftan cagirmak icin hangi yaklasim kullanilir?",
        "options": ["parent.method()", "super().method()", "base.method()", "upper.method()"],
        "answer_index": 1,
        "explanation": "`super()` fonksiyonu, ust sinifin metoduna erisim saglar."
    },
    {
        "id": "oop_005", "topic": "Nesne Yonelimli Programlama", "difficulty": 2,
        "text": "Ayni metodun farkli nesneler uzerinde farkli davranmasini saglayan OOP ilkesi hangisidir?",
        "options": ["Kapsulleme", "Soyutlama", "Cok bicimlilik", "Kalitim"],
        "answer_index": 2,
        "explanation": "Cok bicimlilik (polimorfizm), tek bir arayuzun farkli turler uzerinde calisimasina olanak tanir."
    },
    {
        "id": "oop_006", "topic": "Nesne Yonelimli Programlama", "difficulty": 2,
        "text": "Python'da `@staticmethod` ile tanimlanan bir metodun ozelligi nedir?",
        "options": [
            "Yalnizca sinif niteliklere erisebilir",
            "Sinif veya ornek referansi almaz, bagimsiz calisir",
            "Yalnizca alt siniflardan cagrilabilir",
            "Her cagrildiginda yeni bir nesne olusturur"
        ],
        "answer_index": 1,
        "explanation": "Statik metodlar `self` veya `cls` parametresi almaz; sinif kapsaminda bagimsiz fonksiyonlardir."
    },
    {
        "id": "oop_007", "topic": "Nesne Yonelimli Programlama", "difficulty": 2,
        "text": "Python'da bir niteligi 'korunan' (protected) yapmak icin ne kullanilir?",
        "options": ["protected:", "Tek alt cizgi on eki (_)", "Cift alt cizgi on eki (__)", "#"],
        "answer_index": 1,
        "explanation": "Tek alt cizgi on eki (_attr) o niteligi korunan olarak isaretler; bu bir konvansiyondur, dil tarafindan zorunlu tutulmaz."
    },
    {
        "id": "oop_008", "topic": "Nesne Yonelimli Programlama", "difficulty": 3,
        "text": "Python'da Metot Cozumleme Sirasi (MRO) ne ise yarar?",
        "options": [
            "Fonksiyonlarin baslangiCta hangi sirayla calisacagini belirler",
            "Coklu kalitimda hangi sinifin metodunun cagrIlacagina karar verir",
            "Sinif niteliklerini alfabetik siralar",
            "Cop toplama sIrasini denetler"
        ],
        "answer_index": 1,
        "explanation": "MRO (C3 dogrusalLastirmasi), elmas kalitim hiyerarsisinde hangi metodun once cagrIlacagini tanimlar."
    },
    {
        "id": "oop_009", "topic": "Nesne Yonelimli Programlama", "difficulty": 3,
        "text": "`__str__` ve `__repr__` metodlari arasindaki temel fark nedir?",
        "options": [
            "Ikisi de ayni isi yapar, fark yoktur",
            "`__str__` kullanici icin okunabilir metin, `__repr__` gelistirici icin tekrar olusturulabilir temsil saglar",
            "`__repr__` yalnizca hata ayiklama icin kullanilir, `__str__` kullanilmaz",
            "`__str__` tamsayi dondurur, `__repr__` metin dondurur"
        ],
        "answer_index": 1,
        "explanation": "`__str__` son kullanici icin okunabilir bir metin dondururken, `__repr__` nesneyi yeniden olusturmaya yeterli teknik temsili saglar."
    },
    {
        "id": "oop_010", "topic": "Nesne Yonelimli Programlama", "difficulty": 3,
        "text": "Soyut temel sinif (Abstract Base Class) olusturmak icin Python'da hangi modul kullanilir?",
        "options": ["abstract", "abc", "interface", "base"],
        "answer_index": 1,
        "explanation": "`abc` modulu `ABC` sinifini ve `@abstractmethod` dekoratoru saglar."
    },

    # =========================================================================
    # KONU 2: Veri Yapilari (10 soru)
    # =========================================================================
    {
        "id": "ds_001", "topic": "Veri Yapilari", "difficulty": 1,
        "text": "Bir hash map'te bir elemana erismenin ortalama zaman karmasikligi nedir?",
        "options": ["O(n)", "O(log n)", "O(1)", "O(n^2)"],
        "answer_index": 2,
        "explanation": "Hash map'ler, hash fonksiyonu sayesinde ortalama O(1) erisim saglar."
    },
    {
        "id": "ds_002", "topic": "Veri Yapilari", "difficulty": 1,
        "text": "LIFO (Son Giren Ilk Cikar) prensibini hangi veri yapisi izler?",
        "options": ["Kuyruk", "Yigin (Stack)", "Deque", "Bagli Liste"],
        "answer_index": 1,
        "explanation": "Son Giren Ilk Cikar (LIFO) prensibi yigin yapIsini tanimlar."
    },
    {
        "id": "ds_003", "topic": "Veri Yapilari", "difficulty": 1,
        "text": "Python'da liste sonuna eleman eklemek icin hangi metot kullanilir?",
        "options": ["add()", "insert()", "append()", "push()"],
        "answer_index": 2,
        "explanation": "`append()` metodu listeye sona eleman ekler ve O(1) zaman karmasikligina sahiptir."
    },
    {
        "id": "ds_004", "topic": "Veri Yapilari", "difficulty": 2,
        "text": "Ikili arama agacinda (BST) en kucuk eleman nerede bulunur?",
        "options": ["Kok dugumde", "En sagdaki dugumde", "En soldaki dugumde", "Herhangi bir yaprakta"],
        "answer_index": 2,
        "explanation": "BST ozelligi: tum sol alt agac dugumleri kok dugumden kucuktur."
    },
    {
        "id": "ds_005", "topic": "Veri Yapilari", "difficulty": 2,
        "text": "Python'da `dict` veri yapisinda bir anahtara erismenin zaman karmasikligi nedir?",
        "options": ["O(n)", "O(log n)", "O(1)", "O(n^2)"],
        "answer_index": 2,
        "explanation": "Python sozlukleri hash tablosu tabanlidir ve ortalama O(1) erisim saglar."
    },
    {
        "id": "ds_006", "topic": "Veri Yapilari", "difficulty": 2,
        "text": "Kuyruk (Queue) veri yapisi hangi prensibi izler?",
        "options": ["LIFO", "FIFO", "FILO", "LILO"],
        "answer_index": 1,
        "explanation": "FIFO (First In First Out - Ilk Giren Ilk Cikar) prensibi kuyruk yapIsini tanimlar."
    },
    {
        "id": "ds_007", "topic": "Veri Yapilari", "difficulty": 2,
        "text": "QuickSort'un ortalama durum zaman karmasikligi nedir?",
        "options": ["O(n^2)", "O(n log n)", "O(n)", "O(log n)"],
        "answer_index": 1,
        "explanation": "QuickSort ortalama durumda O(n log n) karmasikligina sahiptir."
    },
    {
        "id": "ds_008", "topic": "Veri Yapilari", "difficulty": 3,
        "text": "QuickSort'un en kotu durum zaman karmasikligi nedir?",
        "options": ["O(n log n)", "O(n)", "O(n^2)", "O(log n)"],
        "answer_index": 2,
        "explanation": "Pivot her seferinde en kucuk/buyuk eleman secilirse QuickSort O(n^2)'ye duzer."
    },
    {
        "id": "ds_009", "topic": "Veri Yapilari", "difficulty": 3,
        "text": "BST'nin hangi dolasim yontemi elemanlari sirali bicimde verir?",
        "options": ["On-sira (Pre-order)", "Art-sira (Post-order)", "Ic-sira (In-order)", "Seviye-sira (Level-order)"],
        "answer_index": 2,
        "explanation": "Ic-sira dolasimi (sol - kok - sag) dugumleri artan sirada ziyaret eder."
    },
    {
        "id": "ds_010", "topic": "Veri Yapilari", "difficulty": 3,
        "text": "Birlesik bulma (Union-Find) veri yapisi esas olarak hangi problemi cozmek icin kullanilir?",
        "options": [
            "En kisa yol bulmak",
            "Ayrik kumeleri takip etmek ve birlestirmek",
            "Siralama yapmak",
            "Arama agaci dengelemek"
        ],
        "answer_index": 1,
        "explanation": "Union-Find, ayrik kumeleri verimli sekilde takip etmek ve birlestirmek icin kullanilir; Kruskal algoritmasi bunun klasik bir uygulamasidir."
    },

    # =========================================================================
    # KONU 3: Fonksiyonlar (10 soru)
    # =========================================================================
    {
        "id": "fn_001", "topic": "Fonksiyonlar", "difficulty": 1,
        "text": "Python'da bir fonksiyon tanimlamak icin hangi anahtar kelime kullanilir?",
        "options": ["func", "define", "def", "fun"],
        "answer_index": 2,
        "explanation": "`def` anahtar kelimesi Python'da fonksiyon tanimlamak icin kullanilir."
    },
    {
        "id": "fn_002", "topic": "Fonksiyonlar", "difficulty": 1,
        "text": "Asagidaki Python kodunun ciktisi nedir?  def f(x): return x * 2  print(f(3))",
        "options": ["3", "6", "23", "Hata"],
        "answer_index": 1,
        "explanation": "f(3) = 3 * 2 = 6 degerini dondurur."
    },
    {
        "id": "fn_003", "topic": "Fonksiyonlar", "difficulty": 1,
        "text": "Python'da isimsiz (lambda) fonksiyon nasil tanimlanir?",
        "options": [
            "def isimsiz(x): return x",
            "lambda x: x",
            "func(x) => x",
            "anonymous(x): x"
        ],
        "answer_index": 1,
        "explanation": "`lambda` anahtar kelimesi ile tek satirlik isimsiz fonksiyonlar olusturulur."
    },
    {
        "id": "fn_004", "topic": "Fonksiyonlar", "difficulty": 2,
        "text": "`*args` parametresi bir fonksiyona ne saglar?",
        "options": [
            "Anahtar kelime argumanlari icin bir sozluk",
            "Istenen sayida konumsal argumanlar",
            "Yalnizca tam sayi argumanlar",
            "Tek bir liste argumani"
        ],
        "answer_index": 1,
        "explanation": "`*args`, fazladan konumsal argumanlari bir demet (tuple) icinde toplar."
    },
    {
        "id": "fn_005", "topic": "Fonksiyonlar", "difficulty": 2,
        "text": "`**kwargs` parametresi ne ise yarar?",
        "options": [
            "Birden fazla konumsal argumanat kabul eder",
            "Isimlendirilmis (keyword) argumanlari sozluk olarak toplar",
            "Yalnizca varsayilan degerli parametreler tanimlar",
            "Fonksiyonu ozyinelemeli yapar"
        ],
        "answer_index": 1,
        "explanation": "`**kwargs`, isimsiz anahtar kelime argumanlari bir sozluk olarak toplar."
    },
    {
        "id": "fn_006", "topic": "Fonksiyonlar", "difficulty": 2,
        "text": "Bir fonksiyonun icindeki yerel degisken, dis kapsamdaki ayni adli degiskeni etkiler mi?",
        "options": [
            "Evet, her zaman etkiler",
            "Hayir, yerel kapsam dis kapsami etkilemez",
            "Yalnizca `return` kullanilirsa etkiler",
            "Yalnizca `global` anahtar kelimesiyle etkiler"
        ],
        "answer_index": 1,
        "explanation": "Python'da fonksiyon icindeki atamalar yerel kapsam olusturur; `global` kullanilmadikca dis degiskeni degistirmez."
    },
    {
        "id": "fn_007", "topic": "Fonksiyonlar", "difficulty": 2,
        "text": "Python'da dekorator (@decorator) ne ise yarar?",
        "options": [
            "Sinif niteliklerini gizler",
            "Bir fonksiyonu baska bir fonksiyon ile sarmalayarak davranis ekler",
            "Degiskenlere tip bilgisi atar",
            "Kodu derleme zamaninda optimize eder"
        ],
        "answer_index": 1,
        "explanation": "Dekoratorler, bir fonksiyonu sarmalayan ve orijinal kodu degistirmeden ekstra davranis ekleyen ust-duzey fonksiyonlardir."
    },
    {
        "id": "fn_008", "topic": "Fonksiyonlar", "difficulty": 3,
        "text": "Python'da kapanim (closure) nedir?",
        "options": [
            "Tum degiskenleri otomatik silen bir fonksiyon",
            "Kendi kapsamindan sonra bile disardaki degiskenlere erisebilen ic ice tanimlanmis fonksiyon",
            "Yalnizca sinif icerisinde calisabilen metot",
            "Birden fazla deger donduren fonksiyon"
        ],
        "answer_index": 1,
        "explanation": "Kapanim, ic fonksiyonun dis fonksiyonun yerel degiskenlerini hafizada tutmasina olanak saglar."
    },
    {
        "id": "fn_009", "topic": "Fonksiyonlar", "difficulty": 3,
        "text": "`map(func, liste)` fonksiyonunun donus degeri Python 3'te nedir?",
        "options": ["Liste", "Demet", "Map nesnesi (iterator)", "Sozluk"],
        "answer_index": 2,
        "explanation": "Python 3'te `map()` tembel bir iterator olan map nesnesi dondurur; `list()` ile donusturmek gerekebilir."
    },
    {
        "id": "fn_010", "topic": "Fonksiyonlar", "difficulty": 3,
        "text": "Asagidaki kodun ciktisi nedir?  funcs = [lambda x: x+i for i in range(3)]  print(funcs[0](0))",
        "options": ["0", "1", "2", "Hata"],
        "answer_index": 2,
        "explanation": "Lambda'lar `i` degiskenini icerir, listeye ekleme anindaki degerini degil. Dongu bittikten sonra `i=2` olur, bu nedenle tum lambdalar 2 kullanir."
    },

    # =========================================================================
    # KONU 4: Donguler (10 soru)
    # =========================================================================
    {
        "id": "lp_001", "topic": "Donguler", "difficulty": 1,
        "text": "`range(5)` ifadesi hangi degerleri uretir?",
        "options": ["1, 2, 3, 4, 5", "0, 1, 2, 3, 4", "0, 1, 2, 3, 4, 5", "1, 2, 3, 4"],
        "answer_index": 1,
        "explanation": "`range(5)`, 0'dan baslayip 5'e kadar (5 dahil degil) tam sayilar uretir."
    },
    {
        "id": "lp_002", "topic": "Donguler", "difficulty": 1,
        "text": "Python'da `while` dongusunde sonsuz dongu olusturmak icin hangi yapi kullanilir?",
        "options": ["while True:", "while 1 == 1:", "loop forever:", "for ever:"],
        "answer_index": 0,
        "explanation": "`while True:` ifadesi Python'da sonsuz dongu olusturmanin standart yontemidir."
    },
    {
        "id": "lp_003", "topic": "Donguler", "difficulty": 1,
        "text": "Asagidaki kodun ciktisi nedir?  for i in range(3): print(i)",
        "options": ["1 2 3", "0 1 2", "0 1 2 3", "1 2"],
        "answer_index": 1,
        "explanation": "`range(3)` 0, 1 ve 2 degerlerini uretir."
    },
    {
        "id": "lp_004", "topic": "Donguler", "difficulty": 2,
        "text": "`break` ifadesi dongude ne ise yarar?",
        "options": [
            "Mevcut iterasyonu atlar, dongue devam eder",
            "Donguyu tamamen sonlandirir",
            "Donguyu yeniden baslatir",
            "Bir sonraki iterasyona gecmeden bekler"
        ],
        "answer_index": 1,
        "explanation": "`break` donguyu tamamen sonlandirir ve program dongu sonrasindaki satirdan devam eder."
    },
    {
        "id": "lp_005", "topic": "Donguler", "difficulty": 2,
        "text": "`continue` ifadesi dongude ne ise yarar?",
        "options": [
            "Donguyu sonlandirir",
            "Mevcut iterasyonun kalanini atlar ve bir sonraki iterasyona gecer",
            "Dongu sayacini sifirlar",
            "Donguyu duraklatir"
        ],
        "answer_index": 1,
        "explanation": "`continue` mevcut iterasyonun geri kalanini atlar ve dongu bir sonraki iterasyonla devam eder."
    },
    {
        "id": "lp_006", "topic": "Donguler", "difficulty": 2,
        "text": "Python'da `enumerate()` fonksiyonu ne saglar?",
        "options": [
            "Bir listeyi siralar",
            "Hem indeks hem de deger donduren bir iterator saglar",
            "Yalnizca indeksleri listeler",
            "Bir listeyi tersine cevir"
        ],
        "answer_index": 1,
        "explanation": "`enumerate()` her iterasyonda (indeks, deger) ikili dondurur; ayri sayac degiskenine gerek kalmaz."
    },
    {
        "id": "lp_007", "topic": "Donguler", "difficulty": 2,
        "text": "Asagidaki liste ureteci (list comprehension) ne uretir?  [x for x in range(10) if x % 2 == 0]",
        "options": ["[1,3,5,7,9]", "[0,2,4,6,8]", "[2,4,6,8,10]", "[0,1,2,3,4]"],
        "answer_index": 1,
        "explanation": "0-9 arasindaki cift sayilar (2'ye tam bolunenler): 0, 2, 4, 6, 8."
    },
    {
        "id": "lp_008", "topic": "Donguler", "difficulty": 3,
        "text": "`for` dongusunde `else` blogu ne zaman calisir?",
        "options": [
            "Dongude hata olusursa",
            "Dongu `break` kullanilmadan tamamlaninca",
            "Dongunun ilk iterasyonundan once",
            "Dongu bos bir iteratorde baslayinca"
        ],
        "answer_index": 1,
        "explanation": "`for...else` yapisinda `else` blogu yalnizca dongu `break` ile kesilmeden tamamlandiginda calisir."
    },
    {
        "id": "lp_009", "topic": "Donguler", "difficulty": 3,
        "text": "Asagidaki inic kodun ciktisi nedir?  i = 5  while i > 0:    i -= 2  print(i)",
        "options": ["0", "-1", "1", "Sonsuz dongu"],
        "answer_index": 1,
        "explanation": "i: 5 -> 3 -> 1 -> -1. Sart i>0 oldugu icin i=-1 oldugunda dongu biter. Cikti: -1."
    },
    {
        "id": "lp_010", "topic": "Donguler", "difficulty": 3,
        "text": "Python'da `zip()` fonksiyonu ne yapar?",
        "options": [
            "Bir listedeki elemanlari sikiStirir",
            "Birden fazla iteratoru paralel olarak birlestirir",
            "Yalnizca iki listeyi sirasina gore karsilastirir",
            "Listeler arasindaki farki dondurur"
        ],
        "answer_index": 1,
        "explanation": "`zip()` birden fazla iteratorun elemanlarini tuple olarak eslestirerek paralel iterasyon saglar."
    },

    # =========================================================================
    # KONU 5: Hata Yonetimi (10 soru)
    # =========================================================================
    {
        "id": "err_001", "topic": "Hata Yonetimi", "difficulty": 1,
        "text": "Python'da hata yakalamak icin hangi yapi kullanilir?",
        "options": ["try/catch", "try/except", "catch/handle", "error/rescue"],
        "answer_index": 1,
        "explanation": "Python'da `try/except` blogu hata yakalamak icin kullanilir; diger dillerdeki `try/catch` yapisinin karsiligi budur."
    },
    {
        "id": "err_002", "topic": "Hata Yonetimi", "difficulty": 1,
        "text": "Asagidaki kodda hangi hata turu olusur?  print(5 / 0)",
        "options": ["ValueError", "TypeError", "ZeroDivisionError", "ArithmeticError"],
        "answer_index": 2,
        "explanation": "Sifira bolme isleminde Python `ZeroDivisionError` firlatir."
    },
    {
        "id": "err_003", "topic": "Hata Yonetimi", "difficulty": 1,
        "text": "Python'da elle hata (istisna) firlatmak icin hangi anahtar kelime kullanilir?",
        "options": ["throw", "raise", "error", "except"],
        "answer_index": 1,
        "explanation": "`raise` anahtar kelimesi Python'da istisna fIrlatmak icin kullanilir."
    },
    {
        "id": "err_004", "topic": "Hata Yonetimi", "difficulty": 2,
        "text": "`finally` blogu ne zaman calisir?",
        "options": [
            "Yalnizca hata olursa",
            "Yalnizca hata olmazsa",
            "Hata olsun ya da olmasin her zaman",
            "Yalnizca `except` blogu calismayinca"
        ],
        "answer_index": 2,
        "explanation": "`finally` blogu, hata olup olmadIgIndan bagimsiz olarak her zaman calisir; kaynak temizlemek icin idealdir."
    },
    {
        "id": "err_005", "topic": "Hata Yonetimi", "difficulty": 2,
        "text": "Hata mesajina erisebilmek icin `except` ifadesi nasil yazilir?",
        "options": [
            "except Error:",
            "except Exception as e:",
            "except (e):",
            "catch Exception e:"
        ],
        "answer_index": 1,
        "explanation": "`except Exception as e:` yapiSi, yakalanan istisnayi `e` degiskenine atarak mesajina erisimi saglar."
    },
    {
        "id": "err_006", "topic": "Hata Yonetimi", "difficulty": 2,
        "text": "Python'da ozel bir istisna sinifi olusturmak icin hangi siniftan miras alinmalidir?",
        "options": ["BaseError", "Error", "Exception", "RuntimeError"],
        "answer_index": 2,
        "explanation": "Ozel istisnalar `Exception` sinifIndan (ya da onun alt sinifindan) turetilmelidir."
    },
    {
        "id": "err_007", "topic": "Hata Yonetimi", "difficulty": 2,
        "text": "Bir listede olmayan bir indekse erismeye calisinca Python hangi hatayi firlatir?",
        "options": ["KeyError", "IndexError", "ValueError", "TypeError"],
        "answer_index": 1,
        "explanation": "`IndexError`, bir dizinin siniri disina cikildIgInda olusur."
    },
    {
        "id": "err_008", "topic": "Hata Yonetimi", "difficulty": 3,
        "text": "`try/except/else` yapisinda `else` blogu ne zaman calisir?",
        "options": [
            "Her zaman",
            "Yalnizca `try` blogu istisna firlatmadan tamamlaninca",
            "Yalnizca `except` blogu istisna yakalainca",
            "Her ikisi de hata verince"
        ],
        "answer_index": 1,
        "explanation": "`else` blogu, `try` blogu hicbir istisna firlatmadan basarIyla tamamlandiginda calisir."
    },
    {
        "id": "err_009", "topic": "Hata Yonetimi", "difficulty": 3,
        "text": "Python'da `context manager` (`with` ifadesi) hata yonetimiyle nasil iliskilidir?",
        "options": [
            "Hata yonetimiyle iliskisi yoktur",
            "Hata olsun ya da olmasin `__exit__` metodunu cagirarak kaynak temizligini garantiler",
            "Yalnizca dosya hatalarIni yakalar",
            "Tum hatalari sessizce yok sayar"
        ],
        "answer_index": 1,
        "explanation": "`with` blogu `__exit__`'i garantili cagIrIr; bu, `finally` gibi davranarak istisna durumlarInda bile kaynak serbest bIrakmayi saglar."
    },
    {
        "id": "err_010", "topic": "Hata Yonetimi", "difficulty": 3,
        "text": "Asagidaki kodun ciktisi nedir?  try:    x = int('abc')  except ValueError:    print('A')  except Exception:    print('B')  else:    print('C')",
        "options": ["A", "B", "C", "Hicbir sey"],
        "answer_index": 0,
        "explanation": "`int('abc')` bir `ValueError` firlatir. Bu `except ValueError` blogu tarafindan yakalanir ve 'A' basilir."
    },
]
