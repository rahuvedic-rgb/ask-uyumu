import os
import json
import math
from datetime import datetime, timedelta

# Skyfield ve Lisanssız Matematiksel Kütüphaneler
from skyfield.api import load, Topos
import pytz

# TimezoneFinder Güvenli Yükleme
try:
    from timezonefinder import TimezoneFinder
    tf = TimezoneFinder()
except Exception:
    tf = None

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

if platform not in ('android', 'ios'):
    Window.size = (360, 640)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "naksatra_cache.json")
GITHUB_JSON_URL = "https://raw.githubusercontent.com/rahuvedic-rgb/ask-uyumu/main/sukur_naksatra_uyum_data_3.json"

# Skyfield Ephemeris Verisinin Yüklenmesi
ts = load.timescale()
eph = None
try:
    load_dir = load.directory = BASE_DIR
    eph = load('de421.bsp')
    print("[SKYFIELD SUCCESS] de421.bsp başarıyla yüklendi.")
except Exception as e:
    print(f"[SKYFIELD HATA] de421.bsp yüklenemedi: {e}")

REHBER_VE_YASAL_UYARI_METNI = """==================================
   AŞK UYUMU ANALİZİ - REHBER
==================================

1. UYGULAMA NASIL KULLANILIR?
----------------------------------
* "SEN" ve "O" bölümlerinde doğum günü, ayı, yılı, saati, dakikası, AM/PM, Ülke ve Şehir bilgilerini eksiksiz girin.
* "HESAPLA" butonuna bastığınızda Skyfield motoru ve Lahiri Ayanamsa hassasiyetiyle Vedik Astroloji haritanıza göre Nakşatra (Ay Burcu) konumlarınız belirlenir.

2. OTOMATİK ZAMAN DİLİMİ VE SAAT (AM/PM)
----------------------------------
* AM (Gece / Sabah): Gece yarısı 12:00'den öğlen 11:59'a kadar olan zamandır. (Örn: Sabah 09:00 = 09:00 AM)
* PM (Öğle / Akşam): Öğlen 12:00'den gece 11:59'a kadar olan zamandır. (Örn: Akşam 21:00 = 09:00 PM)
* Seçtiğiniz şehir ve doğum tarihine ait zaman dilimi ile Yaz/Kış saati (DST) uygulaması arka planda otomatik hesaplanır.

3. BAKIŞ AÇISI UYARISI ("SEN" vs "O")
----------------------------------
* "SEN" bölümüne kendi bilgilerinizi yazdığınızda analiz SİZİN BAKIŞ AÇINIZA göre yapılır.
* "SEN" bölümüne partnerinizin bilgilerini yazdığınızda analiz ONUN BAKIŞ AÇINIZA göre yapılır.
* Derinlemesine kavrayış için sorgulamayı bilgileri yer değiştirerek tekrarlamanız tavsiye edilir.

4. UYUM ORANI SKALASI (%0 - %91)
----------------------------------
* %0 - %33  : Karmik / Zorlu / Mücadeleli Uyum
* %34 - %66 : Dengeli / Esnek Uyum
* %67 - %91 : Mükemmel / Ruh Eşi Bağı

5. YASAL VE TEKNİK UYARI
----------------------------------
* Bu uygulamadaki analizler ve uyum oranları, Vedik astrolojinin 27 Nakşatra sistemine ait mizaç parametreleri (Yoni, Gana, Nadi, Tara) esas alınarak hazırlanmış genel bir psikolojik rehber niteliğindedir.
* Bu sonuçlar tıbbi, hukuki veya kesin psikolojik teşhis içermez; bireysel harita analizi için profesyonel bir Vedik astroloji uzmanından danışmanlık alabilirsiniz.
"""

def rehber_popup_goster(instance=None):
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    scroll = ScrollView(size_hint=(1, 0.85))
    text_label = Label(
        text=REHBER_VE_YASAL_UYARI_METNI,
        font_size='12sp',
        size_hint_y=None,
        halign='left',
        valign='top'
    )
    text_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
    text_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
    scroll.add_widget(text_label)
    
    btn_kapat = Button(
        text="ANLADIM / KAPAT", 
        size_hint=(1, 0.15),
        background_color=(0.75, 0.22, 0.17, 1),
        bold=True
    )
    content.add_widget(scroll)
    content.add_widget(btn_kapat)
    
    popup = Popup(
        title="Uygulama Rehberi & Yasal Uyarı",
        content=content,
        size_hint=(0.88, 0.82),
        auto_dismiss=False
    )
    btn_kapat.bind(on_release=popup.dismiss)
    popup.open()

