import os
import json
import math
from datetime import datetime, timedelta

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
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

LOKASYON_VERISI = {
    "Türkiye": {
        "Ankara": {"lat": 39.93, "lon": 32.85, "tz": 3.0},
        "İstanbul": {"lat": 41.00, "lon": 28.97, "tz": 3.0},
        "İzmir": {"lat": 38.42, "lon": 27.14, "tz": 3.0},
        "Bursa": {"lat": 40.18, "lon": 29.06, "tz": 3.0},
        "Antalya": {"lat": 36.89, "lon": 30.70, "tz": 3.0},
        "Adana": {"lat": 37.00, "lon": 35.32, "tz": 3.0},
        "Gaziantep": {"lat": 37.06, "lon": 37.38, "tz": 3.0},
        "Konya": {"lat": 37.87, "lon": 32.48, "tz": 3.0},
        "Trabzon": {"lat": 41.00, "lon": 39.71, "tz": 3.0},
        "Şanlıurfa": {"lat": 37.16, "lon": 38.79, "tz": 3.0},
        "Hatay": {"lat": 36.20, "lon": 36.16, "tz": 3.0}
    },
    "Suriye": {
        "Şam (Damascus)": {"lat": 33.51, "lon": 36.27, "tz": 3.0},
        "Halep": {"lat": 36.20, "lon": 37.13, "tz": 3.0},
        "Humus": {"lat": 34.73, "lon": 36.71, "tz": 3.0},
        "Laziye": {"lat": 35.53, "lon": 35.78, "tz": 3.0}
    },
    "Irak": {
        "Bağdat": {"lat": 33.31, "lon": 44.36, "tz": 3.0},
        "Erbil": {"lat": 36.19, "lon": 44.00, "tz": 3.0},
        "Musul": {"lat": 36.34, "lon": 43.13, "tz": 3.0},
        "Basra": {"lat": 30.50, "lon": 47.81, "tz": 3.0},
        "Kerkük": {"lat": 35.46, "lon": 44.39, "tz": 3.0}
    },
    "Afganistan": {
        "Kabil": {"lat": 34.55, "lon": 69.20, "tz": 4.5},
        "Herat": {"lat": 34.35, "lon": 62.20, "tz": 4.5},
        "Kandahar": {"lat": 31.62, "lon": 65.73, "tz": 4.5},
        "Mezar-ı Şerif": {"lat": 36.70, "lon": 67.11, "tz": 4.5}
    },
    "İran": {
        "Tahran": {"lat": 35.68, "lon": 51.38, "tz": 3.5},
        "Tebriz": {"lat": 38.08, "lon": 46.29, "tz": 3.5},
        "Meşhed": {"lat": 36.29, "lon": 59.60, "tz": 3.5},
        "İsfahan": {"lat": 32.65, "lon": 51.66, "tz": 3.5}
    },
    "Özbekistan": {
        "Taşkent": {"lat": 41.29, "lon": 69.24, "tz": 5.0},
        "Semerkand": {"lat": 39.65, "lon": 66.97, "tz": 5.0},
        "Buhara": {"lat": 39.76, "lon": 64.42, "tz": 5.0}
    },
    "Türkmenistan": {
        "Aşkabat": {"lat": 37.96, "lon": 58.32, "tz": 5.0},
        "Türkmenabat": {"lat": 39.07, "lon": 63.57, "tz": 5.0}
    },
    "Azerbaycan": {
        "Bakü": {"lat": 40.40, "lon": 49.86, "tz": 4.0},
        "Gence": {"lat": 40.68, "lon": 46.36, "tz": 4.0}
    },
    "Pakistan": {
        "İslamabad": {"lat": 33.68, "lon": 73.04, "tz": 5.0},
        "Karaçi": {"lat": 24.86, "lon": 67.00, "tz": 5.0},
        "Lahor": {"lat": 31.52, "lon": 74.35, "tz": 5.0}
    },
    "Mısır": {
        "Kahire": {"lat": 30.04, "lon": 31.23, "tz": 2.0},
        "İskenderiye": {"lat": 31.20, "lon": 29.91, "tz": 2.0}
    },
    "Lübnan": {
        "Beyrut": {"lat": 33.89, "lon": 35.50, "tz": 2.0}
    },
    "Almanya": {
        "Berlin": {"lat": 52.52, "lon": 13.40, "tz": 1.0},
        "Münih": {"lat": 48.13, "lon": 11.58, "tz": 1.0},
        "Frankfurt": {"lat": 50.11, "lon": 8.68, "tz": 1.0}
    },
    "İngiltere": {
        "Londra": {"lat": 51.50, "lon": -0.12, "tz": 0.0}
    },
    "ABD": {
        "New York": {"lat": 40.71, "lon": -74.00, "tz": -5.0},
        "Los Angeles": {"lat": 34.05, "lon": -118.24, "tz": -8.0}
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
        except Exception:
            pass
    local_json = os.path.join(BASE_DIR, "sukur_naksatra_uyum_data_3.json")
    if os.path.exists(local_json):
        try:
            with open(local_json, "r", encoding="utf-8") as f:
                UYUM_DATA = json.load(f)
                return True
        except Exception:
            pass
    return False

def github_veri_yukle():
    global UYUM_DATA
    def on_success(req, result):
        global UYUM_DATA
        try:
            if isinstance(result, str):
                UYUM_DATA = json.loads(result)
            else:
                UYUM_DATA = result
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(UYUM_DATA, f, ensure_ascii=False)
        except Exception:
            yerel_veri_oku()

    def on_error(req, error):
        yerel_veri_oku()

    # Kivy'nin yerel asenkron ağ istek modülü
    UrlRequest(GITHUB_JSON_URL, on_success=on_success, on_error=on_error, on_failure=on_error, timeout=5)

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

def naksatra_hesapla(gun, ay_str, yil_str, saat_str, dakika_str, am_pm_str, ulke="Türkiye", sehir="Ankara"):
    ay_sozluk = {
        "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6,
        "Temmuz": 7, "Ağustos": 8, "Eylul": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12, "Eylül": 9
    }
    try:
        g = int(gun)
        a = ay_sozluk.get(ay_str, 1)
        y = int(yil_str)
        saat_12 = int(saat_str)
        dk = int(dakika_str)
        
        if am_pm_str == "PM" and saat_12 < 12: saat_24 = saat_12 + 12
        elif am_pm_str == "AM" and saat_12 == 12: saat_24 = 0
        else: saat_24 = saat_12

        lokasyon = LOKASYON_VERISI.get(ulke, {}).get(sehir, {"lat": 39.93, "lon": 32.85, "tz": 3.0})
        tz_offset = lokasyon.get("tz", 3.0)
        boylam = lokasyon.get("lon", 32.85)

        dt_local = datetime(y, a, g, saat_24, dk)
        dt_utc = dt_local - timedelta(hours=tz_offset)
        
        y_utc, m_utc, d_utc = dt_utc.year, dt_utc.month, dt_utc.day
        hour_utc = dt_utc.hour + (dt_utc.minute / 60.0)
        
        if m_utc <= 2:
            y_utc -= 1
            m_utc += 12
            
        A = math.floor(y_utc / 100)
        B = 2 - A + math.floor(A / 4)
        jd = math.floor(365.25 * (y_utc + 4716)) + math.floor(30.6001 * (m_utc + 1)) + d_utc + (hour_utc / 24.0) + B - 1524.5
        
        T = (jd - 2451545.0) / 36525.0
        L_prime = 218.3164477 + 481267.88123421 * T
        M_prime = 134.9633964 + 477198.8675055 * T
        M = 357.5291092 + 35999.0502909 * T
        D = 297.8501921 + 445267.1114034 * T
        F = 93.2720950 + 483202.0175273 * T
        
        to_rad, sin = math.radians, math.sin
        corr = (
            6.288774 * sin(to_rad(M_prime))
            + 1.274027 * sin(to_rad(2*D - M_prime))
            + 0.658314 * sin(to_rad(2*D))
            + 0.213618 * sin(to_rad(2*M_prime))
            - 0.185116 * sin(to_rad(M))
            - 0.114332 * sin(to_rad(2*F))
        )
        moon_tropical_lon = (L_prime + corr + (boylam - (tz_offset * 15.0)) * 0.055) % 360.0
        lahiri_ayanamsa = 23.85 + (T * 100.0) * 0.01397 + 0.16
        moon_sidereal_lon = (moon_tropical_lon - lahiri_ayanamsa) % 360.0
        return NAKSATRA_LISTESI[int(moon_sidereal_lon / (360.0 / 27.0)) % 27]
    except Exception:
        return "ANURADHA"

NAKSATRA_OZELLIKLERI = {
    "ASHWINI": "ASHWINI: Hızlı, cesur, öncü ve enerjik bir yapıya sahiptir.",
    "BHARANI": "BHARANI: Tutkulu, korumacı, şehvetli ve kararlıdır.",
    "KRITTIKA": "KRITTIKA: Doğal bir lider, dürüst ve odaklıdır.",
    "ROHINI": "ROHINI: Çekici, sanatsal ve duygusaldır.",
    "MRIGASIRA": "MRIGASIRA: Araştırmacı, zeki ve meraklıdır.",
    "ARDRA": "ARDRA: Derin, analitik ve dönüşüm odaklıdır.",
    "PUNARVASU": "PUNARVASU: Cömert, iyimser ve barışçıldır.",
    "PUSHYA": "PUSHYA: Besleyici, sadık ve sorumluluk sahibidir.",
    "ASHLESHA": "ASHLESHA: Mistik, sezgisel ve stratejiktir.",
    "MAGHA": "MAGHA: Asil, cömert ve gururludur.",
    "PURVA PHALGUNI": "PURVA PHALGUNI: Neşeli, sosyal ve sanatsaldır.",
    "UTTARA PHALGUNI": "UTTARA PHALGUNI: Cömert, yardımsever ve sadıktır.",
    "HASTA": "HASTA: Becerikli, pratik ve zekidir.",
    "CHITRA": "CHITRA: Yaratıcı, estetik tutkunu ve özgündür.",
    "SWATI": "SWATI: Esnek, özgürlükçü ve naziktir.",
    "VISHAKHA": "VISHAKHA: Azimli, odaklı ve tutkuludur.",
    "ANURADHA": "ANURADHA: Sevgi dolu, sadık ve sezgiseldir.",
    "JYESHTA": "JYESHTA: Koruyucu, olgun ve stratejiktir.",
    "MULA": "MULA: Doğrudan, araştırmacı ve ruhsaldır.",
    "PURVA ASHADHA": "PURVA ASHADHA: İyimser, ikna gücü yüksek ve neşelidir.",
    "UTTARA ASHADHA": "UTTARA ASHADHA: Mütevazı, dürüst ve ilkeli bir karakterdir.",
    "SHRAVANA": "SHRAVANA: Dinlemeyi bilen, bilge ve hassastır.",
    "DHANISHTA": "DHANISHTA: Enerjik, özgüvenli ve cömerttir.",
    "SHATABHISHAK": "SHATABHISHAK: Şifacı, bağımsız ve gizemlidir.",
    "PURVA BHADRA": "PURVA BHADRA: İdealist, tutkulu ve derin düşüncelidir.",
    "UTTARA BHADRA": "UTTARA BHADRA: Sakin, bilge ve şefkatlidir.",
    "REVATI": "REVATI: Besleyici ve koşulsuz sevgi doludur."
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
            text="HESAPLA",
            size_hint=(0.55, 0.07),
            pos_hint={'center_x': 0.5, 'center_y': 0.18},
            background_color=(0.75, 0.22, 0.17, 1),
            font_size='18sp',
            bold=True
        )
        btn_hesapla.bind(on_release=lambda x: setattr(self.manager, 'current', 'sayfa_iki'))
        layout.add_widget(btn_hesapla)
        self.add_widget(layout)

class SayfaIki(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        bg = Image(source=os.path.join(BASE_DIR, "1uyum (2).jpg"), allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        # SEN BÖLÜMÜ
        self.sen_gun = Spinner(text="02", values=GUNLER, size_hint=(0.18, 0.04), pos_hint={'x': 0.30, 'top': 0.88})
        self.sen_ay = Spinner(text="Mayıs", values=AYLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.49, 'top': 0.88})
        self.sen_yil = Spinner(text="1980", values=YILLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.72, 'top': 0.88})

        self.sen_saat = Spinner(text="02", values=SAATLER_12, size_hint=(0.20, 0.04), pos_hint={'x': 0.30, 'top': 0.82})
        self.sen_dk = Spinner(text="00", values=DAKIKALAR, size_hint=(0.20, 0.04), pos_hint={'x': 0.51, 'top': 0.82})
        self.sen_ampm = Spinner(text="AM", values=AM_PM, size_hint=(0.20, 0.04), pos_hint={'x': 0.72, 'top': 0.82})

        self.sen_ulke = Spinner(text="Türkiye", values=ULKELER, size_hint=(0.31, 0.04), pos_hint={'x': 0.30, 'top': 0.76})
        self.sen_sehir = Spinner(text="Ankara", values=list(LOKASYON_VERISI["Türkiye"].keys()), size_hint=(0.31, 0.04), pos_hint={'x': 0.63, 'top': 0.76})
        self.sen_ulke.bind(text=self.update_sen_sehirler)

        for w in [self.sen_gun, self.sen_ay, self.sen_yil, self.sen_saat, self.sen_dk, self.sen_ampm, self.sen_ulke, self.sen_sehir]:
            layout.add_widget(w)

        # O BÖLÜMÜ
        self.o_gun = Spinner(text="23", values=GUNLER, size_hint=(0.18, 0.04), pos_hint={'x': 0.30, 'top': 0.57})
        self.o_ay = Spinner(text="Mart", values=AYLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.49, 'top': 0.57})
        self.o_yil = Spinner(text="1982", values=YILLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.72, 'top': 0.57})

        self.o_saat = Spinner(text="11", values=SAATLER_12, size_hint=(0.20, 0.04), pos_hint={'x': 0.30, 'top': 0.51})
        self.o_dk = Spinner(text="45", values=DAKIKALAR, size_hint=(0.20, 0.04), pos_hint={'x': 0.51, 'top': 0.51})
        self.o_ampm = Spinner(text="AM", values=AM_PM, size_hint=(0.20, 0.04), pos_hint={'x': 0.72, 'top': 0.51})

        self.o_ulke = Spinner(text="Türkiye", values=ULKELER, size_hint=(0.31, 0.04), pos_hint={'x': 0.30, 'top': 0.45})
        self.o_sehir = Spinner(text="Ankara", values=list(LOKASYON_VERISI["Türkiye"].keys()), size_hint=(0.31, 0.04), pos_hint={'x': 0.63, 'top': 0.45})
        self.o_ulke.bind(text=self.update_o_sehirler)

        for w in [self.o_gun, self.o_ay, self.o_yil, self.o_saat, self.o_dk, self.o_ampm, self.o_ulke, self.o_sehir]:
            layout.add_widget(w)

        btn_hesapla = Button(
            text="HESAPLA",
            size_hint=(0.55, 0.07),
            pos_hint={'center_x': 0.5, 'center_y': 0.18},
            background_color=(0.75, 0.22, 0.17, 1),
            font_size='18sp',
            bold=True
        )
        btn_hesapla.bind(on_release=self.hesapla)
        layout.add_widget(btn_hesapla)

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
                uyari_goster("İnternet Bağlantı Hatası", "Veri yüklenemedi.\nLütfen bağlantınızı kontrol edin.")
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
        sayfa_uc.analiz_yukle(sen_nak, o_nak)
        self.manager.current = 'sayfa_uc'

