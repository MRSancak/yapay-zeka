from datetime import datetime
import webbrowser
import json
import os
import re
import html
import urllib.parse
import urllib.request
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import winsound
import ctypes
import sys


try:
    from cefpython3 import cefpython as cef
    CEF_VAR = True
except ImportError:
    cef = None
    CEF_VAR = False


masaustu_yolu = os.path.join(
    os.path.expanduser("~"),
    "Desktop"
)

klasor_adi = os.path.join(
    masaustu_yolu,
    "Yapay Zeka"
)

ses_klasoru = os.path.join(
    klasor_adi,
    "Ses"
)

kayit_klasoru = os.path.join(
    klasor_adi,
    "Kayitlar"
)

tarayici_veri_klasoru = os.path.join(
    klasor_adi,
    "TarayiciVerisi"
)

os.makedirs(klasor_adi, exist_ok=True)
os.makedirs(ses_klasoru, exist_ok=True)
os.makedirs(kayit_klasoru, exist_ok=True)
os.makedirs(tarayici_veri_klasoru, exist_ok=True)


HAFIZA_DOSYASI = os.path.join(
    klasor_adi,
    "hafiza.json"
)

GECMIS_DOSYASI = os.path.join(
    klasor_adi,
    "gecmis.json"
)

SES_AYAR_DOSYASI = os.path.join(
    klasor_adi,
    "ses_ayar.json"
)

TARAYICI_DURUM_DOSYASI = os.path.join(
    klasor_adi,
    "tarayici_durum.json"
)

KLAVYE_SESI = os.path.join(
    ses_klasoru,
    "klavye.wav"
)

WEB_SITESI_URL = "https://minihaxball.onrender.com/"

TARAYICI_MAKS_SEKME = 10

CEF_BASLADI = False


def json_yukle(dosya_adi):
    if os.path.exists(dosya_adi):
        try:
            with open(
                dosya_adi,
                "r",
                encoding="utf-8"
            ) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def json_kaydet(dosya_adi, veri):
    try:
        klasor = os.path.dirname(dosya_adi)

        if klasor:
            os.makedirs(
                klasor,
                exist_ok=True
            )

        gecici_dosya = dosya_adi + ".tmp"

        with open(
            gecici_dosya,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                veri,
                f,
                ensure_ascii=False,
                indent=4
            )

        os.replace(
            gecici_dosya,
            dosya_adi
        )

    except Exception:
        try:
            if os.path.exists(
                dosya_adi + ".tmp"
            ):
                os.remove(
                    dosya_adi + ".tmp"
                )
        except Exception:
            pass


def hafizadan_bul(
    sorgu,
    hafiza_sozlugu
):
    sorgu_temiz = sorgu.lower().strip()

    selamlasmalar = {
        "naber":
            "İyidir, kodları yazmaya devam ediyorum! Sen nasılsın, neler yapıyorsun?",
        "nasılsın":
            "Çok iyiyim, sistem sorunsuz çalışıyor. Sen nasılsın?",
        "merhaba":
            "Merhaba! Sana nasıl yardımcı olabilirim?",
        "selam":
            "Aleykümselam! Hangi konuda yardıma ihtiyacın var?",
        "iyi günler":
            "Teşekkürler, sana da iyi günler!"
    }

    if sorgu_temiz in selamlasmalar:
        return selamlasmalar[sorgu_temiz]

    if sorgu_temiz in hafiza_sozlugu:
        return hafiza_sozlugu[sorgu_temiz]

    kelimeler = sorgu_temiz.split()

    en_iyi = None
    en_yuksek = 0

    for anahtar, cevap in hafiza_sozlugu.items():
        anahtar_kelime = str(
            anahtar
        ).lower().strip()

        if not anahtar_kelime:
            continue

        skor = 0

        if anahtar_kelime in sorgu_temiz:
            skor += 70

        for kelime in kelimeler:
            if kelime in anahtar_kelime:
                skor += 10

        if skor > en_yuksek:
            en_yuksek = skor
            en_iyi = cevap

    if en_yuksek >= 70:
        return en_iyi

    return None


def html_temizle(metin):
    if not metin:
        return ""

    metin = re.sub(
        r"<script.*?</script>",
        "",
        metin,
        flags=re.IGNORECASE | re.DOTALL
    )

    metin = re.sub(
        r"<style.*?</style>",
        "",
        metin,
        flags=re.IGNORECASE | re.DOTALL
    )

    metin = re.sub(
        r"<[^>]+>",
        "",
        metin
    )

    metin = html.unescape(
        metin
    )

    metin = re.sub(
        r"\s+",
        " ",
        metin
    )

    return metin.strip()


def guvenli_istek(
    url,
    timeout=10
):
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36",
        "Accept":
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language":
            "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    req = urllib.request.Request(
        url,
        headers=headers
    )

    with urllib.request.urlopen(
        req,
        timeout=timeout
    ) as response:
        return response.read().decode(
            "utf-8",
            errors="replace"
        )