LOKASYON_VERISI = {
    "Türkiye": {
        "Ankara": {"lat": 39.93, "lon": 32.85},
        "İstanbul": {"lat": 41.00, "lon": 28.97},
        "İzmir": {"lat": 38.42, "lon": 27.14},
        "Bursa": {"lat": 40.18, "lon": 29.06},
        "Antalya": {"lat": 36.89, "lon": 30.70},
        "Adana": {"lat": 37.00, "lon": 35.32},
        "Gaziantep": {"lat": 37.06, "lon": 37.38},
        "Konya": {"lat": 37.87, "lon": 32.48},
        "Trabzon": {"lat": 41.00, "lon": 39.71},
        "Şanlıurfa": {"lat": 37.16, "lon": 38.79},
        "Hatay": {"lat": 36.20, "lon": 36.16}
    },
    "İspanya": {
        "Madrid": {"lat": 40.41, "lon": -3.70},
        "Barselona": {"lat": 41.38, "lon": 2.17},
        "Sevilla": {"lat": 37.38, "lon": -5.98},
        "Valensiya": {"lat": 39.46, "lon": -0.37}
    },
    "İtalya": {
        "Roma": {"lat": 41.90, "lon": 12.49},
        "Milano": {"lat": 45.46, "lon": 9.19},
        "Venedik": {"lat": 45.44, "lon": 12.31},
        "Floransa": {"lat": 43.76, "lon": 11.25},
        "Napoli": {"lat": 40.85, "lon": 14.26}
    },
    "Rusya": {
        "Moskova": {"lat": 55.75, "lon": 37.61},
        "Sankt-Peterburg": {"lat": 59.93, "lon": 30.33},
        "Kazan": {"lat": 55.83, "lon": 49.06},
        "Soçi": {"lat": 43.60, "lon": 39.73}
    },
    "Fransa": {
        "Paris": {"lat": 48.85, "lon": 2.35},
        "Marsilya": {"lat": 43.29, "lon": 5.36},
        "Lyon": {"lat": 45.76, "lon": 4.83}
    },
    "Almanya": {
        "Berlin": {"lat": 52.52, "lon": 13.40},
        "Münih": {"lat": 48.13, "lon": 11.58},
        "Frankfurt": {"lat": 50.11, "lon": 8.68}
    },
    "İngiltere": {
        "Londra": {"lat": 51.50, "lon": -0.12},
        "Manchester": {"lat": 53.48, "lon": -2.24}
    },
    "Hollanda": {
        "Amsterdam": {"lat": 52.36, "lon": 4.90},
        "Rotterdam": {"lat": 51.92, "lon": 4.47}
    },
    "Yunanistan": {
        "Atina": {"lat": 37.98, "lon": 23.72},
        "Selanik": {"lat": 40.64, "lon": 22.94}
    },
    "Suriye": {
        "Şam (Damascus)": {"lat": 33.51, "lon": 36.27},
        "Halep": {"lat": 36.20, "lon": 37.13},
        "Humus": {"lat": 34.73, "lon": 36.71},
        "Laziye": {"lat": 35.53, "lon": 35.78}
    },
    "Irak": {
        "Bağdat": {"lat": 33.31, "lon": 44.36},
        "Erbil": {"lat": 36.19, "lon": 44.00},
        "Musul": {"lat": 36.34, "lon": 43.13},
        "Basra": {"lat": 30.50, "lon": 47.81},
        "Kerkük": {"lat": 35.46, "lon": 44.39}
    },
    "Afganistan": {
        "Kabil": {"lat": 34.55, "lon": 69.20},
        "Herat": {"lat": 34.35, "lon": 62.20},
        "Kandahar": {"lat": 31.62, "lon": 65.73},
        "Mezar-ı Şerif": {"lat": 36.70, "lon": 67.11}
    },
    "İran": {
        "Tahran": {"lat": 35.68, "lon": 51.38},
        "Tebriz": {"lat": 38.08, "lon": 46.29},
        "Meşhed": {"lat": 36.29, "lon": 59.60},
        "İsfahan": {"lat": 32.65, "lon": 51.66}
    },
    "Özbekistan": {
        "Taşkent": {"lat": 41.29, "lon": 69.24},
        "Semerkand": {"lat": 39.65, "lon": 66.97},
        "Buhara": {"lat": 39.76, "lon": 64.42}
    },
    "Türkmenistan": {
        "Aşkabat": {"lat": 37.96, "lon": 58.32},
        "Türkmenabat": {"lat": 39.07, "lon": 63.57}
    },
    "Azerbaycan": {
        "Bakü": {"lat": 40.40, "lon": 49.86},
        "Gence": {"lat": 40.68, "lon": 46.36}
    },
    "Pakistan": {
        "İslamabad": {"lat": 33.68, "lon": 73.04},
        "Karaçi": {"lat": 24.86, "lon": 67.00},
        "Lahor": {"lat": 31.52, "lon": 74.35}
    },
    "Mısır": {
        "Kahire": {"lat": 30.04, "lon": 31.23},
        "İskenderiye": {"lat": 31.20, "lon": 29.91}
    },
    "Lübnan": {
        "Beyrut": {"lat": 33.89, "lon": 35.50}
    },
    "ABD": {
        "New York": {"lat": 40.71, "lon": -74.00},
        "Los Angeles": {"lat": 34.05, "lon": -118.24}
    }
}

