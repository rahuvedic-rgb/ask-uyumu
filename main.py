import os
import json
import math
from datetime import datetime, timedelta

# C KÜTÜPHANELERİ İÇİN GÜVENLİ YÜKLEME VE KORUMA
try:
    import swisseph as swe
except Exception as e:
    print(f"[UYARI] Swiss Ephemeris kütüphanesi yüklenemedi: {e}")
    swe = None

import pytz

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

# REHBER VE YASAL UYARI METNİ
REHBER_VE_YASAL_UYARI_METNI = """==================================
   AŞK UYUMU ANALİZİ - REHBER
==================================

1. UYGULAMA NASIL KULLANILIR?
----------------------------------
* "SEN" ve "O" bölümlerinde doğum günü, ayı, yılı, saati, dakikası, AM/PM, Ülke ve Şehir bilgilerini eksiksiz girin.
* "HESAPLA" butonuna bastığınızda Vedik Astroloji haritanıza göre Nakşatra (Ay Burcu) konumlarınız belirlenir.

2. OTOMATİK ZAMAN DİLİMİ VE SAAT (AM/PM)
----------------------------------
* AM (Gece / Sabah): Gece yarısı 12:00'den öğlen 11:59'a kadar olan zamandır.
* PM (Öğle / Akşam): Öğlen 12:00'den gece 11:59'a kadar olan zamandır.

3. BAKIŞ AÇISI UYARISI ("SEN" vs "O")
----------------------------------
* "SEN" bölümüne kendi bilgilerinizi yazdığınızda analiz SİZİN BAKIŞ AÇINIZA göre yapılır.
* "SEN" bölümüne partnerinizin bilgilerini yazdığınızda analiz ONUN BAKIŞ AÇINIZA göre yapılır.

4. UYUM ORANI SKALASI (%0 - %91)
----------------------------------
* %0 - %33  : Karmik / Zorlu / Mücadeleli Uyum
* %34 - %66 : Dengeli / Esnek Uyum
* %67 - %91 : Mükemmel / Ruh Eşi Bağı
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
        "Ankara": {"lat": 39.93, "lon": 32.85, "tz": "Europe/Istanbul"},
        "İstanbul": {"lat": 41.00, "lon": 28.97, "tz": "Europe/Istanbul"},
        "İzmir": {"lat": 38.42, "lon": 27.14, "tz": "Europe/Istanbul"},
        "Bursa": {"lat": 40.18, "lon": 29.06, "tz": "Europe/Istanbul"},
        "Antalya": {"lat": 36.89, "lon": 30.70, "tz": "Europe/Istanbul"},
        "Adana": {"lat": 37.00, "lon": 35.32, "tz": "Europe/Istanbul"},
        "Gaziantep": {"lat": 37.06, "lon": 37.38, "tz": "Europe/Istanbul"},
        "Konya": {"lat": 37.87, "lon": 32.48, "tz": "Europe/Istanbul"},
        "Trabzon": {"lat": 41.00, "lon": 39.71, "tz": "Europe/Istanbul"},
        "Şanlıurfa": {"lat": 37.16, "lon": 38.79, "tz": "Europe/Istanbul"},
        "Hatay": {"lat": 36.20, "lon": 36.16, "tz": "Europe/Istanbul"}
    },
    "İspanya": {
        "Madrid": {"lat": 40.41, "lon": -3.70, "tz": "Europe/Madrid"},
        "Barselona": {"lat": 41.38, "lon": 2.17, "tz": "Europe/Madrid"}
    }
}

ULKELER = list(LOKASYON_VERISI.keys())

def uyari_goster(baslik, mesaj):
    content = FloatLayout()
    lbl = Label(
        text=mesaj, size_hint=(0.9, 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.6},
        halign='center', valign='middle'
    )
    lbl.bind(size=lbl.setter('text_size'))
    content.add_widget(lbl)
    
    btn = Button(
        text="TAMAM", size_hint=(0.4, 0.25), pos_hint={'center_x': 0.5, 'center_y': 0.18},
        background_color=(0.75, 0.22, 0.17, 1)
    )
    content.add_widget(btn)
    
    popup = Popup(title=baslik, content=content, size_hint=(0.8, 0.35), auto_dismiss=False)
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

def otomatik_utc_offset_bul(tz_name, dt_local):
    try:
        local_tz = pytz.timezone(tz_name)
        localized_dt = local_tz.localize(dt_local, is_dst=None)
        return localized_dt.utcoffset().total_seconds() / 3600.0
    except Exception:
        return 3.0

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
        
        if str(am_pm_str).strip().upper() == "PM" and saat_12 < 12: 
            saat_24 = saat_12 + 12
        elif str(am_pm_str).strip().upper() == "AM" and saat_12 == 12: 
            saat_24 = 0
        else: 
            saat_24 = saat_12

        lokasyon = LOKASYON_VERISI.get(ulke, {}).get(sehir, {"lat": 39.93, "lon": 32.85, "tz": "Europe/Istanbul"})
        tz_name = lokasyon.get("tz", "Europe/Istanbul")

        dt_local = datetime(y, a, g, saat_24, dk)
        tz_offset = otomatik_utc_offset_bul(tz_name, dt_local)

        if swe is not None:
            swe.close()
            swe.set_ephe_path('')
            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
            ut_hour = (saat_24 + (dk / 60.0)) - tz_offset
            julian_day = swe.julday(y, a, g, ut_hour)
            flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
            res, flag = swe.calc_ut(julian_day, swe.MOON, flags)
            moon_longitude = res[0] % 360.0
            nakshatra_index = int(moon_longitude / (360.0 / 27.0)) % 27
            hesaplanan_nak = NAKSATRA_LISTESI[nakshatra_index]
            swe.close()
            return hesaplanan_nak
        else:
            return "ANURADHA"
    except Exception as e:
        print(f"HATA: {e}")
        return "ANURADHA"

NAKSATRA_OZELLIKLERI = {
    "ASHWINI": "ASHWINI (Yönetici: Ketu): Hızlı, cesur, öncü ve tükenmez bir yaşam enerjisine sahiptir.",
    "BHARANI": "BHARANI (Yönetici: Venüs): Aşırı tutkulu, korumacı, şehvetli ve kararlı bir doğaya sahiptir.",
    "KRITTIKA": "KRITTIKA (Yönetici: Güneş): Doğal bir lider, son derece dürüst ve keskin zekalıdır.",
    "ROHINI": "ROHINI (Yönetici: Ay): Sonsuz bir çekicilik, sanatsal yetenek ve zarafet taşır.",
    "MRIGASIRA": "MRIGASIRA (Yönetici: Mars): Arayışın, araştırmanın ve merakın temsilcisidir.",
    "ARDRA": "ARDRA (Yönetici: Rahu): Derin, analitik ve dönüşüm odaklıdır.",
    "PUNARVASU": "PUNARVASU (Yönetici: Jüpiter): Cömert, iyimser ve barışçıl bir mizaca sahiptir.",
    "PUSHYA": "PUSHYA (Yönetici: Satürn): Vedik sistemin en koruyucu ve sorumluluk sahibi Nakşatrasıdır.",
    "ASHLESHA": "ASHLESHA (Yönetici: Merkür): Mistik, derin sezgilere sahip ve stratejiktir.",
    "MAGHA": "MAGHA (Yönetici: Ketu): Asil, gururlu ve lider ruhlu bir karakterdir.",
    "PURVA PHALGUNI": "PURVA PHALGUNI (Yönetici: Venüs): Neşeli, sosyal ve sanatsal bir mizaca sahiptir.",
    "UTTARA PHALGUNI": "UTTARA PHALGUNI (Yönetici: Güneş): Yardımsever, ilkeli ve sözünün eridir.",
    "HASTA": "HASTA (Yönetici: Ay): Becerikli, pratik zekası gelişmiş ve esprilidir.",
    "CHITRA": "CHITRA (Yönetici: Mars): Yaratıcı, estetik tutkunu ve özgündür.",
    "SWATI": "SWATI (Yönetici: Rahu): Esnek, özgürlükçü ve diplomatiktir.",
    "VISHAKHA": "VISHAKHA (Yönetici: Jüpiter): Azimli, kararlı ve hedeflerine odaklıdır.",
    "ANURADHA": "ANURADHA (Yönetici: Satürn): Sevgi dolu, kalpten bağlı ve sezgiseldir.",
    "JYESHTA": "JYESHTA (Yönetici: Merkür): Koruyucu, olgun ve kriz anlarında liderdir.",
    "MULA": "MULA (Yönetici: Ketu): Hakikati araştıran ruhsal bir karakterdir.",
    "PURVA ASHADHA": "PURVA ASHADHA (Yönetici: Venüs): İyimser, ikna gücü yüksek ve neşelidir.",
    "UTTARA ASHADHA": "UTTARA ASHADHA (Yönetici: Güneş): Mütevazı, dürüst ve ilkeli bir karakterdir.",
    "SHRAVANA": "SHRAVANA (Yönetici: Ay): Dinlemeyi bilen ve derin bilgelik taşıyan bir ruhtur.",
    "DHANISHTA": "DHANISHTA (Yönetici: Mars): Enerjik, ritim duygusu yüksek ve özgüvenlidir.",
    "SHATABHISHAK": "SHATABHISHAK (Yönetici: Rahu): Şifacı, bağımsız ve gizemli bir zekaya sahiptir.",
    "PURVA BHADRA": "PURVA BHADRA (Yönetici: Jüpiter): İidealist, tutkulu ve derin düşüncelidir.",
    "UTTARA BHADRA": "UTTARA BHADRA (Yönetici: Satürn): Sakin, bilge, şefkatli ve olgundur.",
    "REVATI": "REVATI (Yönetici: Merkür): Besleyici, koşulsuz sevgi dolu ve empati yeteneği yüksektir."
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

        self.sen_gun = Spinner(text="17", values=GUNLER, size_hint=(0.18, 0.04), pos_hint={'x': 0.30, 'top': 0.88})
        self.sen_ay = Spinner(text="Nisan", values=AYLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.49, 'top': 0.88})
        self.sen_yil = Spinner(text="2026", values=YILLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.72, 'top': 0.88})

        self.sen_saat = Spinner(text="08", values=SAATLER_12, size_hint=(0.20, 0.04), pos_hint={'x': 0.30, 'top': 0.82})
        self.sen_dk = Spinner(text="00", values=DAKIKALAR, size_hint=(0.20, 0.04), pos_hint={'x': 0.51, 'top': 0.82})
        self.sen_ampm = Spinner(text="AM", values=AM_PM, size_hint=(0.20, 0.04), pos_hint={'x': 0.72, 'top': 0.82})

        self.sen_ulke = Spinner(text="Türkiye", values=ULKELER, size_hint=(0.31, 0.04), pos_hint={'x': 0.30, 'top': 0.76})
        self.sen_sehir = Spinner(text="Ankara", values=list(LOKASYON_VERISI["Türkiye"].keys()), size_hint=(0.31, 0.04), pos_hint={'x': 0.63, 'top': 0.76})

        for w in [self.sen_gun, self.sen_ay, self.sen_yil, self.sen_saat, self.sen_dk, self.sen_ampm, self.sen_ulke, self.sen_sehir]:
            layout.add_widget(w)

        self.o_gun = Spinner(text="21", values=GUNLER, size_hint=(0.18, 0.04), pos_hint={'x': 0.30, 'top': 0.57})
        self.o_ay = Spinner(text="Nisan", values=AYLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.49, 'top': 0.57})
        self.o_yil = Spinner(text="2023", values=YILLAR, size_hint=(0.22, 0.04), pos_hint={'x': 0.72, 'top': 0.57})

        self.o_saat = Spinner(text="09", values=SAATLER_12, size_hint=(0.20, 0.04), pos_hint={'x': 0.30, 'top': 0.51})
        self.o_dk = Spinner(text="00", values=DAKIKALAR, size_hint=(0.20, 0.04), pos_hint={'x': 0.51, 'top': 0.51})
        self.o_ampm = Spinner(text="AM", values=AM_PM, size_hint=(0.20, 0.04), pos_hint={'x': 0.72, 'top': 0.51})

        self.o_ulke = Spinner(text="Türkiye", values=ULKELER, size_hint=(0.31, 0.04), pos_hint={'x': 0.30, 'top': 0.45})
        self.o_sehir = Spinner(text="Ankara", values=list(LOKASYON_VERISI["Türkiye"].keys()), size_hint=(0.31, 0.04), pos_hint={'x': 0.63, 'top': 0.45})

        for w in [self.o_gun, self.o_ay, self.o_yil, self.o_saat, self.o_dk, self.o_ampm, self.o_ulke, self.o_sehir]:
            layout.add_widget(w)

        btn_hesapla = Button(
            text="HESAPLA", size_hint=(0.55, 0.07), pos_hint={'center_x': 0.5, 'center_y': 0.18},
            background_color=(0.75, 0.22, 0.17, 1), font_size='18sp', bold=True
        )
        btn_hesapla.bind(on_release=self.hesapla)
        layout.add_widget(btn_hesapla)

        self.add_widget(layout)

    def hesapla(self, instance):
        if not UYUM_DATA:
            if not yerel_veri_oku():
                uyari_goster("Veri Hatası", "Yerel Nakşatra veri dosyası bulunamadı.")
                return

        sen_nak = naksatra_hesapla(self.sen_gun.text, self.sen_ay.text, self.sen_yil.text, self.sen_saat.text, self.sen_dk.text, self.sen_ampm.text, self.sen_ulke.text, self.sen_sehir.text)
        o_nak = naksatra_hesapla(self.o_gun.text, self.o_ay.text, self.o_yil.text, self.o_saat.text, self.o_dk.text, self.o_ampm.text, self.o_ulke.text, self.o_sehir.text)

        sayfa_uc = self.manager.get_screen('sayfa_uc')
        sayfa_uc.analiz_yukle(sen_nak, o_nak)
        self.manager.current = 'sayfa_uc'

class SayfaUc(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        bg = Image(source=os.path.join(BASE_DIR, "1uyum (3).jpg"), allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        scroll_sen = ScrollView(size_hint=(0.72, 0.16), pos_hint={'x': 0.25, 'top': 0.94}, do_scroll_x=False, do_scroll_y=True)
        self.lbl_sen = Label(text="", size_hint_y=None, color=(0.48, 0.25, 0.52, 1), font_size='13.5sp', halign='left', valign='top')
        self.lbl_sen.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)), texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        scroll_sen.add_widget(self.lbl_sen)
        layout.add_widget(scroll_sen)

        scroll_o = ScrollView(size_hint=(0.72, 0.16), pos_hint={'x': 0.25, 'top': 0.76}, do_scroll_x=False, do_scroll_y=True)
        self.lbl_o = Label(text="", size_hint_y=None, color=(0.48, 0.25, 0.52, 1), font_size='13.5sp', halign='left', valign='top')
        self.lbl_o.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)), texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        scroll_o.add_widget(self.lbl_o)
        layout.add_widget(scroll_o)

        self.lbl_yuzde = Label(text="% --", size_hint=(0.72, 0.07), pos_hint={'x': 0.25, 'top': 0.58}, color=(0.75, 0.22, 0.17, 1), font_size='24sp', bold=True, halign='left')
        self.lbl_yuzde.bind(size=self.lbl_yuzde.setter('text_size'))
        layout.add_widget(self.lbl_yuzde)

        self.scroll = ScrollView(size_hint=(0.72, 0.20), pos_hint={'x': 0.25, 'top': 0.49}, do_scroll_x=False, do_scroll_y=True, bar_width=6)
        self.lbl_ozet = Label(text="", size_hint_y=None, color=(0.48, 0.25, 0.52, 1), font_size='13sp', halign='left', valign='top')
        self.lbl_ozet.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)), texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.scroll.add_widget(self.lbl_ozet)
        layout.add_widget(self.scroll)

        btn_geri = Button(text="YENİ SORGULAMA", size_hint=(0.50, 0.06), pos_hint={'center_x': 0.5, 'center_y': 0.08}, background_color=(0.48, 0.14, 0.11, 1), font_size='14sp', bold=True)
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
            yuzde = (sen_to_o_veri.get('compatibility_percentage') if sen_to_o_veri else o_to_sen_veri.get('compatibility_percentage', '--'))
            self.lbl_yuzde.text = f"%{yuzde}"

            birlesik_metin = ""
            if sen_to_o_veri:
                birlesik_metin += f"📌 {sen_nak.title()} gözüyle {o_nak.title()}:\n"
                birlesik_metin += f"{sen_to_o_veri.get('description', 'Açıklama bulunamadı.')}\n\n"

            if o_to_sen_veri:
                birlesik_metin += f"📌 {o_nak.title()} gözüyle {sen_nak.title()}:\n"
                birlesik_metin += f"{o_to_sen_veri.get('description', 'Açıklama bulunamadı.')}"

            self.lbl_ozet.text = birlesik_metin
        else:
            self.lbl_yuzde.text = "% --"
            self.lbl_ozet.text = f"'{sen_nak}' ile '{o_nak}' için uyum verisi bulunamadı."

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