def github_sonuclarini_ayikla(
    html_icerik
):
    sonuclar = []

    bloklar = re.findall(
        r'<div[^>]*class="result[^"]*"[^>]*>'
        r'(.*?)</div>\s*</div>',
        html_icerik,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not bloklar:
        bloklar = re.findall(
            r'(<div[^>]*class="result[^"]*".*?)'
            r'(?=<div[^>]*class="result[^"]*")',
            html_icerik,
            flags=re.IGNORECASE | re.DOTALL
        )

    for blok in bloklar:
        baslik_eslesme = re.search(
            r'class="result__a"[^>]*href="([^"]+)"'
            r'[^>]*>(.*?)</a>',
            blok,
            flags=re.IGNORECASE | re.DOTALL
        )

        if not baslik_eslesme:
            continue

        link = html.unescape(
            baslik_eslesme.group(1)
        )

        baslik = html_temizle(
            baslik_eslesme.group(2)
        )

        try:
            parsed = urllib.parse.urlparse(
                link
            )

            params = urllib.parse.parse_qs(
                parsed.query
            )

            if "uddg" in params:
                link = urllib.parse.unquote(
                    params["uddg"][0]
                )

        except Exception:
            pass

        snippet_eslesme = re.search(
            r'class="result__snippet[^"]*"'
            r'[^>]*>(.*?)</(?:a|div)>',
            blok,
            flags=re.IGNORECASE | re.DOTALL
        )

        if snippet_eslesme:
            aciklama = html_temizle(
                snippet_eslesme.group(1)
            )
        else:
            aciklama = ""

        if not baslik:
            continue

        mevcut_linkler = [
            x["link"]
            for x in sonuclar
        ]

        if link not in mevcut_linkler:
            sonuclar.append({
                "baslik": baslik,
                "link": link,
                "aciklama": aciklama
            })

        if len(sonuclar) >= 8:
            break

    return sonuclar


def github_arastir(sorgu):
    try:
        arama_sorgusu = (
            f"site:github.com {sorgu}"
        )

        encoded_query = urllib.parse.quote_plus(
            arama_sorgusu
        )

        url = (
            "https://html.duckduckgo.com/html/?q="
            + encoded_query
        )

        html_icerik = guvenli_istek(
            url,
            timeout=12
        )

        sonuclar = github_sonuclarini_ayikla(
            html_icerik
        )

        github_sonuclari = []

        for sonuc in sonuclar:
            link = sonuc["link"].lower()

            if (
                "github.com" in link
                and "github.com/search" not in link
            ):
                github_sonuclari.append(
                    sonuc
                )

        if github_sonuclari:
            cikti = [
                f"GitHub Kod ve Kaynak Sonuçları ({sorgu}):",
                ""
            ]

            for i, sonuc in enumerate(
                github_sonuclari[:8],
                start=1
            ):
                cikti.append(
                    f"{i}. {sonuc['baslik']}"
                )

                cikti.append(
                    f"   🔗 {sonuc['link']}"
                )

                if sonuc["aciklama"]:
                    cikti.append(
                        f"   📝 {sonuc['aciklama']}"
                    )

                cikti.append("")

            cikti.append(
                "GitHub taraması tamamlandı."
            )

            return "\n".join(cikti)

        return github_yedek_arama(
            sorgu
        )

    except Exception as e:
        return (
            "GitHub araması sırasında bağlantı sorunu oluştu.\n\n"
            f"Hata: {e}\n\n"
            "Yedek arama sistemi çalıştırılıyor...\n\n"
            + github_yedek_arama(sorgu)
        )


def github_yedek_arama(sorgu):
    try:
        arama_sorgusu = (
            f"github {sorgu} source code repository"
        )

        encoded_query = urllib.parse.quote_plus(
            arama_sorgusu
        )

        url = (
            "https://html.duckduckgo.com/html/?q="
            + encoded_query
        )

        html_icerik = guvenli_istek(
            url,
            timeout=10
        )

        sonuclar = github_sonuclarini_ayikla(
            html_icerik
        )

        if sonuclar:
            cikti = [
                "GitHub için genişletilmiş arama sonuçları:",
                ""
            ]

            sayac = 0

            for sonuc in sonuclar:
                if "github.com" not in sonuc[
                    "link"
                ].lower():
                    continue

                sayac += 1

                cikti.append(
                    f"{sayac}. {sonuc['baslik']}"
                )

                cikti.append(
                    f"   🔗 {sonuc['link']}"
                )

                if sonuc["aciklama"]:
                    cikti.append(
                        f"   📝 {sonuc['aciklama']}"
                    )

                cikti.append("")

                if sayac >= 8:
                    break

            if sayac > 0:
                return "\n".join(cikti)

        return (
            f"'{sorgu}' için GitHub'da "
            "uygun bir sonuç bulunamadı."
        )

    except Exception as e:
        return (
            "GitHub araması başarısız oldu.\n"
            f"Hata: {e}"
        )


def normal_web_arastir(sorgu):
    try:
        sorgu_temiz = sorgu.lower()

        if "hava durumu" in sorgu_temiz:
            arama_sorgusu = (
                f"{sorgu} güncel hava durumu "
                f"tahmin sıcaklık meteoroloji"
            )
        else:
            arama_sorgusu = sorgu

        encoded_query = urllib.parse.quote_plus(
            arama_sorgusu
        )

        url = (
            "https://html.duckduckgo.com/html/?q="
            + encoded_query
        )

        html_icerik = guvenli_istek(
            url,
            timeout=10
        )

        bulunan_metinler = []

        snippetler = re.findall(
            r'class="result__snippet[^"]*"'
            r'[^>]*>(.*?)</(?:a|div)>',
            html_icerik,
            flags=re.IGNORECASE | re.DOTALL
        )

        for snip in snippetler[:8]:
            temiz = html_temizle(
                snip
            )

            if (
                len(temiz) > 20
                and temiz not in bulunan_metinler
            ):
                bulunan_metinler.append(
                    temiz
                )

        if bulunan_metinler:
            birlesmis_ozet = " ".join(
                bulunan_metinler[:5]
            )

            return (
                "Canlı Web Araştırma Özeti:\n\n"
                "• "
                + birlesmis_ozet
            )

        return duckduckgo_api_arama(
            sorgu
        )

    except Exception as e:
        return (
            "Arama sırasında bağlantı hatası oluştu: "
            f"{e}"
        )


def duckduckgo_api_arama(sorgu):
    try:
        encoded_query = urllib.parse.quote_plus(
            sorgu
        )

        api_url = (
            "https://api.duckduckgo.com/"
            "?q="
            + encoded_query
            + "&format=json"
            "&no_html=1"
            "&skip_disambig=1"
        )

        api_req = urllib.request.Request(
            api_url,
            headers={
                "User-Agent":
                    "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            api_req,
            timeout=8
        ) as api_resp:

            api_veri = json.loads(
                api_resp.read().decode(
                    "utf-8",
                    errors="replace"
                )
            )

        ozet = api_veri.get(
            "AbstractText",
            ""
        )

        ilgili_konular = api_veri.get(
            "RelatedTopics",
            []
        )

        sonuc_metni = []

        if ozet:
            sonuc_metni.append(
                ozet
            )

        for konu in ilgili_konular:
            if (
                isinstance(konu, dict)
                and "Text" in konu
            ):
                sonuc_metni.append(
                    konu["Text"]
                )

        if sonuc_metni:
            return (
                "Canlı Veritabanı Özeti:\n\n"
                "• "
                + " ".join(
                    sonuc_metni[:3]
                )
            )

        return (
            f"'{sorgu}' hakkında güncel kaynaklardan "
            "anlamlı bir veri çıkarılamadı."
        )

    except Exception as e:
        return (
            "Yedek arama sistemi de sonuç veremedi.\n"
            f"Hata: {e}"
        )


def canli_arastir(
    sorgu,
    kod_modu_aktif=False
):
    if kod_modu_aktif:
        return github_arastir(
            sorgu
        )

    return normal_web_arastir(
        sorgu
    )


hafiza = json_yukle(
    HAFIZA_DOSYASI
)

gecmis = json_yukle(
    GECMIS_DOSYASI
)

ses_ayari = json_yukle(
    SES_AYAR_DOSYASI
)


class TarayiciDisplayHandler:

    def __init__(
        self,
        uygulama
    ):
        self.uygulama = uygulama

    def OnAddressChange(
        self,
        browser,
        frame,
        url
    ):
        try:
            if frame.IsMain():
                self.uygulama.root.after(
                    0,
                    lambda u=url:
                    self.uygulama.tarayici_url_guncelle(
                        u
                    )
                )
        except Exception:
            pass

    def OnTitleChange(
        self,
        browser,
        title
    ):
        try:
            self.uygulama.root.after(
                0,
                lambda t=title:
                self.uygulama.tarayici_baslik_guncelle(
                    t
                )
            )
        except Exception:
            pass


class YapayZekaUygulamasi:

    def __init__(
        self,
        root
    ):

        self.root = root

        self.root.overrideredirect(
            True
        )

        self.root.geometry(
            "1100x720+80+50"
        )

        self.root.minsize(
            800,
            550
        )

        self.normal_bg_koyu = "#030405"
        self.normal_bg_acik = "#080A0D"
        self.normal_panel = "#0B0D11"
        self.normal_turkuaz = "#00A6AD"
        self.normal_turkuaz_acik = "#00DDE5"
        self.normal_yazi = "#FFFFFF"

        self.code_bg_koyu = "#020202"
        self.code_bg_acik = "#080808"
        self.code_panel = "#0C0C0C"
        self.code_kirmizi = "#B00018"
        self.code_kirmizi_acik = "#FF1833"
        self.code_yazi = "#FFFFFF"

        self.bg_koyu = self.normal_bg_koyu
        self.bg_acik = self.normal_bg_acik
        self.panel = self.normal_panel
        self.turkuaz = self.normal_turkuaz
        self.turkuaz_acik = self.normal_turkuaz_acik
        self.yazi_renk = self.normal_yazi

        self.root.configure(
            bg="#050505"
        )

        self.admin_modu = False
        self.sohbet_kod_modlari = {}
        self.codemod_aktif = False
        self.yazma_id = 0
        self.gecmis_acik = True
        self.tam_ekran = False
        self.ses_menu = None
        self.klavye_sesi_aktif = False
        self.pencere_buyuk = False
        self.uygulama_kapaniyor = False

        self.pencere_normal_x = 80
        self.pencere_normal_y = 50
        self.pencere_normal_w = 1100
        self.pencere_normal_h = 720

        self.titlebar_drag_x = 0
        self.titlebar_drag_y = 0
        self.titlebar_baslangic_x = 0
        self.titlebar_baslangic_y = 0

        self.sekmeler = {}
        self.sekme_butonlari = {}

        self.tarayici_acik = False
        self.tarayici_frame = None
        self.tarayici_alan = None
        self.tarayici_browser = None
        self.tarayici_adres = None
        self.tarayici_tab_bar = None
        self.tarayici_resize = None
        self.tarayici_ust = None

        self.tarayici_min_genislik = 500
        self.tarayici_min_yukseklik = 300

        self.tarayici_genislik = 760
        self.tarayici_yukseklik = 500

        self.tarayici_x = 30
        self.tarayici_y = 20

        self.tarayici_normal_x = 30
        self.tarayici_normal_y = 20
        self.tarayici_normal_w = 760
        self.tarayici_normal_h = 500

        self.tarayici_buyuk = False

        self.tarayici_resize_x = 0
        self.tarayici_resize_y = 0
        self.tarayici_resize_w = 760
        self.tarayici_resize_h = 500

        self.tarayici_drag_x = 0
        self.tarayici_drag_y = 0
        self.tarayici_drag_baslangic_x = 0
        self.tarayici_drag_baslangic_y = 0
        self.tarayici_surukleniyor = False

        self.tarayici_sekmeleri = []
        self.tarayici_aktif_sekme = 0
        self.tarayici_sekme_butonlari = {}

        self.tarayici_son_url = (
            "https://www.google.com/"
        )

        self.tarayici_kapaliyken_sekmeler = [
            {
                "url":
                    "https://www.google.com/",
                "isim":
                    "Google"
            }
        ]

        self.cef_dongu_basladi = False

        self.tarayici_durumunu_yukle()

        try:
            self.ses_seviyesi = int(
                ses_ayari.get(
                    "ses",
                    35
                )
            )
        except Exception:
            self.ses_seviyesi = 35

        self.ses_seviyesi = max(
            0,
            min(
                100,
                self.ses_seviyesi
            )
        )

        self.ses_seviyesini_uygula()

        self.aktif_oturum = datetime.now().strftime(
            "Sohbet - %H:%M %d.%m"
        )

        while self.aktif_oturum in gecmis:
            self.aktif_oturum = datetime.now().strftime(
                "Sohbet - %H:%M:%S %d.%m"
            )

        if self.aktif_oturum not in gecmis:
            gecmis[
                self.aktif_oturum
            ] = []

        self.sohbet_kod_modlari[
            self.aktif_oturum
        ] = False

        self.baslik_cubugu_olustur()

        self.ana_frame = tk.Frame(
            self.root,
            bg=self.bg_koyu
        )

        self.ana_frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        self.sol_frame = tk.Frame(
            self.ana_frame,
            bg=self.bg_acik,
            width=240
        )

        self.sol_frame.pack(
            side=tk.LEFT,
            fill=tk.Y
        )

        self.sol_frame.pack_propagate(
            False
        )

        self.gecmis_baslik = tk.Label(
            self.sol_frame,
            text="💬 Sohbet Geçmişi",
            bg=self.bg_acik,
            fg="#FFFFFF",
            font=(
                "Segoe UI",
                11,
                "bold"
            )
        )

        self.gecmis_baslik.pack(
            pady=15
        )

        self.gecmis_liste = tk.Listbox(
            self.sol_frame,
            bg="#050609",
            fg="#FFFFFF",
            font=(
                "Segoe UI",
                9
            ),
            bd=0,
            highlightthickness=1,
            highlightbackground="#151820",
            highlightcolor=self.turkuaz,
            selectbackground=self.turkuaz,
            selectforeground="#000000"
        )

        self.gecmis_liste.pack(
            fill=tk.BOTH,
            expand=True,
            padx=12,
            pady=(0, 15)
        )

        self.gecmis_liste.bind(
            "<<ListboxSelect>>",
            self.eski_sohbeti_yukle
        )

        self.gecmis_liste.bind(
            "<Double-Button-1>",
            self.sohbet_ismini_degistir
        )

        self.sag_frame = tk.Frame(
            self.ana_frame,
            bg=self.bg_koyu
        )

        self.sag_frame.pack(
            side=tk.RIGHT,
            fill=tk.BOTH,
            expand=True
        )

        self.ust_bar = tk.Frame(
            self.sag_frame,
            bg=self.bg_acik,
            height=70
        )

        self.ust_bar.pack(
            fill=tk.X
        )

        self.ust_bar.pack_propagate(
            False
        )

        self.ust_komutlar = tk.Frame(
            self.ust_bar,
            bg=self.bg_acik
        )

        self.ust_komutlar.pack(
            fill=tk.X,
            padx=12,
            pady=(8, 4)
        )

        self.gecmis_toggle_btn = self.buton_olustur(
            self.ust_komutlar,
            "☰ Geçmiş",
            self.gecmis_paneli_ac_kapat
        )

        self.gecmis_toggle_btn.pack(
            side=tk.LEFT,
            padx=(0, 6),
            ipady=4
        )

        self.yeni_sohbet_btn = self.buton_olustur(
            self.ust_komutlar,
            "＋ Yeni Sohbet",
            self.yeni_sohbet
        )

        self.yeni_sohbet_btn.pack(
            side=tk.LEFT,
            padx=6,
            ipady=4
        )

        self.sil_sohbet_btn = self.buton_olustur(
            self.ust_komutlar,
            "🗑 Sohbet Sil",
            self.sohbet_sil
        )

        self.sil_sohbet_btn.pack(
            side=tk.LEFT,
            padx=6,
            ipady=4
        )

        self.kaydet_btn = self.buton_olustur(
            self.ust_komutlar,
            "💾 Kaydet",
            self.aktif_sohbeti_kaydet
        )

        self.kaydet_btn.pack(
            side=tk.LEFT,
            padx=6,
            ipady=4
        )

        self.tam_ekran_btn = self.buton_olustur(
            self.ust_komutlar,
            "⛶ Tam Ekran",
            self.tam_ekran_degistir
        )

        self.tam_ekran_btn.pack(
            side=tk.LEFT,
            padx=6,
            ipady=4
        )

        self.web_site_btn = self.buton_olustur(
            self.ust_komutlar,
            "🌐 Web Sitem",
            self.web_sitesini_ac
        )

        self.web_site_btn.pack(
            side=tk.LEFT,
            padx=6,
            ipady=4
        )

        self.tarayici_btn = self.buton_olustur(
            self.ust_komutlar,
            "🌐 Tarayıcı",
            self.tarayici_toggle
        )

        self.tarayici_btn.pack(
            side=tk.LEFT,
            padx=6,
            ipady=4
        )

        self.ses_btn = self.buton_olustur(
            self.ust_komutlar,
            "🔊 Ses",
            self.ses_menusu_toggle
        )

        self.ses_btn.pack(
            side=tk.LEFT,
            padx=6,
            ipady=4
        )

        self.baslik = tk.Label(
            self.ust_komutlar,
            text="✨ ASİSTAN | CodeMod: KAPALI",
            bg=self.bg_acik,
            fg="#FFFFFF",
            font=(
                "Segoe UI",
                9,
                "bold"
            )
        )

        self.baslik.pack(
            side=tk.RIGHT,
            padx=(8, 4)
        )

        self.ust_cizgi = tk.Frame(
            self.ust_bar,
            bg=self.turkuaz_acik,
            height=3
        )

        self.ust_cizgi.pack(
            side=tk.BOTTOM,
            fill=tk.X
        )

        self.sekme_bar = tk.Frame(
            self.sag_frame,
            bg="#050609",
            height=38
        )

        self.sekme_bar.pack(
            fill=tk.X
        )

        self.sekme_bar.pack_propagate(
            False
        )

        self.sekme_icerik = tk.Frame(
            self.sekme_bar,
            bg="#050609"
        )

        self.sekme_icerik.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        self.sekme_yeni_btn = tk.Button(
            self.sekme_bar,
            text="＋",
            command=self.yeni_sekme,
            bg=self.turkuaz,
            fg="#000000",
            activebackground=self.turkuaz_acik,
            activeforeground="#000000",
            relief=tk.FLAT,
            bd=0,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2",
            width=4
        )

        self.sekme_yeni_btn.pack(
            side=tk.RIGHT,
            padx=5,
            pady=5
        )

        self.sohbet_alani = scrolledtext.ScrolledText(
            self.sag_frame,
            wrap=tk.WORD,
            font=(
                "Consolas",
                11
            ),
            bg="#030405",
            fg="#FFFFFF",
            bd=0,
            highlightthickness=1,
            highlightbackground="#11151B",
            highlightcolor="#151A20",
            padx=15,
            pady=15,
            insertbackground="#FFFFFF"
        )

        self.sohbet_alani.pack(
            padx=15,
            pady=15,
            fill=tk.BOTH,
            expand=True
        )

        self.sohbet_alani.config(
            state=tk.DISABLED
        )

        self.sohbet_alani.tag_config(
            "kullanici",
            foreground="#FFFFFF"
        )

        self.sohbet_alani.tag_config(
            "bot",
            foreground="#FFFFFF"
        )

        self.sohbet_alani.tag_config(
            "sistem",
            foreground="#FF3048"
        )

        self.alt_frame = tk.Frame(
            self.sag_frame,
            bg=self.bg_koyu
        )

        self.alt_frame.pack(
            padx=15,
            pady=(0, 15),
            fill=tk.X
        )

        self.giris_kutusu = tk.Entry(
            self.alt_frame,
            font=(
                "Segoe UI",
                12
            ),
            bg="#090B0F",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            bd=0,
            highlightthickness=1,
            highlightbackground="#171B22",
            highlightcolor=self.turkuaz,
            relief=tk.FLAT
        )

        self.giris_kutusu.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(0, 10),
            ipady=8,
            ipadx=10
        )

        self.giris_kutusu.bind(
            "<Return>",
            lambda event:
            self.mesaj_gonder()
        )

        self.gonder_butonu = self.buton_olustur(
            self.alt_frame,
            "ARA / GÖNDER 🚀",
            self.mesaj_gonder,
            buyuk=True
        )

        self.gonder_butonu.pack(
            side=tk.RIGHT,
            ipady=4
        )

        self.gecmis_listesini_guncelle()
        self.sekmeleri_guncelle()

        self.root.bind(
            "<Map>",
            self.pencere_map
        )

        self.root.after(
            150,
            self.ana_pencere_sinirla
        )

        if not gecmis[
            self.aktif_oturum
        ]:
            self.mesaja_yaz(
                "Yapay Zeka",
                "Sistem hazır! GitHub, web ve CodeMod sistemleri hazır."
            )

    def baslik_cubugu_olustur(self):

        self.titlebar = tk.Frame(
            self.root,
            bg="#0D0D0D",
            height=36
        )

        self.titlebar.pack(
            fill=tk.X
        )

        self.titlebar.pack_propagate(
            False
        )

        self.title_label = tk.Label(
            self.titlebar,
            text="  🤖 Canlı Araştırma Asistanı",
            bg="#0D0D0D",
            fg="#E5E5E5",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            anchor="w"
        )

        self.title_label.pack(
            side=tk.LEFT,
            fill=tk.Y,
            expand=True
        )

        self.title_label.bind(
            "<Button-1>",
            self.pencere_surukle_baslat
        )

        self.title_label.bind(
            "<B1-Motion>",
            self.pencere_surukle
        )

        self.title_label.bind(
            "<ButtonRelease-1>",
            self.pencere_surukle_bitir
        )

        self.titlebar.bind(
            "<Button-1>",
            self.pencere_surukle_baslat
        )

        self.titlebar.bind(
            "<B1-Motion>",
            self.pencere_surukle
        )

        self.min_btn = tk.Button(
            self.titlebar,
            text="—",
            command=self.pencere_kucult,
            bg="#111111",
            fg="#E0E0E0",
            activebackground="#222222",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            width=5,
            font=(
                "Segoe UI",
                10
            ),
            cursor="hand2"
        )

        self.min_btn.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.max_btn = tk.Button(
            self.titlebar,
            text="□",
            command=self.pencere_buyut_kucult,
            bg="#111111",
            fg="#E0E0E0",
            activebackground="#222222",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            width=5,
            font=(
                "Segoe UI",
                10
            ),
            cursor="hand2"
        )

        self.max_btn.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.close_btn = tk.Button(
            self.titlebar,
            text="✕",
            command=self.uygulama_kapat,
            bg="#111111",
            fg="#E0E0E0",
            activebackground="#7A1515",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            width=5,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        )

        self.close_btn.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.min_btn.bind(
            "<Enter>",
            lambda e:
            self.min_btn.config(
                bg="#202020"
            )
        )

        self.min_btn.bind(
            "<Leave>",
            lambda e:
            self.min_btn.config(
                bg="#111111"
            )
        )

        self.max_btn.bind(
            "<Enter>",
            lambda e:
            self.max_btn.config(
                bg="#202020"
            )
        )

        self.max_btn.bind(
            "<Leave>",
            lambda e:
            self.max_btn.config(
                bg="#111111"
            )
        )

        self.close_btn.bind(
            "<Enter>",
            lambda e:
            self.close_btn.config(
                bg="#7A1515"
            )
        )

        self.close_btn.bind(
            "<Leave>",
            lambda e:
            self.close_btn.config(
                bg="#111111"
            )
        )

    def pencere_map(
        self,
        event=None
    ):

        if self.uygulama_kapaniyor:
            return

        try:
            if self.root.state() == "normal":
                self.root.after(
                    20,
                    lambda:
                    self.root.overrideredirect(True)
                )
        except Exception:
            pass

    def ana_pencere_sinirla(self):

        if self.pencere_buyuk or self.tam_ekran:
            return

        try:
            ekran_w = self.root.winfo_screenwidth()
            ekran_h = self.root.winfo_screenheight()

            self.root.update_idletasks()

            mevcut_w = self.root.winfo_width()
            mevcut_h = self.root.winfo_height()

            max_w = max(
                800,
                ekran_w - 20
            )

            max_h = max(
                550,
                ekran_h - 60
            )

            yeni_w = min(
                mevcut_w,
                max_w
            )

            yeni_h = min(
                mevcut_h,
                max_h
            )

            x = self.root.winfo_x()
            y = self.root.winfo_y()

            x = max(
                0,
                min(
                    x,
                    ekran_w - yeni_w
                )
            )

            y = max(
                0,
                min(
                    y,
                    ekran_h - yeni_h
                )
            )

            if (
                yeni_w != mevcut_w
                or yeni_h != mevcut_h
                or x != self.root.winfo_x()
                or y != self.root.winfo_y()
            ):
                self.root.geometry(
                    f"{yeni_w}x{yeni_h}+{x}+{y}"
                )

        except Exception:
            pass

    def pencere_surukle_baslat(
        self,
        event
    ):

        if self.pencere_buyuk:
            return

        self.titlebar_drag_x = event.x_root
        self.titlebar_drag_y = event.y_root

        self.root.update_idletasks()

        self.titlebar_baslangic_x = (
            self.root.winfo_x()
        )

        self.titlebar_baslangic_y = (
            self.root.winfo_y()
        )

    def pencere_surukle(
        self,
        event
    ):

        if self.pencere_buyuk or self.tam_ekran:
            return

        fark_x = (
            event.x_root
            - self.titlebar_drag_x
        )

        fark_y = (
            event.y_root
            - self.titlebar_drag_y
        )

        yeni_x = (
            self.titlebar_baslangic_x
            + fark_x
        )

        yeni_y = (
            self.titlebar_baslangic_y
            + fark_y
        )

        ekran_w = self.root.winfo_screenwidth()
        ekran_h = self.root.winfo_screenheight()

        pencere_w = self.root.winfo_width()
        pencere_h = self.root.winfo_height()

        yeni_x = max(
            0,
            min(
                yeni_x,
                ekran_w - pencere_w
            )
        )

        yeni_y = max(
            0,
            min(
                yeni_y,
                ekran_h - pencere_h
            )
        )

        self.root.geometry(
            f"+{int(yeni_x)}+{int(yeni_y)}"
        )

    def pencere_surukle_bitir(
        self,
        event
    ):
        self.ana_pencere_sinirla()

    def pencere_kucult(self):

        try:
            self.root.overrideredirect(
                False
            )

            self.root.iconify()

        except Exception:
            pass

    def pencere_buyut_kucult(self):

        if self.tam_ekran:
            return

        if not self.pencere_buyuk:

            self.root.update_idletasks()

            self.pencere_normal_x = (
                self.root.winfo_x()
            )

            self.pencere_normal_y = (
                self.root.winfo_y()
            )

            self.pencere_normal_w = (
                self.root.winfo_width()
            )

            self.pencere_normal_h = (
                self.root.winfo_height()
            )

            ekran_w = self.root.winfo_screenwidth()
            ekran_h = self.root.winfo_screenheight()

            self.root.geometry(
                f"{ekran_w}x{ekran_h}+0+0"
            )

            self.pencere_buyuk = True

            self.max_btn.config(
                text="❐"
            )

        else:

            self.root.geometry(
                f"{self.pencere_normal_w}x"
                f"{self.pencere_normal_h}+"
                f"{self.pencere_normal_x}+"
                f"{self.pencere_normal_y}"
            )

            self.pencere_buyuk = False

            self.max_btn.config(
                text="□"
            )

            self.root.after(
                50,
                self.ana_pencere_sinirla
            )

        self.root.after(
            100,
            self.tarayici_sinirla
        )

        self.root.after(
            150,
            self.tarayici_browser_boyutlandir
        )

    def uygulama_kapat(self):

        if self.uygulama_kapaniyor:
            return

        self.uygulama_kapaniyor = True

        try:
            self.tarayici_durumunu_kaydet()
        except Exception:
            pass

        try:
            self.tarayici_kapat(
                uygulamayi_kapat=True
            )
        except Exception:
            pass

        try:
            cef_kapat()
        except Exception:
            pass

        try:
            self.root.destroy()
        except Exception:
            pass

    def buton_olustur(
        self,
        parent,
        metin,
        komut,
        buyuk=False
    ):

        dis = tk.Frame(
            parent,
            bg="#000000",
            padx=1,
            pady=1
        )

        btn = tk.Button(
            dis,
            text=metin,
            bg=self.turkuaz,
            fg="#000000",
            activebackground=self.turkuaz_acik,
            activeforeground="#000000",
            font=(
                "Segoe UI",
                9 if not buyuk else 10,
                "bold"
            ),
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=12 if not buyuk else 20,
            pady=5 if not buyuk else 8,
            command=komut
        )

        btn.pack()

        btn.bind(
            "<Enter>",
            lambda e, b=btn:
            self.buton_hover(
                b,
                True
            )
        )

        btn.bind(
            "<Leave>",
            lambda e, b=btn:
            self.buton_hover(
                b,
                False
            )
        )

        return dis

    def buton_hover(
        self,
        buton,
        aktif
    ):

        if self.codemod_aktif:
            buton.config(
                bg=(
                    self.code_kirmizi_acik
                    if aktif
                    else self.code_kirmizi
                ),
                fg="#FFFFFF"
            )

        else:
            buton.config(
                bg=(
                    self.normal_turkuaz_acik
                    if aktif
                    else self.normal_turkuaz
                ),
                fg="#000000"
            )

    def ses_seviyesini_uygula(self):

        try:
            oran = (
                self.ses_seviyesi
                / 100.0
            )

            deger = int(
                65535 * oran
            )

            stereo_deger = (
                deger
                | (deger << 16)
            )

            ctypes.windll.winmm.waveOutSetVolume(
                0xFFFFFFFF,
                stereo_deger
            )

        except Exception:
            pass

    def ses_ayarini_kaydet(self):

        json_kaydet(
            SES_AYAR_DOSYASI,
            {
                "ses":
                    self.ses_seviyesi
            }
        )

    def ses_degistir(
        self,
        deger
    ):

        try:
            self.ses_seviyesi = int(
                float(deger)
            )
        except Exception:
            return

        self.ses_seviyesi = max(
            0,
            min(
                100,
                self.ses_seviyesi
            )
        )

        self.ses_seviyesini_uygula()
        self.ses_ayarini_kaydet()

        if hasattr(
            self,
            "ses_deger_label"
        ):
            self.ses_deger_label.config(
                text=f"%{self.ses_seviyesi}"
            )

    def ses_menusu_toggle(self):

        if (
            self.ses_menu
            and self.ses_menu.winfo_exists()
        ):

            self.ses_menu.destroy()
            self.ses_menu = None
            return

        self.ses_menu = tk.Toplevel(
            self.root
        )

        pencere = self.ses_menu

        pencere.overrideredirect(
            True
        )

        pencere.configure(
            bg="#000000"
        )

        ana = tk.Frame(
            pencere,
            bg="#090B0F",
            highlightthickness=1,
            highlightbackground=(
                self.code_kirmizi
                if self.codemod_aktif
                else "#171D24"
            )
        )

        ana.pack(
            padx=1,
            pady=1
        )

        baslik = tk.Label(
            ana,
            text="🔊  SES",
            bg="#090B0F",
            fg="#FFFFFF",
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        )

        baslik.pack(
            padx=15,
            pady=(12, 5)
        )

        self.ses_deger_label = tk.Label(
            ana,
            text=f"%{self.ses_seviyesi}",
            bg="#090B0F",
            fg="#FFFFFF",
            font=(
                "Segoe UI",
                9,
                "bold"
            )
        )

        self.ses_deger_label.pack(
            pady=(0, 5)
        )

        self.ses_slider = tk.Scale(
            ana,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            resolution=1,
            showvalue=False,
            bg="#090B0F",
            fg="#FFFFFF",
            troughcolor="#181B20",
            activebackground=(
                self.code_kirmizi
                if self.codemod_aktif
                else self.normal_turkuaz
            ),
            highlightthickness=0,
            bd=0,
            length=250,
            sliderlength=18,
            width=10,
            command=self.ses_degistir
        )

        self.ses_slider.set(
            self.ses_seviyesi
        )

        self.ses_slider.pack(
            padx=15,
            pady=(3, 10)
        )

        x = self.ses_btn.winfo_rootx()

        y = (
            self.ses_btn.winfo_rooty()
            + self.ses_btn.winfo_height()
            + 5
        )

        pencere.geometry(
            f"+{x}+{y}"
        )

        pencere.bind(
            "<FocusOut>",
            lambda e:
            self.ses_menu_kapat()
        )

        pencere.focus_force()

    def ses_menu_kapat(self):

        if (
            self.ses_menu
            and self.ses_menu.winfo_exists()
        ):

            self.ses_menu.destroy()
            self.ses_menu = None

    def ses_durdur(self):

        try:
            winsound.PlaySound(
                None,
                winsound.SND_PURGE
            )
        except Exception:
            pass

        self.klavye_sesi_aktif = False

    def klavye_sesini_baslat(self):

        if self.klavye_sesi_aktif:
            return

        if not self.codemod_aktif:
            return

        if not os.path.exists(
            KLAVYE_SESI
        ):
            return

        if self.ses_seviyesi <= 0:
            return

        try:

            self.ses_seviyesini_uygula()

            winsound.PlaySound(
                KLAVYE_SESI,
                winsound.SND_FILENAME
                | winsound.SND_ASYNC
                | winsound.SND_LOOP
            )

            self.klavye_sesi_aktif = True

        except Exception:
            self.klavye_sesi_aktif = False

    def klavye_sesini_durdur(self):

        if not self.klavye_sesi_aktif:
            return

        try:
            winsound.PlaySound(
                None,
                winsound.SND_PURGE
            )
        except Exception:
            pass

        self.klavye_sesi_aktif = False

    def tam_ekran_degistir(self):

        if self.tam_ekran:

            self.tam_ekran = False

            self.root.geometry(
                f"{self.pencere_normal_w}x"
                f"{self.pencere_normal_h}+"
                f"{self.pencere_normal_x}+"
                f"{self.pencere_normal_y}"
            )

            self.tam_ekran_btn.winfo_children()[0].config(
                text="⛶ Tam Ekran"
            )

        else:

            self.root.update_idletasks()

            self.pencere_normal_x = (
                self.root.winfo_x()
            )

            self.pencere_normal_y = (
                self.root.winfo_y()
            )

            self.pencere_normal_w = (
                self.root.winfo_width()
            )

            self.pencere_normal_h = (
                self.root.winfo_height()
            )

            ekran_w = self.root.winfo_screenwidth()
            ekran_h = self.root.winfo_screenheight()

            self.root.geometry(
                f"{ekran_w}x{ekran_h}+0+0"
            )

            self.tam_ekran = True

            self.tam_ekran_btn.winfo_children()[0].config(
                text="⛶ Pencere Modu"
            )

        self.root.after(
            100,
            self.tarayici_sinirla
        )

        self.root.after(
            150,
            self.tarayici_browser_boyutlandir
        )

    def web_sitesini_ac(self):

        webbrowser.open_new_tab(
            WEB_SITESI_URL
        )

    def sekmeleri_guncelle(self):

        for widget in self.sekme_icerik.winfo_children():
            widget.destroy()

        self.sekme_butonlari = {}

        for oturum_adi in gecmis.keys():

            isim = oturum_adi

            if len(isim) > 22:
                isim = (
                    isim[:22]
                    + "..."
                )

            aktif = (
                oturum_adi
                == self.aktif_oturum
            )

            buton = tk.Button(
                self.sekme_icerik,
                text=(
                    "● " + isim
                    if aktif
                    else isim
                ),
                command=lambda x=oturum_adi:
                self.sekme_ac(x),
                bg=(
                    self.turkuaz
                    if aktif
                    else "#101318"
                ),
                fg=(
                    "#000000"
                    if aktif
                    else "#FFFFFF"
                ),
                activebackground=self.turkuaz_acik,
                activeforeground="#000000",
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=5,
                font=(
                    "Segoe UI",
                    8,
                    "bold"
                ),
                cursor="hand2"
            )

            buton.pack(
                side=tk.LEFT,
                padx=2,
                pady=4
            )

            self.sekme_butonlari[
                oturum_adi
            ] = buton

    def sekme_ac(
        self,
        oturum_adi
    ):

        if oturum_adi not in gecmis:
            return

        self.aktif_oturum = oturum_adi

        sohbet_modu = (
            self.sohbet_kod_modlari.get(
                oturum_adi,
                False
            )
        )

        if sohbet_modu:
            self.codemod_ac()
        else:
            self.codemod_kapat()

        self.sohbet_alani.config(
            state=tk.NORMAL
        )

        self.sohbet_alani.delete(
            1.0,
            tk.END
        )

        for mesaj in gecmis[
            oturum_adi
        ]:

            if mesaj.startswith(
                "Sistem:"
            ):
                tag = "sistem"
            elif mesaj.startswith(
                "Sen:"
            ):
                tag = "kullanici"
            else:
                tag = "bot"

            self.sohbet_alani.insert(
                tk.END,
                mesaj + "\n\n",
                tag
            )

        self.sohbet_alani.see(
            tk.END
        )

        self.sohbet_alani.config(
            state=tk.DISABLED
        )

        self.gecmis_listesini_guncelle()
        self.sekmeleri_guncelle()

    def yeni_sekme(self):
        self.yeni_sohbet()

    def aktif_sohbeti_kaydet(self):

        if self.aktif_oturum not in gecmis:

            messagebox.showerror(
                "Kaydet",
                "Kaydedilecek sohbet bulunamadı."
            )

            return

        mesajlar = gecmis[
            self.aktif_oturum
        ]

        if not mesajlar:

            messagebox.showinfo(
                "Kaydet",
                "Bu sohbette kaydedilecek mesaj yok."
            )

            return

        guvenli_isim = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            self.aktif_oturum
        )

        dosya_yolu = os.path.join(
            kayit_klasoru,
            guvenli_isim + ".txt"
        )

        sayac = 2

        while os.path.exists(
            dosya_yolu
        ):

            dosya_yolu = os.path.join(
                kayit_klasoru,
                f"{guvenli_isim} ({sayac}).txt"
            )

            sayac += 1

        try:

            with open(
                dosya_yolu,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    "CANLI ARAŞTIRMA ASİSTANI\n"
                )

                f.write(
                    "========================\n\n"
                )

                f.write(
                    f"Sohbet: {self.aktif_oturum}\n"
                )

                f.write(
                    f"Kaydedilme: "
                    f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
                )

                for mesaj in mesajlar:
                    f.write(
                        mesaj
                        + "\n\n"
                    )

            messagebox.showinfo(
                "Kaydedildi",
                "Sohbet başarıyla kaydedildi.\n\n"
                + dosya_yolu
            )

        except Exception as e:

            messagebox.showerror(
                "Kaydetme Hatası",
                str(e)
            )

    def gecmis_paneli_ac_kapat(self):

        if self.gecmis_acik:

            self.sol_frame.pack_forget()

            self.gecmis_acik = False

            self.gecmis_toggle_btn.winfo_children()[0].config(
                text="☰ Geçmiş Aç"
            )

        else:

            self.sol_frame.pack(
                side=tk.LEFT,
                fill=tk.Y
            )

            self.gecmis_acik = True

            self.gecmis_toggle_btn.winfo_children()[0].config(
                text="☰ Geçmiş"
            )

        self.root.after(
            100,
            self.tarayici_sinirla
        )

    def tarayici_durumunu_yukle(self):

        veri = json_yukle(
            TARAYICI_DURUM_DOSYASI
        )

        if not isinstance(
            veri,
            dict
        ):
            veri = {}

        sekmeler = veri.get(
            "sekmeler",
            []
        )

        temiz_sekmeler = []

        if isinstance(
            sekmeler,
            list
        ):

            for sekme in sekmeler[:TARAYICI_MAKS_SEKME]:

                if not isinstance(
                    sekme,
                    dict
                ):
                    continue

                url = str(
                    sekme.get(
                        "url",
                        ""
                    )
                ).strip()

                if not url:
                    continue

                isim = str(
                    sekme.get(
                        "isim",
                        self.tarayici_basliktan_isim(
                            url
                        )
                    )
                )

                temiz_sekmeler.append({
                    "url": url,
                    "isim": isim
                })

        if not temiz_sekmeler:

            temiz_sekmeler = [
                {
                    "url":
                        "https://www.google.com/",
                    "isim":
                        "Google"
                }
            ]

        self.tarayici_sekmeleri = (
            temiz_sekmeler
        )

        try:
            aktif = int(
                veri.get(
                    "aktif_sekme",
                    0
                )
            )
        except Exception:
            aktif = 0

        if aktif < 0:
            aktif = 0

        if aktif >= len(
            self.tarayici_sekmeleri
        ):
            aktif = (
                len(
                    self.tarayici_sekmeleri
                ) - 1
            )

        self.tarayici_aktif_sekme = aktif

        son_url = str(
            veri.get(
                "son_url",
                ""
            )
        ).strip()

        if son_url:
            self.tarayici_son_url = (
                son_url
            )
        else:
            self.tarayici_son_url = (
                self.tarayici_sekmeleri[
                    self.tarayici_aktif_sekme
                ].get(
                    "url",
                    "https://www.google.com/"
                )
            )

    def tarayici_durumunu_kaydet(self):

        try:

            self.tarayici_mevcut_url_kaydet()

            if not self.tarayici_sekmeleri:
                self.tarayici_sekmeleri = [
                    {
                        "url":
                            self.tarayici_son_url
                            or "https://www.google.com/",
                        "isim":
                            "Google"
                    }
                ]

            veri = {
                "aktif_sekme":
                    self.tarayici_aktif_sekme,
                "son_url":
                    self.tarayici_son_url,
                "sekmeler":
                    self.tarayici_sekmeleri
            }

            json_kaydet(
                TARAYICI_DURUM_DOSYASI,
                veri
            )

        except Exception:
            pass

    def tarayici_toggle(self):

        if self.tarayici_acik:

            self.tarayici_kapat(
                uygulamayi_kapat=False
            )

        else:

            self.tarayici_ac()

    def tarayici_ac(self):

        if self.tarayici_acik:
            return

        if not CEF_VAR:

            messagebox.showerror(
                "Tarayıcı",
                "cefpython3 bulunamadı."
            )

            return

        self.tarayici_acik = True

        if not self.tarayici_sekmeleri:

            self.tarayici_sekmeleri = [
                {
                    "url":
                        self.tarayici_son_url
                        or "https://www.google.com/",
                    "isim":
                        self.tarayici_basliktan_isim(
                            self.tarayici_son_url
                            or "https://www.google.com/"
                        )
                }
            ]

            self.tarayici_aktif_sekme = 0

        if self.tarayici_frame is not None:

            self.tarayici_frame.place(
                x=int(
                    self.tarayici_x
                ),
                y=int(
                    self.tarayici_y
                ),
                width=int(
                    self.tarayici_genislik
                ),
                height=int(
                    self.tarayici_yukseklik
                )
            )

            self.tarayici_sinirla()

            if self.tarayici_browser is not None:

                try:

                    url = self.tarayici_sekmeleri[
                        self.tarayici_aktif_sekme
                    ].get(
                        "url",
                        self.tarayici_son_url
                    )

                    if self.tarayici_adres is not None:

                        self.tarayici_adres.delete(
                            0,
                            tk.END
                        )

                        self.tarayici_adres.insert(
                            0,
                            url
                        )

                    self.tarayici_browser.SetFocus(
                        True
                    )

                    self.root.after(
                        50,
                        self.tarayici_browser_boyutlandir
                    )

                except Exception:
                    pass

            return

        self.tarayici_frame = tk.Frame(
            self.sag_frame,
            bg="#000000",
            highlightthickness=2,
            highlightbackground=self.turkuaz
        )

        self.tarayici_frame.place(
            x=int(
                self.tarayici_x
            ),
            y=int(
                self.tarayici_y
            ),
            width=int(
                self.tarayici_genislik
            ),
            height=int(
                self.tarayici_yukseklik
            )
        )

        self.tarayici_frame.bind(
            "<Configure>",
            lambda event:
            self.root.after_idle(
                self.tarayici_browser_boyutlandir
            )
        )

        self.tarayici_ust = tk.Frame(
            self.tarayici_frame,
            bg="#090A0B",
            height=42
        )

        self.tarayici_ust.pack(
            side=tk.TOP,
            fill=tk.X
        )

        self.tarayici_ust.pack_propagate(
            False
        )

        self.tarayici_drag_label = tk.Label(
            self.tarayici_ust,
            text="⋮⋮",
            bg="#090A0B",
            fg="#777777",
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            cursor="fleur"
        )

        self.tarayici_drag_label.pack(
            side=tk.LEFT,
            padx=(5, 2)
        )

        self.tarayici_drag_label.bind(
            "<Button-1>",
            self.tarayici_surukleme_baslat
        )

        self.tarayici_drag_label.bind(
            "<B1-Motion>",
            self.tarayici_surukleme_hareket
        )

        self.tarayici_drag_label.bind(
            "<ButtonRelease-1>",
            self.tarayici_surukleme_bitir
        )

        geri_btn = tk.Button(
            self.tarayici_ust,
            text="←",
            command=self.tarayici_geri,
            bg="#111111",
            fg="#DDDDDD",
            activebackground="#242424",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            width=3
        )

        geri_btn.pack(
            side=tk.LEFT,
            padx=2,
            pady=5
        )

        ileri_btn = tk.Button(
            self.tarayici_ust,
            text="→",
            command=self.tarayici_ileri,
            bg="#111111",
            fg="#DDDDDD",
            activebackground="#242424",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            width=3
        )

        ileri_btn.pack(
            side=tk.LEFT,
            padx=2,
            pady=5
        )

        yenile_btn = tk.Button(
            self.tarayici_ust,
            text="↻",
            command=self.tarayici_yenile,
            bg="#111111",
            fg="#DDDDDD",
            activebackground="#242424",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            width=3
        )

        yenile_btn.pack(
            side=tk.LEFT,
            padx=2,
            pady=5
        )

        self.tarayici_adres = tk.Entry(
            self.tarayici_ust,
            bg="#050505",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            bd=0,
            relief=tk.FLAT,
            font=(
                "Segoe UI",
                9
            )
        )

        self.tarayici_adres.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=6,
            pady=7,
            ipady=5
        )

        self.tarayici_adres.bind(
            "<Return>",
            lambda event:
            self.tarayici_adres_ac()
        )

        self.tarayici_buyut_btn = tk.Button(
            self.tarayici_ust,
            text="□",
            command=self.tarayici_buyut_kucult,
            bg="#111111",
            fg="#DDDDDD",
            activebackground="#242424",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            font=(
                "Segoe UI",
                10
            ),
            width=3
        )

        self.tarayici_buyut_btn.pack(
            side=tk.RIGHT,
            padx=2,
            pady=5
        )

        kapat_btn = tk.Button(
            self.tarayici_ust,
            text="✕",
            command=self.tarayici_kapat,
            bg="#111111",
            fg="#DDDDDD",
            activebackground="#7A1515",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            width=3
        )

        kapat_btn.pack(
            side=tk.RIGHT,
            padx=(2, 5),
            pady=5
        )

        self.tarayici_tab_bar = tk.Frame(
            self.tarayici_frame,
            bg="#050505",
            height=32
        )

        self.tarayici_tab_bar.pack(
            side=tk.TOP,
            fill=tk.X
        )

        self.tarayici_tab_bar.pack_propagate(
            False
        )

        self.tarayici_alan = tk.Frame(
            self.tarayici_frame,
            bg="#000000"
        )

        self.tarayici_alan.pack(
            fill=tk.BOTH,
            expand=True
        )

        self.tarayici_alan.bind(
            "<Configure>",
            lambda event:
            self.root.after_idle(
                self.tarayici_browser_boyutlandir
            )
        )

        self.tarayici_resize = tk.Label(
            self.tarayici_frame,
            text="◢",
            bg="#080A0D",
            fg=self.turkuaz_acik,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="size_nw_se"
        )

        self.tarayici_resize.place(
            relx=1.0,
            rely=1.0,
            anchor="se",
            width=22,
            height=22
        )

        self.tarayici_resize.bind(
            "<Button-1>",
            self.tarayici_resize_baslat
        )

        self.tarayici_resize.bind(
            "<B1-Motion>",
            self.tarayici_resize_hareket
        )

        self.tarayici_resize.bind(
            "<ButtonRelease-1>",
            self.tarayici_resize_bitir
        )

        self.tarayici_ust.bind(
            "<Double-Button-1>",
            lambda event:
            self.tarayici_buyut_kucult()
        )

        self.tarayici_sekmelerini_guncelle()

        self.root.after(
            100,
            self.tarayici_cef_baslat
        )

    def tarayici_sekmelerini_guncelle(self):

        if self.tarayici_tab_bar is None:
            return

        for widget in self.tarayici_tab_bar.winfo_children():
            widget.destroy()

        self.tarayici_sekme_butonlari = {}

        for index, sekme in enumerate(
            self.tarayici_sekmeleri
        ):

            aktif = (
                index
                == self.tarayici_aktif_sekme
            )

            isim = sekme.get(
                "isim",
                f"Sekme {index + 1}"
            )

            if len(isim) > 16:
                isim = (
                    isim[:16]
                    + "..."
                )

            tab_frame = tk.Frame(
                self.tarayici_tab_bar,
                bg=(
                    "#151515"
                    if aktif
                    else "#080808"
                )
            )

            tab_frame.pack(
                side=tk.LEFT,
                padx=(3, 0),
                pady=3
            )

            tab_btn = tk.Button(
                tab_frame,
                text=(
                    "● "
                    if aktif
                    else ""
                ) + isim,
                command=lambda i=index:
                self.tarayici_sekme_degistir(i),
                bg=(
                    "#191919"
                    if aktif
                    else "#090909"
                ),
                fg=(
                    "#FFFFFF"
                    if aktif
                    else "#AAAAAA"
                ),
                activebackground="#242424",
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                bd=0,
                padx=7,
                pady=2,
                font=(
                    "Segoe UI",
                    8,
                    "bold"
                ),
                cursor="hand2"
            )

            tab_btn.pack(
                side=tk.LEFT
            )

            kapat_tab_btn = tk.Button(
                tab_frame,
                text="×",
                command=lambda i=index:
                self.tarayici_sekme_kapat(i),
                bg=(
                    "#191919"
                    if aktif
                    else "#090909"
                ),
                fg="#888888",
                activebackground="#7A1515",
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                bd=0,
                padx=5,
                pady=2,
                font=(
                    "Segoe UI",
                    8,
                    "bold"
                ),
                cursor="hand2"
            )

            kapat_tab_btn.pack(
                side=tk.LEFT
            )

            self.tarayici_sekme_butonlari[
                index
            ] = tab_btn

        yeni_btn = tk.Button(
            self.tarayici_tab_bar,
            text="＋",
            command=self.tarayici_yeni_sekme,
            bg="#111111",
            fg="#DDDDDD",
            activebackground="#252525",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2",
            width=3
        )

        yeni_btn.pack(
            side=tk.LEFT,
            padx=4,
            pady=3
        )

    def tarayici_yeni_sekme(self):

        if len(
            self.tarayici_sekmeleri
        ) >= TARAYICI_MAKS_SEKME:

            messagebox.showinfo(
                "Tarayıcı",
                "En fazla 10 tarayıcı sekmesi açabilirsin.",
                parent=self.root
            )

            return

        self.tarayici_mevcut_url_kaydet()

        yeni_index = len(
            self.tarayici_sekmeleri
        )

        self.tarayici_sekmeleri.append(
            {
                "url":
                    "https://www.google.com/",
                "isim":
                    "Google"
            }
        )

        self.tarayici_aktif_sekme = (
            yeni_index
        )

        self.tarayici_durumunu_kaydet()
        self.tarayici_sekmelerini_guncelle()

        if self.tarayici_browser is not None:

            try:
                self.tarayici_browser.StopLoad()
            except Exception:
                pass

            try:
                self.tarayici_browser.LoadUrl(
                    "https://www.google.com/"
                )
            except Exception:
                pass

            self.tarayici_adres.delete(
                0,
                tk.END
            )

            self.tarayici_adres.insert(
                0,
                "https://www.google.com/"
            )

    def tarayici_mevcut_url_kaydet(self):

        if not self.tarayici_sekmeleri:
            return

        if (
            self.tarayici_browser is None
            and self.tarayici_adres is None
        ):
            return

        try:

            mevcut_url = ""

            if self.tarayici_browser is not None:

                try:
                    mevcut_url = (
                        self.tarayici_browser.GetUrl()
                    )
                except Exception:
                    pass

            if not mevcut_url and self.tarayici_adres is not None:

                try:
                    mevcut_url = (
                        self.tarayici_adres.get().strip()
                    )
                except Exception:
                    pass

            if mevcut_url:

                self.tarayici_sekmeleri[
                    self.tarayici_aktif_sekme
                ]["url"] = mevcut_url

                self.tarayici_son_url = (
                    mevcut_url
                )

        except Exception:
            pass

    def tarayici_url_guncelle(
        self,
        url
    ):

        if not url:
            return

        if not self.tarayici_sekmeleri:
            return

        try:

            self.tarayici_sekmeleri[
                self.tarayici_aktif_sekme
            ]["url"] = url

            self.tarayici_son_url = url

            if self.tarayici_adres is not None:

                self.tarayici_adres.delete(
                    0,
                    tk.END
                )

                self.tarayici_adres.insert(
                    0,
                    url
                )

            self.tarayici_durumunu_kaydet()

        except Exception:
            pass

    def tarayici_baslik_guncelle(
        self,
        baslik
    ):

        if not baslik:
            return

        if not self.tarayici_sekmeleri:
            return

        try:

            temiz_baslik = (
                str(baslik).strip()
            )

            if len(temiz_baslik) > 18:
                temiz_baslik = (
                    temiz_baslik[:18]
                    + "..."
                )

            self.tarayici_sekmeleri[
                self.tarayici_aktif_sekme
            ]["isim"] = temiz_baslik

            self.tarayici_sekmelerini_guncelle()

            self.tarayici_durumunu_kaydet()

        except Exception:
            pass

    def tarayici_sekme_degistir(
        self,
        index
    ):

        if index < 0:
            return

        if index >= len(
            self.tarayici_sekmeleri
        ):
            return

        self.tarayici_mevcut_url_kaydet()

        self.tarayici_aktif_sekme = index

        url = self.tarayici_sekmeleri[
            index
        ].get(
            "url",
            "https://www.google.com/"
        )

        self.tarayici_durumunu_kaydet()
        self.tarayici_sekmelerini_guncelle()

        if self.tarayici_browser is not None:

            try:
                self.tarayici_browser.LoadUrl(
                    url
                )
            except Exception:
                pass

            if self.tarayici_adres is not None:

                self.tarayici_adres.delete(
                    0,
                    tk.END
                )

                self.tarayici_adres.insert(
                    0,
                    url
                )

    def tarayici_sekme_kapat(
        self,
        index
    ):

        if index < 0:
            return

        if index >= len(
            self.tarayici_sekmeleri
        ):
            return

        self.tarayici_mevcut_url_kaydet()

        if len(
            self.tarayici_sekmeleri
        ) == 1:

            self.tarayici_kapat(
                uygulamayi_kapat=False
            )

            return

        del self.tarayici_sekmeleri[
            index
        ]

        if index < self.tarayici_aktif_sekme:
            self.tarayici_aktif_sekme -= 1

        elif index == self.tarayici_aktif_sekme:

            if self.tarayici_aktif_sekme >= len(
                self.tarayici_sekmeleri
            ):
                self.tarayici_aktif_sekme = (
                    len(self.tarayici_sekmeleri)
                    - 1
                )

        self.tarayici_durumunu_kaydet()
        self.tarayici_sekmelerini_guncelle()

        if self.tarayici_browser is not None:

            url = self.tarayici_sekmeleri[
                self.tarayici_aktif_sekme
            ].get(
                "url",
                "https://www.google.com/"
            )

            try:
                self.tarayici_browser.LoadUrl(
                    url
                )
            except Exception:
                pass

            if self.tarayici_adres is not None:

                self.tarayici_adres.delete(
                    0,
                    tk.END
                )

                self.tarayici_adres.insert(
                    0,
                    url
                )

    def tarayici_surukleme_baslat(
        self,
        event
    ):

        if self.tarayici_buyuk:
            return

        self.tarayici_surukleniyor = True

        self.tarayici_drag_x = (
            event.x_root
        )

        self.tarayici_drag_y = (
            event.y_root
        )

        self.tarayici_drag_baslangic_x = (
            self.tarayici_x
        )

        self.tarayici_drag_baslangic_y = (
            self.tarayici_y
        )

    def tarayici_surukleme_hareket(
        self,
        event
    ):

        if not self.tarayici_surukleniyor:
            return

        fark_x = (
            event.x_root
            - self.tarayici_drag_x
        )

        fark_y = (
            event.y_root
            - self.tarayici_drag_y
        )

        yeni_x = (
            self.tarayici_drag_baslangic_x
            + fark_x
        )

        yeni_y = (
            self.tarayici_drag_baslangic_y
            + fark_y
        )

        self.tarayici_konum_sinirla(
            yeni_x,
            yeni_y
        )

    def tarayici_surukleme_bitir(
        self,
        event
    ):

        self.tarayici_surukleniyor = False

    def tarayici_konum_sinirla(
        self,
        x,
        y
    ):

        if self.tarayici_frame is None:
            return

        self.sag_frame.update_idletasks()

        alan_w = (
            self.sag_frame.winfo_width()
        )

        alan_h = (
            self.sag_frame.winfo_height()
        )

        frame_w = (
            self.tarayici_frame.winfo_width()
        )

        frame_h = (
            self.tarayici_frame.winfo_height()
        )

        max_x = max(
            5,
            alan_w - frame_w - 5
        )

        max_y = max(
            5,
            alan_h - frame_h - 5
        )

        x = max(
            5,
            min(
                int(x),
                max_x
            )
        )

        y = max(
            5,
            min(
                int(y),
                max_y
            )
        )

        self.tarayici_x = x
        self.tarayici_y = y

        self.tarayici_frame.place_configure(
            x=int(x),
            y=int(y)
        )

        self.root.after_idle(
            self.tarayici_browser_boyutlandir
        )

    def tarayici_sinirla(self):

        if not self.tarayici_acik:
            return

        if self.tarayici_frame is None:
            return

        if self.tarayici_buyuk:
            self.tarayici_buyut_uygula()
            return

        self.sag_frame.update_idletasks()

        alan_w = (
            self.sag_frame.winfo_width()
        )

        alan_h = (
            self.sag_frame.winfo_height()
        )

        max_w = max(
            self.tarayici_min_genislik,
            alan_w - 10
        )

        max_h = max(
            self.tarayici_min_yukseklik,
            alan_h - 10
        )

        self.tarayici_genislik = min(
            self.tarayici_genislik,
            max_w
        )

        self.tarayici_yukseklik = min(
            self.tarayici_yukseklik,
            max_h
        )

        self.tarayici_frame.place_configure(
            width=int(
                self.tarayici_genislik
            ),
            height=int(
                self.tarayici_yukseklik
            )
        )

        self.tarayici_konum_sinirla(
            self.tarayici_x,
            self.tarayici_y
        )

        self.root.after_idle(
            self.tarayici_browser_boyutlandir
        )

    def tarayici_buyut_kucult(self):

        if not self.tarayici_acik:
            return

        if not self.tarayici_buyuk:

            self.tarayici_normal_x = (
                self.tarayici_x
            )

            self.tarayici_normal_y = (
                self.tarayici_y
            )

            self.tarayici_normal_w = (
                self.tarayici_frame.winfo_width()
            )

            self.tarayici_normal_h = (
                self.tarayici_frame.winfo_height()
            )

            self.tarayici_buyuk = True

            self.tarayici_buyut_btn.config(
                text="❐"
            )

            self.tarayici_buyut_uygula()

        else:

            self.tarayici_buyuk = False

            self.tarayici_x = (
                self.tarayici_normal_x
            )

            self.tarayici_y = (
                self.tarayici_normal_y
            )

            self.tarayici_genislik = (
                self.tarayici_normal_w
            )

            self.tarayici_yukseklik = (
                self.tarayici_normal_h
            )

            self.tarayici_buyut_btn.config(
                text="□"
            )

            self.tarayici_frame.place_configure(
                x=int(
                    self.tarayici_x
                ),
                y=int(
                    self.tarayici_y
                ),
                width=int(
                    self.tarayici_genislik
                ),
                height=int(
                    self.tarayici_yukseklik
                )
            )

            self.tarayici_sinirla()

        self.root.after(
            100,
            self.tarayici_browser_boyutlandir
        )

    def tarayici_buyut_uygula(self):

        if self.tarayici_frame is None:
            return

        self.sag_frame.update_idletasks()

        alan_w = (
            self.sag_frame.winfo_width()
        )

        alan_h = (
            self.sag_frame.winfo_height()
        )

        self.tarayici_x = 5
        self.tarayici_y = 5

        self.tarayici_genislik = max(
            self.tarayici_min_genislik,
            alan_w - 10
        )

        self.tarayici_yukseklik = max(
            self.tarayici_min_yukseklik,
            alan_h - 10
        )

        self.tarayici_frame.place_configure(
            x=5,
            y=5,
            width=int(
                self.tarayici_genislik
            ),
            height=int(
                self.tarayici_yukseklik
            )
        )

        self.root.update_idletasks()

        self.root.after_idle(
            self.tarayici_browser_boyutlandir
        )

        self.root.after(
            50,
            self.tarayici_browser_boyutlandir
        )

        self.root.after(
            150,
            self.tarayici_browser_boyutlandir
        )

    def tarayici_cef_baslat(self):

        if not self.tarayici_acik:
            return

        if self.tarayici_browser is not None:

            self.tarayici_browser_boyutlandir()

            return

        try:

            self.root.update_idletasks()
            self.tarayici_alan.update_idletasks()

            hwnd = (
                self.tarayici_alan.winfo_id()
            )

            alan_w = max(
                1,
                self.tarayici_alan.winfo_width()
            )

            alan_h = max(
                1,
                self.tarayici_alan.winfo_height()
            )

            window_info = cef.WindowInfo()

            window_info.SetAsChild(
                hwnd,
                [
                    0,
                    0,
                    alan_w,
                    alan_h
                ]
            )

            url = self.tarayici_sekmeleri[
                self.tarayici_aktif_sekme
            ].get(
                "url",
                "https://www.google.com/"
            )

            self.tarayici_browser = (
                cef.CreateBrowserSync(
                    window_info,
                    url=url
                )
            )

            try:
                self.tarayici_browser.SetClientHandler(
                    TarayiciDisplayHandler(
                        self
                    )
                )
            except Exception:
                pass

            self.tarayici_adres.delete(
                0,
                tk.END
            )

            self.tarayici_adres.insert(
                0,
                url
            )

            self.tarayici_browser.SetFocus(
                True
            )

            self.tarayici_browser_boyutlandir()

            self.root.after(
                50,
                self.tarayici_browser_boyutlandir
            )

            self.root.after(
                150,
                self.tarayici_browser_boyutlandir
            )

            self.root.after(
                500,
                self.tarayici_browser_boyutlandir
            )

            self.tarayici_durumunu_kaydet()

            if not self.cef_dongu_basladi:

                self.cef_dongu_basladi = True

                self.root.after(
                    10,
                    self.tarayici_cef_dongu
                )

        except Exception as e:

            self.tarayici_acik = False

            try:
                if self.tarayici_frame is not None:
                    self.tarayici_frame.place_forget()
            except Exception:
                pass

            messagebox.showerror(
                "Tarayıcı Hatası",
                str(e)
            )

    def tarayici_cef_dongu(self):

        if self.uygulama_kapaniyor:
            self.cef_dongu_basladi = False
            return

        try:
            cef.MessageLoopWork()

        except Exception:
            self.cef_dongu_basladi = False
            return

        try:
            if self.root.winfo_exists():
                self.root.after(
                    10,
                    self.tarayici_cef_dongu
                )
        except Exception:
            self.cef_dongu_basladi = False

    def tarayici_adres_ac(self):

        if self.tarayici_browser is None:
            return

        adres = (
            self.tarayici_adres
            .get()
            .strip()
        )

        if not adres:
            return

        if not adres.startswith(
            (
                "http://",
                "https://"
            )
        ):

            if "." in adres:

                adres = (
                    "https://"
                    + adres
                )

            else:

                adres = (
                    "https://www.google.com/search?q="
                    + urllib.parse.quote_plus(
                        adres
                    )
                )

        self.tarayici_sekmeleri[
            self.tarayici_aktif_sekme
        ]["url"] = adres

        self.tarayici_sekmeleri[
            self.tarayici_aktif_sekme
        ]["isim"] = (
            self.tarayici_basliktan_isim(
                adres
            )
        )

        self.tarayici_son_url = adres

        try:

            self.tarayici_browser.LoadUrl(
                adres
            )

        except Exception:
            pass

        self.tarayici_durumunu_kaydet()
        self.tarayici_sekmelerini_guncelle()

    def tarayici_basliktan_isim(
        self,
        url
    ):

        try:

            parsed = urllib.parse.urlparse(
                url
            )

            host = parsed.netloc

            if host.startswith(
                "www."
            ):
                host = host[4:]

            if host:
                return host[:18]

        except Exception:
            pass

        return "Sekme"

    def tarayici_geri(self):

        if self.tarayici_browser is None:
            return

        try:

            if self.tarayici_browser.CanGoBack():
                self.tarayici_browser.GoBack()

        except Exception:
            pass

    def tarayici_ileri(self):

        if self.tarayici_browser is None:
            return

        try:

            if self.tarayici_browser.CanGoForward():
                self.tarayici_browser.GoForward()

        except Exception:
            pass

    def tarayici_yenile(self):

        if self.tarayici_browser is None:
            return

        try:
            self.tarayici_browser.Reload()

        except Exception:
            pass

    def tarayici_resize_baslat(
        self,
        event
    ):

        if self.tarayici_buyuk:
            return

        self.tarayici_resize_x = (
            event.x_root
        )

        self.tarayici_resize_y = (
            event.y_root
        )

        self.tarayici_resize_w = (
            self.tarayici_frame.winfo_width()
        )

        self.tarayici_resize_h = (
            self.tarayici_frame.winfo_height()
        )

    def tarayici_resize_hareket(
        self,
        event
    ):

        if self.tarayici_buyuk:
            return

        fark_x = (
            event.x_root
            - self.tarayici_resize_x
        )

        fark_y = (
            event.y_root
            - self.tarayici_resize_y
        )

        yeni_genislik = (
            self.tarayici_resize_w
            + fark_x
        )

        yeni_yukseklik = (
            self.tarayici_resize_h
            + fark_y
        )

        self.sag_frame.update_idletasks()

        alan_w = (
            self.sag_frame.winfo_width()
        )

        alan_h = (
            self.sag_frame.winfo_height()
        )

        gercek_max_w = max(
            self.tarayici_min_genislik,
            alan_w - self.tarayici_x - 5
        )

        gercek_max_h = max(
            self.tarayici_min_yukseklik,
            alan_h - self.tarayici_y - 5
        )

        yeni_genislik = max(
            self.tarayici_min_genislik,
            min(
                gercek_max_w,
                yeni_genislik
            )
        )

        yeni_yukseklik = max(
            self.tarayici_min_yukseklik,
            min(
                gercek_max_h,
                yeni_yukseklik
            )
        )

        self.tarayici_genislik = (
            yeni_genislik
        )

        self.tarayici_yukseklik = (
            yeni_yukseklik
        )

        self.tarayici_frame.place_configure(
            width=int(
                yeni_genislik
            ),
            height=int(
                yeni_yukseklik
            )
        )

        self.root.update_idletasks()

        self.tarayici_browser_boyutlandir()

    def tarayici_resize_bitir(
        self,
        event
    ):

        self.root.after_idle(
            self.tarayici_browser_boyutlandir
        )

    def tarayici_browser_boyutlandir(
        self
    ):

        if self.tarayici_browser is None:
            return

        if self.tarayici_alan is None:
            return

        try:

            self.tarayici_alan.update_idletasks()

            genislik = max(
                1,
                self.tarayici_alan.winfo_width()
            )

            yukseklik = max(
                1,
                self.tarayici_alan.winfo_height()
            )

            if (
                genislik <= 1
                or yukseklik <= 1
            ):
                return

            try:

                hwnd = (
                    self.tarayici_browser
                    .GetWindowHandle()
                )

            except Exception:

                hwnd = (
                    self.tarayici_browser
                    .GetHost()
                    .GetWindowHandle()
                )

            if not hwnd:
                return

            parent_hwnd = (
                self.tarayici_alan.winfo_id()
            )

            user32 = ctypes.windll.user32

            try:
                user32.SetParent(
                    hwnd,
                    parent_hwnd
                )
            except Exception:
                pass

            SWP_NOZORDER = 0x0004
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040

            user32.SetWindowPos(
                hwnd,
                0,
                0,
                0,
                int(genislik),
                int(yukseklik),
                SWP_NOZORDER
                | SWP_NOACTIVATE
                | SWP_SHOWWINDOW
            )

            user32.MoveWindow(
                hwnd,
                0,
                0,
                int(genislik),
                int(yukseklik),
                True
            )

            try:

                self.tarayici_browser.GetHost().WasResized()

            except Exception:
                pass

            try:

                self.tarayici_browser.GetHost().Invalidate(
                    0
                )

            except Exception:
                pass

        except Exception:
            pass

    def tarayici_kapat(
        self,
        uygulamayi_kapat=False
    ):

        try:
            self.tarayici_mevcut_url_kaydet()
        except Exception:
            pass

        try:
            self.tarayici_durumunu_kaydet()
        except Exception:
            pass

        if uygulamayi_kapat:

            try:

                if self.tarayici_browser is not None:

                    try:
                        self.tarayici_browser.StopLoad()
                    except Exception:
                        pass

                    try:
                        self.tarayici_browser.CloseBrowser(
                            True
                        )
                    except Exception:
                        pass

            except Exception:
                pass

            self.tarayici_browser = None

            try:

                if self.tarayici_frame is not None:
                    self.tarayici_frame.destroy()

            except Exception:
                pass

            self.tarayici_frame = None
            self.tarayici_alan = None
            self.tarayici_adres = None
            self.tarayici_resize = None
            self.tarayici_tab_bar = None
            self.tarayici_ust = None
            self.tarayici_acik = False

            return

        self.tarayici_kapaliyken_sekmeler = [
            dict(x)
            for x in self.tarayici_sekmeleri
        ]

        self.tarayici_acik = False

        if self.tarayici_frame is not None:

            try:
                self.tarayici_frame.place_forget()
            except Exception:
                pass

        if self.tarayici_sekmeleri:

            self.tarayici_son_url = (
                self.tarayici_sekmeleri[
                    self.tarayici_aktif_sekme
                ].get(
                    "url",
                    self.tarayici_son_url
                )
            )

        self.tarayici_durumunu_kaydet()

    def codemod_yaz(
        self,
        gonderen,
        metin
    ):

        self.yazma_id += 1

        aktif_id = self.yazma_id

        tam_mesaj = (
            f"{gonderen}: "
        )

        self.sohbet_alani.config(
            state=tk.NORMAL
        )

        if gonderen == "Sistem":
            tag = "sistem"

        elif gonderen == "Sen":
            tag = "kullanici"

        else:
            tag = "bot"

        self.sohbet_alani.insert(
            tk.END,
            tam_mesaj,
            tag
        )

        self.sohbet_alani.config(
            state=tk.DISABLED
        )

        index = [0]

        self.klavye_sesini_baslat()

        def yaz():

            if aktif_id != self.yazma_id:

                self.klavye_sesini_durdur()

                return

            if index[0] >= len(
                metin
            ):

                self.klavye_sesini_durdur()

                if (
                    self.aktif_oturum
                    in gecmis
                ):

                    gecmis[
                        self.aktif_oturum
                    ].append(
                        f"{gonderen}: {metin}"
                    )

                    json_kaydet(
                        GECMIS_DOSYASI,
                        gecmis
                    )

                    self.sekmeleri_guncelle()

                return

            karakter = metin[
                index[0]
            ]

            self.sohbet_alani.config(
                state=tk.NORMAL
            )

            self.sohbet_alani.insert(
                tk.END,
                karakter,
                tag
            )

            self.sohbet_alani.see(
                tk.END
            )

            self.sohbet_alani.config(
                state=tk.DISABLED
            )

            index[0] += 1

            self.root.after(
                3,
                yaz
            )

        yaz()

    def yeni_sohbet(self):

        self.aktif_oturum = datetime.now().strftime(
            "Sohbet - %H:%M %d.%m"
        )

        while self.aktif_oturum in gecmis:

            self.aktif_oturum = datetime.now().strftime(
                "Sohbet - %H:%M:%S %d.%m"
            )

        gecmis[
            self.aktif_oturum
        ] = []

        self.sohbet_kod_modlari[
            self.aktif_oturum
        ] = self.codemod_aktif

        json_kaydet(
            GECMIS_DOSYASI,
            gecmis
        )

        self.sohbet_alani.config(
            state=tk.NORMAL
        )

        self.sohbet_alani.delete(
            1.0,
            tk.END
        )

        self.sohbet_alani.config(
            state=tk.DISABLED
        )

        self.gecmis_listesini_guncelle()
        self.sekmeleri_guncelle()

        self.mesaja_yaz(
            "Yapay Zeka",
            "Yeni sohbet başlatıldı."
        )

    def sohbet_sil(self):

        secim = (
            self.gecmis_liste
            .curselection()
        )

        if not secim:

            messagebox.showinfo(
                "Sohbet Sil",
                "Önce silmek istediğin sohbeti seç."
            )

            return

        secilen_metin = (
            self.gecmis_liste
            .get(
                secim[0]
            )
            .replace(
                "🕒 ",
                ""
            )
        )

        oturum_adi = secilen_metin.split(
            " 💻[CodeMod]"
        )[0]

        onay = messagebox.askyesno(
            "Sohbet Sil",
            f"'{oturum_adi}' sohbeti silinsin?"
        )

        if not onay:
            return

        if oturum_adi in gecmis:

            del gecmis[
                oturum_adi
            ]

        if oturum_adi in self.sohbet_kod_modlari:

            del self.sohbet_kod_modlari[
                oturum_adi
            ]

        if self.aktif_oturum == oturum_adi:

            if gecmis:

                self.aktif_oturum = list(
                    gecmis.keys()
                )[-1]

                self.sohbet_kod_modlari.setdefault(
                    self.aktif_oturum,
                    False
                )

            else:

                self.aktif_oturum = datetime.now().strftime(
                    "Sohbet - %H:%M %d.%m"
                )

                gecmis[
                    self.aktif_oturum
                ] = []

                self.sohbet_kod_modlari[
                    self.aktif_oturum
                ] = self.codemod_aktif

        json_kaydet(
            GECMIS_DOSYASI,
            gecmis
        )

        self.sekme_ac(
            self.aktif_oturum
        )

        self.gecmis_listesini_guncelle()
        self.sekmeleri_guncelle()

    def sohbet_ismini_degistir(
        self,
        event=None
    ):

        secim = (
            self.gecmis_liste
            .curselection()
        )

        if not secim:
            return

        secilen_metin = (
            self.gecmis_liste
            .get(
                secim[0]
            )
            .replace(
                "🕒 ",
                ""
            )
        )

        eski_isim = secilen_metin.split(
            " 💻[CodeMod]"
        )[0]

        yeni_isim = simpledialog.askstring(
            "Sohbet İsmi",
            "Yeni sohbet ismini yaz:",
            initialvalue=eski_isim,
            parent=self.root
        )

        if yeni_isim is None:
            return

        yeni_isim = yeni_isim.strip()

        if not yeni_isim:
            return

        if yeni_isim in gecmis:

            messagebox.showerror(
                "Hata",
                "Bu isimde bir sohbet zaten var."
            )

            return

        gecmis[
            yeni_isim
        ] = gecmis.pop(
            eski_isim
        )

        self.sohbet_kod_modlari[
            yeni_isim
        ] = self.sohbet_kod_modlari.pop(
            eski_isim,
            False
        )

        if self.aktif_oturum == eski_isim:
            self.aktif_oturum = yeni_isim

        json_kaydet(
            GECMIS_DOSYASI,
            gecmis
        )

        self.gecmis_listesini_guncelle()
        self.sekmeleri_guncelle()

    def gecmis_listesini_guncelle(self):

        self.gecmis_liste.delete(
            0,
            tk.END
        )

        for oturum_adi in reversed(
            list(
                gecmis.keys()
            )
        ):

            etiket = oturum_adi

            if self.sohbet_kod_modlari.get(
                oturum_adi,
                False
            ):

                etiket += (
                    " 💻[CodeMod]"
                )

            self.gecmis_liste.insert(
                tk.END,
                "🕒 "
                + etiket
            )

    def eski_sohbeti_yukle(
        self,
        event=None
    ):

        secim = (
            self.gecmis_liste
            .curselection()
        )

        if not secim:
            return

        secilen_metin = (
            self.gecmis_liste
            .get(
                secim[0]
            )
            .replace(
                "🕒 ",
                ""
            )
        )

        oturum_adi = secilen_metin.split(
            " 💻[CodeMod]"
        )[0]

        self.sekme_ac(
            oturum_adi
        )

    def mesaja_yaz(
        self,
        gonderen,
        metin
    ):

        if self.codemod_aktif:

            self.codemod_yaz(
                gonderen,
                metin
            )

            return

        tam_mesaj = (
            f"{gonderen}: {metin}"
        )

        self.sohbet_alani.config(
            state=tk.NORMAL
        )

        if gonderen == "Sen":
            tag = "kullanici"

        elif gonderen == "Sistem":
            tag = "sistem"

        else:
            tag = "bot"

        self.sohbet_alani.insert(
            tk.END,
            tam_mesaj + "\n\n",
            tag
        )

        self.sohbet_alani.see(
            tk.END
        )

        self.sohbet_alani.config(
            state=tk.DISABLED
        )

        if self.aktif_oturum in gecmis:

            gecmis[
                self.aktif_oturum
            ].append(
                tam_mesaj
            )

            json_kaydet(
                GECMIS_DOSYASI,
                gecmis
            )

        self.sekmeleri_guncelle()

    def tema_uygula(self):

        if self.codemod_aktif:

            koyu = self.code_bg_koyu
            acik = self.code_bg_acik
            ana = self.code_kirmizi
            ana_acik = self.code_kirmizi_acik

        else:

            koyu = self.normal_bg_koyu
            acik = self.normal_bg_acik
            ana = self.normal_turkuaz
            ana_acik = self.normal_turkuaz_acik

        self.bg_koyu = koyu
        self.bg_acik = acik
        self.turkuaz = ana
        self.turkuaz_acik = ana_acik

        self.root.config(
            bg="#050505"
        )

        self.titlebar.config(
            bg="#0D0D0D"
        )

        self.title_label.config(
            bg="#0D0D0D"
        )

        self.min_btn.config(
            bg="#111111"
        )

        self.max_btn.config(
            bg="#111111"
        )

        self.close_btn.config(
            bg="#111111"
        )

        self.ana_frame.config(
            bg=koyu
        )

        self.sol_frame.config(
            bg=acik
        )

        self.sag_frame.config(
            bg=koyu
        )

        self.ust_bar.config(
            bg=acik
        )

        self.ust_komutlar.config(
            bg=acik
        )

        self.sekme_bar.config(
            bg="#050505"
        )

        self.sekme_icerik.config(
            bg="#050505"
        )

        self.alt_frame.config(
            bg=koyu
        )

        self.ust_cizgi.config(
            bg=ana
        )

        self.gecmis_baslik.config(
            bg=acik
        )

        self.baslik.config(
            bg=acik
        )

        self.giris_kutusu.config(
            highlightcolor=ana
        )

        self.sohbet_alani.config(
            bg=koyu
        )

        self.sekme_yeni_btn.config(
            bg=ana,
            activebackground=ana_acik
        )

        butonlar = [
            self.gecmis_toggle_btn,
            self.yeni_sohbet_btn,
            self.sil_sohbet_btn,
            self.kaydet_btn,
            self.tam_ekran_btn,
            self.web_site_btn,
            self.tarayici_btn,
            self.ses_btn
        ]

        for konteyner in butonlar:

            if konteyner.winfo_children():

                konteyner.winfo_children()[0].config(
                    bg=ana,
                    activebackground=ana_acik,
                    fg=(
                        "#FFFFFF"
                        if self.codemod_aktif
                        else "#000000"
                    )
                )

        if self.tarayici_frame is not None:

            try:

                self.tarayici_frame.config(
                    highlightbackground=ana
                )

                self.tarayici_resize.config(
                    fg=ana_acik
                )

            except Exception:
                pass

        self.sekmeleri_guncelle()

    def codemod_ac(self):

        if self.codemod_aktif:
            return

        self.codemod_aktif = True

        self.sohbet_kod_modlari[
            self.aktif_oturum
        ] = True

        self.baslik.config(
            text="✨ ASİSTAN | CodeMod: AKTİF 💻"
        )

        self.tema_uygula()
        self.gecmis_listesini_guncelle()

    def codemod_kapat(self):

        if not self.codemod_aktif:
            return

        self.codemod_aktif = False

        self.ses_durdur()

        self.sohbet_kod_modlari[
            self.aktif_oturum
        ] = False

        self.baslik.config(
            text="✨ ASİSTAN | CodeMod: KAPALI"
        )

        self.tema_uygula()
        self.gecmis_listesini_guncelle()

    def mesaj_gonder(self):

        ham_metin = (
            self.giris_kutusu
            .get()
            .strip()
        )

        self.giris_kutusu.delete(
            0,
            tk.END
        )

        if not ham_metin:
            return

        if ham_metin.lower() == "codemod":

            self.mesaja_yaz(
                "Sen",
                ham_metin
            )

            self.codemod_ac()

            self.mesaja_yaz(
                "Sistem",
                "GitHub CodeMod aktifleştirildi."
            )

            return

        if ham_metin.lower() in [
            "codemod0",
            "codemod 0"
        ]:

            self.mesaja_yaz(
                "Sen",
                ham_metin
            )

            self.codemod_kapat()

            self.mesaja_yaz(
                "Sistem",
                "CodeMod kapatıldı. Normal moda dönüldü."
            )

            return

        if ham_metin == "Hamdi123":

            self.admin_modu = (
                not self.admin_modu
            )

            durum = (
                "AKTİF"
                if self.admin_modu
                else "KAPALI"
            )

            self.mesaja_yaz(
                "Sen",
                ham_metin
            )

            self.mesaja_yaz(
                "Sistem",
                f"Admin modu {durum}."
            )

            return

        if self.aktif_oturum.startswith(
            "Sohbet -"
        ):

            yeni_isim = (
                ham_metin[:25]
                + (
                    "..."
                    if len(
                        ham_metin
                    ) > 25
                    else ""
                )
            )

            orijinal_isim = yeni_isim

            sayac = 2

            while yeni_isim in gecmis:

                yeni_isim = (
                    f"{orijinal_isim} "
                    f"({sayac})"
                )

                sayac += 1

            gecmis[
                yeni_isim
            ] = gecmis.pop(
                self.aktif_oturum
            )

            self.sohbet_kod_modlari[
                yeni_isim
            ] = self.sohbet_kod_modlari.pop(
                self.aktif_oturum,
                self.codemod_aktif
            )

            self.aktif_oturum = yeni_isim

            json_kaydet(
                GECMIS_DOSYASI,
                gecmis
            )

            self.gecmis_listesini_guncelle()
            self.sekmeleri_guncelle()

        self.mesaja_yaz(
            "Sen",
            ham_metin
        )

        hafiza_yaniti = hafizadan_bul(
            ham_metin,
            hafiza
        )

        if hafiza_yaniti:

            self.mesaja_yaz(
                "Yapay Zeka",
                hafiza_yaniti
            )

            return

        kod_modu_aktif = (
            self.sohbet_kod_modlari.get(
                self.aktif_oturum,
                self.codemod_aktif
            )
        )

        if kod_modu_aktif:

            arama_bildirimi = (
                "GitHub kaynakları taranıyor... 🔍💻"
            )

        else:

            arama_bildirimi = (
                "Canlı web taranıyor... 🔍"
            )

        self.mesaja_yaz(
            "Yapay Zeka",
            arama_bildirimi
        )

        self.root.update()

        sonuc = canli_arastir(
            ham_metin,
            kod_modu_aktif
        )

        self.mesaja_yaz(
            "Yapay Zeka",
            sonuc
        )