ULKELER = list(LOKASYON_VERISI.keys())

def uyari_goster(baslik, mesaj):
    content = FloatLayout()
    lbl = Label(
        text=mesaj,
        size_hint=(0.9, 0.6),
        pos_hint={'center_x': 0.5, 'center_y': 0.6},
        halign='center',
        valign='middle'
    )
    lbl.bind(size=lbl.setter('text_size'))
    content.add_widget(lbl)
    
    btn = Button(
        text="TAMAM",
        size_hint=(0.4, 0.25),
        pos_hint={'center_x': 0.5, 'center_y': 0.18},
        background_color=(0.75, 0.22, 0.17, 1)
    )
    content.add_widget(btn)
    
    popup = Popup(
        title=baslik,
        content=content,
        size_hint=(0.8, 0.35),
        auto_dismiss=False
    )
    btn.bind(on_release=popup.dismiss)
    popup.open()

UYUM_DATA = []

def yerel_veri_oku():
    global UYUM_DATA
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                UYUM_DATA = json.load(f)
                return True
        except Exception as e:
            print(f"Cache okuma hatası: {e}")

    olasi_dosyalar = ["sukur_naksatra_uyum_data_3.json", "sukur_naksatra_uyum_data.json"]
    for dosya_adi in olasi_dosyalar:
        local_json = os.path.join(BASE_DIR, dosya_adi)
        if os.path.exists(local_json):
            try:
                with open(local_json, "r", encoding="utf-8") as f:
                    UYUM_DATA = json.load(f)
                    return True
            except Exception as e:
                print(f"{dosya_adi} okuma hatası: {e}")
    return False

def github_veri_yukle():
    global UYUM_DATA
    def on_success(req, result):
        global UYUM_DATA
        try:
            if isinstance(result, str):
                yeni_veri = json.loads(result)
            else:
                yeni_veri = result
            if yeni_veri:
                UYUM_DATA = yeni_veri
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(UYUM_DATA, f, ensure_ascii=False)
        except Exception as e:
            print(f"GitHub veri hatası: {e}")

    def on_error(req, error):
        pass

    UrlRequest(GITHUB_JSON_URL, on_success=on_success, on_error=on_error, on_failure=on_error, timeout=4)

NAKSATRA_LISTESI = [
    "ASHWINI", "BHARANI", "KRITTIKA", "ROHINI", "MRIGASIRA", "ARDRA",
    "PUNARVASU", "PUSHYA", "ASHLESHA", "MAGHA", "PURVA PHALGUNI", "UTTARA PHALGUNI",
    "HASTA", "CHITRA", "SWATI", "VISHAKHA", "ANURADHA", "JYESHTA",
    "MULA", "PURVA ASHADHA", "UTTARA ASHADHA", "SHRAVANA", "DHANISHTA", "SHATABHISHAK",
    "PURVA BHADRA", "UTTARA BHADRA", "REVATI"
]