class SayfaUc(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        bg = Image(source=os.path.join(BASE_DIR, "1uyum (3).jpg"), allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        self.lbl_sen = Label(
            text="", size_hint=(0.72, 0.15), pos_hint={'x': 0.25, 'top': 0.93}, 
            color=(0.48, 0.14, 0.11, 1), font_size='13sp', halign='left', valign='top'
        )
        self.lbl_sen.bind(size=self.lbl_sen.setter('text_size'))
        layout.add_widget(self.lbl_sen)

        self.lbl_o = Label(
            text="", size_hint=(0.72, 0.15), pos_hint={'x': 0.25, 'top': 0.75}, 
            color=(0.48, 0.14, 0.11, 1), font_size='13sp', halign='left', valign='top'
        )
        self.lbl_o.bind(size=self.lbl_o.setter('text_size'))
        layout.add_widget(self.lbl_o)

        self.lbl_yuzde = Label(
            text="% --", size_hint=(0.72, 0.08), pos_hint={'x': 0.25, 'top': 0.58}, 
            color=(0.75, 0.22, 0.17, 1), font_size='26sp', bold=True, halign='left'
        )
        self.lbl_yuzde.bind(size=self.lbl_yuzde.setter('text_size'))
        layout.add_widget(self.lbl_yuzde)

        self.scroll = ScrollView(
            size_hint=(0.72, 0.20), pos_hint={'x': 0.25, 'top': 0.48},
            do_scroll_x=False, do_scroll_y=True, bar_width=6,
            bar_color=(0.75, 0.22, 0.17, 0.8), bar_inactive_color=(0.75, 0.22, 0.17, 0.3)
        )

        self.lbl_ozet = Label(
            text="", size_hint_y=None, color=(0.29, 0.13, 0.35, 1), 
            font_size='12sp', halign='left', valign='top'
        )
        # Kivy Render Uyumu İçin Güvenli Boyutlandırma
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
        btn_geri.bind(on_release=lambda x: setattr(self.manager, 'current', 'sayfa_bir'))
        layout.add_widget(btn_geri)

        self.add_widget(layout)

    def analiz_yukle(self, sen_nak, o_nak):
        self.lbl_sen.text = NAKSATRA_OZELLIKLERI.get(sen_nak.upper(), f"{sen_nak}: Özellik bilgisi bulunamadı.")
        self.lbl_o.text = NAKSATRA_OZELLIKLERI.get(o_nak.upper(), f"{o_nak}: Özellik bilgisi bulunamadı.")

        target_sen = metin_sadeleştir(sen_nak)
        target_o = metin_sadeleştir(o_nak)

        sen_to_o_veri = None
        o_to_sen_veri = None

        if isinstance(UYUM_DATA, list):
            for item in UYUM_DATA:
                nak = metin_sadeleştir(item.get("nakshatra"))
                prt = metin_sadeleştir(item.get("partner"))

                if nak == target_sen and prt == target_o:
                    sen_to_o_veri = item
                elif nak == target_o and prt == target_sen:
                    o_to_sen_veri = item

        if sen_to_o_veri or o_to_sen_veri:
            yuzde = (
                sen_to_o_veri.get('compatibility_percentage') if sen_to_o_veri 
                else o_to_sen_veri.get('compatibility_percentage', '--')
            )
            self.lbl_yuzde.text = f"%{yuzde}"

            birlesik_metin = ""
            if sen_to_o_veri:
                birlesik_metin += f"📌 {sen_nak.title()} gözüyle {o_nak.title()}:\n"
                birlesik_metin += f"{sen_to_o_veri.get('description', 'Açıklama bulunamadı.')}\n\n"
                birlesik_metin += "----------------------------------------\n\n"

            if o_to_sen_veri:
                birlesik_metin += f"📌 {o_nak.title()} gözüyle {sen_nak.title()}:\n"
                birlesik_metin += f"{o_to_sen_veri.get('description', 'Açıklama bulunamadı.')}"

            self.lbl_ozet.text = birlesik_metin
        else:
            self.lbl_yuzde.text = "% --"
            self.lbl_ozet.text = f"'{sen_nak}' ile '{o_nak}' için uyum verisi bulunamadı."

class AskUyumuApp(App):
    def build(self):
        # Uygulama açılırken Kivy döngüsünü aksatmadan arka planda ağ isteği başlatır
        Clock.schedule_once(lambda dt: github_veri_yukle(), 0.5)
        
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SayfaBir(name='sayfa_bir'))
        sm.add_widget(SayfaIki(name='sayfa_iki'))
        sm.add_widget(SayfaUc(name='sayfa_uc'))
        return sm

if __name__ == '__main__':
    AskUyumuApp().run()