def cef_baslat():

    global CEF_BASLADI

    if not CEF_VAR:
        return

    if CEF_BASLADI:
        return

    sys.excepthook = (
        cef.ExceptHook
    )

    os.makedirs(
        tarayici_veri_klasoru,
        exist_ok=True
    )

    settings = {
        "multi_threaded_message_loop": False,
        "external_message_pump": False,
        "cache_path":
            tarayici_veri_klasoru,
        "persist_session_cookies":
            True
    }

    cef.Initialize(
        settings=settings
    )

    CEF_BASLADI = True


def cef_kapat():

    global CEF_BASLADI

    if not CEF_VAR:
        return

    if not CEF_BASLADI:
        return

    try:
        cef.Shutdown()
    except Exception:
        pass

    CEF_BASLADI = False


if __name__ == "__main__":

    if not CEF_VAR:

        root = tk.Tk()

        root.withdraw()

        messagebox.showerror(
            "Eksik Paket",
            "cefpython3 kurulu değil."
        )

        root.destroy()

        raise SystemExit

    cef_baslat()

    root = tk.Tk()

    app = YapayZekaUygulamasi(
        root
    )

    root.bind(
        "<F11>",
        lambda event:
        app.tam_ekran_degistir()
    )

    root.bind(
        "<Control-s>",
        lambda event:
        app.aktif_sohbeti_kaydet()
    )

    root.bind(
        "<Control-n>",
        lambda event:
        app.yeni_sekme()
    )

    root.bind(
        "<Configure>",
        lambda event:
        (
            app.tarayici_sinirla(),
            app.tarayici_browser_boyutlandir()
        )
        if app.tarayici_acik
        else None
    )

    root.protocol(
        "WM_DELETE_WINDOW",
        app.uygulama_kapat
    )

    root.mainloop()