def metin_sadeleştir(s):
    if not s: return ""
    s = str(s).upper().strip()
    harf_haritalama = {'Ş': 'S', 'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'I': 'I', 'Ö': 'O', 'Ü': 'U'}
    for k, v in harf_haritalama.items():
        s = s.replace(k, v)
    return "".join(c for c in s if c.isalpha())

def otomatik_utc_offset_bul(lat, lon, dt_local):
    try:
        if tf is not None:
            tz_name = tf.timezone_at(lat=lat, lng=lon)
            if tz_name:
                local_tz = pytz.timezone(tz_name)
                localized_dt = local_tz.localize(dt_local, is_dst=None)
                return localized_dt.utcoffset().total_seconds() / 3600.0
        return 3.0
    except Exception as e:
        return 3.0

def lahiri_ayanamsa_hesapla(t_skyfield):
    julian_date = t_skyfield.tt
    years_since_2000 = (julian_date - 2451545.0) / 365.25
    ayanamsa = 23.85 + (0.01396 * years_since_2000)
    return ayanamsa

def naksatra_hesapla(gun, ay_str, yil_str, saat_str, dakika_str, am_pm_str, ulke="Türkiye", sehir="Ankara"):
    ay_sozluk = {
        "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, 
        "mayıs": 5, "mayis": 5, "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8,
        "eylül": 9, "eylul": 9, "ekim": 10, "kasım": 11, "kasim": 11, "aralık": 12, "aralik": 12
    }
    try:
        g = int(str(gun).strip())
        a = ay_sozluk.get(str(ay_str).strip().lower(), 1)
        y = int(str(yil_str).strip())
        saat_12 = int(str(saat_str).strip())
        dk = int(str(dakika_str).strip())
        
        ampm_upper = str(am_pm_str).strip().upper()
        if ampm_upper == "PM" and saat_12 < 12: 
            saat_24 = saat_12 + 12
        elif ampm_upper == "AM" and saat_12 == 12: 
            saat_24 = 0
        else: 
            saat_24 = saat_12

        lokasyon = LOKASYON_VERISI.get(ulke, {}).get(sehir, {"lat": 39.93, "lon": 32.85})
        lat = lokasyon.get("lat", 39.93)
        lon = lokasyon.get("lon", 32.85)

        dt_local = datetime(y, a, g, saat_24, dk)
        tz_offset = otomatik_utc_offset_bul(lat, lon, dt_local)

        dt_utc = dt_local - timedelta(hours=tz_offset)
        t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second)

        global eph
        if eph is None:
            try:
                eph = load('de421.bsp')
            except Exception as e:
                print(f"[RE-LOAD FAIL] de421.bsp okunamıyor: {e}")

        if eph is not None:
            earth = eph['earth']
            moon = eph['moon']
            observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
            astrometric = observer.at(t).observe(moon)
            ecliptic_lat, ecliptic_lon, distance = astrometric.ecliptic_latlon()
            tropical_moon_deg = ecliptic_lon.degrees % 360.0
        else:
            day_of_year = dt_utc.timetuple().tm_yday
            tropical_moon_deg = ((y - 2000) * 365.25 + day_of_year + (dt_utc.hour / 24.0)) * 13.17639 % 360.0

        ayanamsa = lahiri_ayanamsa_hesapla(t)
        sidereal_moon_deg = (tropical_moon_deg - ayanamsa) % 360.0

        nakshatra_index = int(sidereal_moon_deg / (360.0 / 27.0)) % 27
        hesaplanan_nak = NAKSATRA_LISTESI[nakshatra_index]

        print(f"[CANLI HESAPLANDI] Tarih: {g}.{a}.{y} {saat_24}:{dk} | Sehir: {sehir} | Ay: {sidereal_moon_deg:.2f}° | Sonuc: {hesaplanan_nak}")
        return hesaplanan_nak
    except Exception as e:
        print(f"[KRİTİK HATA] {e}")
        return "ANURADHA"

NAKSATRA_OZELLIKLERI = {
    "ASHWINI": "ASHWINI (Yönetici: Ketu):\nHızlı, cesur, öncü ve tükenmez bir yaşam enerjisine sahiptir. Şifacılık yönü yüksektir.",
    "BHARANI": "BHARANI (Yönetici: Venüs):\nAşırı tutkulu, korumacı, şehvetli ve kararlı bir doğaya sahiptir.",
    "KRITTIKA": "KRITTIKA (Yönetici: Güneş):\nDoğal bir lider, son derece dürüst, keskin zekalı ve odaklıdır.",
    "ROHINI": "ROHINI (Yönetici: Ay):\nSonsuz bir çekicilik, sanatsal yetenek, zarafet ve duygusallık taşır.",
    "MRIGASIRA": "MRIGASIRA (Yönetici: Mars):\nArayışın, araştırmanın ve merakın temsilcisidir. Zeki ve meraklıdır.",
    "ARDRA": "ARDRA (Yönetici: Rahu):\nDerin, analitik, duygusal fırtınalara açık ve dönüşüm odaklıdır.",
    "PUNARVASU": "PUNARVASU (Yönetici: Jüpiter):\nCömert, iyimser, hoşgörülü ve barışçıl bir mizaca sahiptir.",
    "PUSHYA": "PUSHYA (Yönetici: Satürn):\nVedik sistemin en koruyucu, besleyici ve sorumluluk sahibi Nakşatrasıdır.",
    "ASHLESHA": "ASHLESHA (Yönetici: Merkür):\nMistik, derin sezgilere sahip, stratejik ve psikolojik kavrayışı yüksektir.",
    "MAGHA": "MAGHA (Yönetici: Ketu):\nAsil, gururlu, cömert ve geçmişine/köklerine bağlı bir karakterdir.",
    "PURVA PHALGUNI": "PURVA PHALGUNI (Yönetici: Venüs):\nNeşeli, sosyal, yaşamın tadını çıkarmayı seven bir yapısı vardır.",
    "UTTARA PHALGUNI": "UTTARA PHALGUNI (Yönetici: Güneş):\nYardımsever, ilkeli, sözünün eri ve toplumsal sorumluluğu yüksektir.",
    "HASTA": "HASTA (Yönetici: Ay):\nBecerikli, pratik zekası gelişmiş, esprili ve el sanatlarına yatkındır.",
    "CHITRA": "CHITRA (Yönetici: Mars):\nYaratıcı, estetik tutkunu, özgün ve büyüleyici bir görsel zevke sahiptir.",
    "SWATI": "SWATI (Yönetici: Rahu):\nEsnek, özgürlükçü, diplomatik ve iletişim gücü çok yüksektir.",
    "VISHAKHA": "VISHAKHA (Yönetici: Jüpiter):\nAzimli, kararlı, hedeflerine kilitlenen ve pes etmeyen bir ruh taşır.",
    "ANURADHA": "ANURADHA (Yönetici: Satürn):\nSevgi dolu, kalpten bağlı, sezgisel ve dostluğa büyük değer verir.",
    "JYESHTA": "JYESHTA (Yönetici: Merkür):\nKoruyucu, olgun, stratejik ve kriz anlarında liderliği ele alandır.",
    "MULA": "MULA (Yönetici: Ketu):\nDoğrudan, yüzeysellikten uzak, kökleri ve hakikati araştıran ruhsal yapıdır.",
    "PURVA ASHADHA": "PURVA ASHADHA (Yönetici: Venüs):\nİyimser, ikna gücü yüksek, neşeli ve yenilmezlik inancına sahiptir.",
    "UTTARA ASHADHA": "UTTARA ASHADHA (Yönetici: Güneş):\nMütevazı, dürüst, ilkeli ve kalıcı zaferler elde eden adil bir karakterdir.",
    "SHRAVANA": "SHRAVANA (Yönetici: Ay):\nDinlemeyi bilen, derin bilgelik taşıyan, hassas ve öğrenmeye açıktır.",
    "DHANISHTA": "DHANISHTA (Yönetici: Mars):\nEnerjik, ritim duygusu yüksek, özgüvenli ve üretken bir yapıdır.",
    "SHATABHISHAK": "SHATABHISHAK (Yönetici: Rahu):\nŞifacı, bağımsız, gizemli ve analitik bir zekaya sahiptir.",
    "PURVA BHADRA": "PURVA BHADRA (Yönetici: Jüpiter):\nİidealist, tutkulu, derin düşünceli ve dönüşüm potansiyeli yüksektir.",
    "UTTARA BHADRA": "UTTARA BHADRA (Yönetici: Satürn):\nSakin, bilge, şefkatli, öfkesini kontrol edebilen olgun bir ruhtur.",
    "REVATI": "REVATI (Yönetici: Merkür):\nBesleyici, koşulsuz sevgi dolu, empati yeteneği yüksek ve romantiktir."
}

GUNLER = [f"{g:02d}" for g in range(1, 32)]
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylul", "Ekim", "Kasım", "Aralık"]
YILLAR = [str(y) for y in range(2026, 1930, -1)]
SAATLER_12 = [f"{h:02d}" for h in range(1, 13)]
DAKIKALAR = [f"{m:02d}" for m in range(60)]
AM_PM = ["AM", "PM"]

class SayfaBir(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        bg = Image(source=os.path.join(BASE_DIR, "1uyum (1).jpg"), allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        btn_hesapla = Button(
            text="HESAPLA", size_hint=(0.55, 0.07), pos_hint={'center_x': 0.5, 'center_y': 0.18},
            background_color=(0.75, 0.22, 0.17, 1), font_size='18sp', bold=True
        )
        btn_hesapla.bind(on_release=lambda x: setattr(self.manager, 'current', 'sayfa_iki'))
        layout.add_widget(btn_hesapla)

        btn_rehber = Button(
            text="Rehber & Yasal Uyarı", size_hint=(0.45, 0.04), pos_hint={'center_x': 0.5, 'center_y': 0.10},
            background_color=(0.91, 0.45, 0.62, 1), font_size='12sp', bold=True
        )
        btn_rehber.bind(on_release=rehber_popup_goster)
        layout.add_widget(btn_rehber)

        self.add_widget(layout)

class SayfaIki(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        bg = Image(source=os.path.join(BASE_DIR, "1uyum (2).jpg"), allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        # SEN BÖLÜMÜ
        self.sen_gun = Spinner(text="01", values=GUNLER, size_hint=(0.18, 0.04), pos_hint={'x': 0.30, 'top': 0.88})
        self.sen_ay = Spinner(text="Mayıs", values=AYLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.49, 'top': 0.88})
        self.sen_yil = Spinner(text="1980", values=YILLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.72, 'top': 0.88})

        self.sen_saat = Spinner(text="02", values=SAATLER_12, size_hint=(0.20, 0.04), pos_hint={'x': 0.30, 'top': 0.82})
        self.sen_dk = Spinner(text="42", values=DAKIKALAR, size_hint=(0.20, 0.04), pos_hint={'x': 0.51, 'top': 0.82})
        self.sen_ampm = Spinner(text="AM", values=AM_PM, size_hint=(0.20, 0.04), pos_hint={'x': 0.72, 'top': 0.82})

        self.sen_ulke = Spinner(text="Türkiye", values=ULKELER, size_hint=(0.31, 0.04), pos_hint={'x': 0.30, 'top': 0.76})
        self.sen_sehir = Spinner(text="Ankara", values=list(LOKASYON_VERISI["Türkiye"].keys()), size_hint=(0.31, 0.04), pos_hint={'x': 0.63, 'top': 0.76})
        self.sen_ulke.bind(text=self.update_sen_sehirler)

        for w in [self.sen_gun, self.sen_ay, self.sen_yil, self.sen_saat, self.sen_dk, self.sen_ampm, self.sen_ulke, self.sen_sehir]:
            layout.add_widget(w)

        # O BÖLÜMÜ
        self.o_gun = Spinner(text="09", values=GUNLER, size_hint=(0.18, 0.04), pos_hint={'x': 0.30, 'top': 0.57})
        self.o_ay = Spinner(text="Nisan", values=AYLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.49, 'top': 0.57})
        self.o_yil = Spinner(text="2013", values=YILLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.72, 'top': 0.57})

        self.o_saat = Spinner(text="12", values=SAATLER_12, size_hint=(0.20, 0.04), pos_hint={'x': 0.30, 'top': 0.51})
        self.o_dk = Spinner(text="05", values=DAKIKALAR, size_hint=(0.20, 0.04), pos_hint={'x': 0.51, 'top': 0.51})
        self.o_ampm = Spinner(text="AM", values=AM_PM, size_hint=(0.20, 0.04), pos_hint={'x': 0.72, 'top': 0.51})

        self.o_ulke = Spinner(text="Türkiye", values=ULKELER, size_hint=(0.31, 0.04), pos_hint={'x': 0.30, 'top': 0.45})
        self.o_sehir = Spinner(text="Ankara", values=list(LOKASYON_VERISI["Türkiye"].keys()), size_hint=(0.31, 0.04), pos_hint={'x': 0.63, 'top': 0.45})
        self.o_ulke.bind(text=self.update_o_sehirler)

        for w in [self.o_gun, self.o_ay, self.o_yil, self.o_saat, self.o_dk, self.o_ampm, self.o_ulke, self.o_sehir]:
            layout.add_widget(w)

        # HESAPLA BUTONU
        btn_hesapla = Button(
            text="HESAPLA", size_hint=(0.55, 0.07), pos_hint={'center_x': 0.5, 'center_y': 0.18},
            background_color=(0.75, 0.22, 0.17, 1), font_size='18sp', bold=True
        )
        btn_hesapla.bind(on_release=self.hesapla)
        layout.add_widget(btn_hesapla)

        # REHBER BUTONU
        btn_rehber = Button(
            text="Rehber & Yasal Uyarı", size_hint=(0.45, 0.04), pos_hint={'center_x': 0.5, 'center_y': 0.10},
            background_color=(0.91, 0.45, 0.62, 1), font_size='12sp', bold=True
        )
        btn_rehber.bind(on_release=rehber_popup_goster)
        layout.add_widget(btn_rehber)

        # GÖRSELDEKİ SAAT & UYARI METNİ
        lbl_saat_uyari = Label(
            text='"Doğum saatinizden ve AM/PM (Gece/Gündüz)\nseçiminizden emin olunuz. 1 saatlik bir sapma\nbile Ay konumunu değiştirebilir."',
            size_hint=(0.85, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.04},
            color=(0.75, 0.22, 0.17, 1),
            font_size='11sp',
            halign='center',
            valign='middle',
            bold=True
        )
        lbl_saat_uyari.bind(size=lbl_saat_uyari.setter('text_size'))
        layout.add_widget(lbl_saat_uyari)

        self.add_widget(layout)

    def update_sen_sehirler(self, spinner, text):
        sehirler = list(LOKASYON_VERISI.get(text, {}).keys())
        self.sen_sehir.values = sehirler
        if sehirler: self.sen_sehir.text = sehirler[0]

    def update_o_sehirler(self, spinner, text):
        sehirler = list(LOKASYON_VERISI.get(text, {}).keys())
        self.o_sehir.values = sehirler
        if sehirler: self.o_sehir.text = sehirler[0]

    def hesapla(self, instance):
        if not UYUM_DATA:
            if not yerel_veri_oku():
                uyari_goster("Veri Hatası", "Yerel Nakşatra veri dosyası bulunamadı.")
                return

        sen_nak = naksatra_hesapla(
            self.sen_gun.text, self.sen_ay.text, self.sen_yil.text,
            self.sen_saat.text, self.sen_dk.text, self.sen_ampm.text,
            self.sen_ulke.text, self.sen_sehir.text
        )
        
        o_nak = naksatra_hesapla(
            self.o_gun.text, self.o_ay.text, self.o_yil.text,
            self.o_saat.text, self.o_dk.text, self.o_ampm.text,
            self.o_ulke.text, self.o_sehir.text
        )

        sayfa_uc = self.manager.get_screen('sayfa_uc')
        sayfa_uc.son_sen_nak = sen_nak
        sayfa_uc.son_o_nak = o_nak
        sayfa_uc.analiz_yukle(sen_nak, o_nak)
        self.manager.current = 'sayfa_uc'

class SayfaUc(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.son_sen_nak = "ANURADHA"
        self.son_o_nak = "ANURADHA"

        layout = FloatLayout()
        bg = Image(source=os.path.join(BASE_DIR, "1uyum (3).jpg"), allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        # SEN BÖLÜMÜ
        scroll_sen = ScrollView(
            size_hint=(0.72, 0.16), pos_hint={'x': 0.25, 'top': 0.94},
            do_scroll_x=False, do_scroll_y=True
        )
        self.lbl_sen = Label(
            text="", size_hint_y=None, 
            color=(0.48, 0.25, 0.52, 1), font_size='13.5sp', halign='left', valign='top'
        )
        self.lbl_sen.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )
        scroll_sen.add_widget(self.lbl_sen)
        layout.add_widget(scroll_sen)

        # O BÖLÜMÜ
        scroll_o = ScrollView(
            size_hint=(0.72, 0.16), pos_hint={'x': 0.25, 'top': 0.76},
            do_scroll_x=False, do_scroll_y=True
        )
        self.lbl_o = Label(
            text="", size_hint_y=None, 
            color=(0.48, 0.25, 0.52, 1), font_size='13.5sp', halign='left', valign='top'
        )
        self.lbl_o.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )
        scroll_o.add_widget(self.lbl_o)
        layout.add_widget(scroll_o)

        # UYUM YÜZDESİ
        self.lbl_yuzde = Label(
            text="% --", size_hint=(0.72, 0.07), pos_hint={'x': 0.25, 'top': 0.58}, 
            color=(0.75, 0.22, 0.17, 1), font_size='24sp', bold=True, halign='left'
        )
        self.lbl_yuzde.bind(size=self.lbl_yuzde.setter('text_size'))
        layout.add_widget(self.lbl_yuzde)

        # DETAYLI JSON UYUM AÇIKLAMALARI
        self.scroll = ScrollView(
            size_hint=(0.72, 0.20), pos_hint={'x': 0.25, 'top': 0.49},
            do_scroll_x=False, do_scroll_y=True, bar_width=6,
            bar_color=(0.75, 0.22, 0.17, 0.8), bar_inactive_color=(0.75, 0.22, 0.17, 0.3)
        )

        self.lbl_ozet = Label(
            text="", size_hint_y=None, color=(0.48, 0.25, 0.52, 1), 
            font_size='13sp', halign='left', valign='top'
        )
        self.lbl_ozet.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )

        self.scroll.add_widget(self.lbl_ozet)
        layout.add_widget(self.scroll)

        btn_geri = Button(
            text="YENİ SORGULAMA", size_hint=(0.50, 0.06), pos_hint={'center_x': 0.5, 'center_y': 0.08},
            background_color=(0.48, 0.14, 0.11, 1), font_size='14sp', bold=True
        )
        btn_geri.bind(on_release=lambda x: setattr(self.manager, 'current', 'sayfa_iki'))
        layout.add_widget(btn_geri)

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        self.analiz_yukle(self.son_sen_nak, self.son_o_nak)

    def analiz_yukle(self, sen_nak, o_nak):
        self.son_sen_nak = sen_nak
        self.son_o_nak = o_nak

        sen_ozellik = NAKSATRA_OZELLIKLERI.get(sen_nak.upper(), "Özellik bulunamadı.")
        o_ozellik = NAKSATRA_OZELLIKLERI.get(o_nak.upper(), "Özellik bulunamadı.")

        self.lbl_sen.text = f"🌟 SEN: {sen_nak}\n{sen_ozellik}"
        self.lbl_o.text = f"🌟 O: {o_nak}\n{o_ozellik}"

        target_sen = metin_sadeleştir(sen_nak)
        target_o = metin_sadeleştir(o_nak)

        sen_to_o_veri = None
        o_to_sen_veri = None

        if isinstance(UYUM_DATA, list):
            for item in UYUM_DATA:
                nak = metin_sadeleştir(item.get("nakshatra") or item.get("nakshatra1") or item.get("naksatra"))
                prt = metin_sadeleştir(item.get("partner") or item.get("nakshatra2") or item.get("partner_naksatra"))

                if target_sen == target_o:
                    if nak == target_sen and prt == target_o:
                        sen_to_o_veri = item
                        break
                else:
                    if nak == target_sen and prt == target_o:
                        sen_to_o_veri = item
                    if nak == target_o and prt == target_sen:
                        o_to_sen_veri = item

        if sen_to_o_veri or o_to_sen_veri:
            yuzde = "--"
            if sen_to_o_veri:
                yuzde = sen_to_o_veri.get('compatibility_percentage') or sen_to_o_veri.get('puan') or sen_to_o_veri.get('percentage') or "--"
            elif o_to_sen_veri:
                yuzde = o_to_sen_veri.get('compatibility_percentage') or o_to_sen_veri.get('puan') or o_to_sen_veri.get('percentage') or "--"
            
            self.lbl_yuzde.text = f"%{yuzde}"

            birlesik_metin = ""

            if target_sen == target_o and sen_to_o_veri:
                birlesik_metin += f"📌 {sen_nak.title()} gözüyle {o_nak.title()}:\n"
                birlesik_metin += f"{sen_to_o_veri.get('description') or sen_to_o_veri.get('aciklama') or 'Açıklama bulunamadı.'}"
            else:
                if sen_to_o_veri:
                    birlesik_metin += f"📌 {sen_nak.title()} gözüyle {o_nak.title()}:\n"
                    birlesik_metin += f"{sen_to_o_veri.get('description') or sen_to_o_veri.get('aciklama') or 'Açıklama bulunamadı.'}"

                if sen_to_o_veri and o_to_sen_veri:
                    birlesik_metin += "\n\n----------------------------------------\n\n"

                if o_to_sen_veri:
                    birlesik_metin += f"📌 {o_nak.title()} gözüyle {sen_nak.title()}:\n"
                    birlesik_metin += f"{o_to_sen_veri.get('description') or o_to_sen_veri.get('aciklama') or 'Açıklama bulunamadı.'}"

            self.lbl_ozet.text = birlesik_metin
        else:
            self.lbl_yuzde.text = "% --"
            self.lbl_ozet.text = f"'{sen_nak}' ile '{o_nak}' ikilisi için detaylı uyum metni veritabanında bulunamadı."

class AskUyumuApp(App):
    def build(self):
        yerel_veri_oku()
        Clock.schedule_once(lambda dt: github_veri_yukle(), 0.5)
        
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SayfaBir(name='sayfa_bir'))
        sm.add_widget(SayfaIki(name='sayfa_iki'))
        sm.add_widget(SayfaUc(name='sayfa_uc'))
        return sm

if __name__ == '__main__':
    AskUyumuApp().run()
