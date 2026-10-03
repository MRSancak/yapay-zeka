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

masaustu_yolu = os.path.join(os.path.expanduser("~"), "Desktop")
klasor_adi = os.path.join(masaustu_yolu, "Yapay Zeka")
ses_klasoru = os.path.join(klasor_adi, "Ses")

os.makedirs(klasor_adi, exist_ok=True)
os.makedirs(ses_klasoru, exist_ok=True)

HAFIZA_DOSYASI = os.path.join(klasor_adi, "hafiza.json")
GECMIS_DOSYASI = os.path.join(klasor_adi, "gecmis.json")
SES_AYAR_DOSYASI = os.path.join(klasor_adi, "ses_ayar.json")

KLAVYE_SESI = os.path.join(ses_klasoru, "klavye.wav")

WEB_SITESI_URL = "https://minihaxball.onrender.com/"


def json_yukle(dosya_adi):
    if os.path.exists(dosya_adi):
        try:
            with open(dosya_adi, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def json_kaydet(dosya_adi, veri):
    try:
        with open(dosya_adi, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def hafizadan_bul(sorgu, hafiza_sozlugu):
    sorgu_temiz = sorgu.lower().strip()

    selamlasmalar = {
        "naber": "İyidir, kodları yazmaya devam ediyorum! Sen nasılsın, neler yapıyorsun?",
        "nasılsın": "Çok iyiyim, sistem sorunsuz çalışıyor. Sen nasılsın?",
        "merhaba": "Merhaba! Sana nasıl yardımcı olabilirim?",
        "selam": "Aleykümselam! Hangi konuda yardıma ihtiyacın var?",
        "iyi günler": "Teşekkürler, sana da iyi günler!"
    }

    if sorgu_temiz in selamlasmalar:
        return selamlasmalar[sorgu_temiz]

    if sorgu_temiz in hafiza_sozlugu:
        return hafiza_sozlugu[sorgu_temiz]

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

    metin = re.sub(r"<[^>]+>", "", metin)
    metin = html.unescape(metin)
    metin = re.sub(r"\s+", " ", metin)

    return metin.strip()


def guvenli_istek(url, timeout=10):
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

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def github_sonuclarini_ayikla(html_icerik):
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

        link = html.unescape(baslik_eslesme.group(1))
        baslik = html_temizle(baslik_eslesme.group(2))

        try:
            parsed = urllib.parse.urlparse(link)
            params = urllib.parse.parse_qs(parsed.query)

            if "uddg" in params:
                link = urllib.parse.unquote(params["uddg"][0])
        except Exception:
            pass

        snippet_eslesme = re.search(
            r'class="result__snippet[^"]*"'
            r'[^>]*>(.*?)</(?:a|div)>',
            blok,
            flags=re.IGNORECASE | re.DOTALL
        )

        if snippet_eslesme:
            aciklama = html_temizle(snippet_eslesme.group(1))
        else:
            aciklama = ""

        if not baslik:
            continue

        mevcut_linkler = [x["link"] for x in sonuclar]

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
        arama_sorgusu = f"site:github.com {sorgu}"
        encoded_query = urllib.parse.quote_plus(arama_sorgusu)

        url = (
            "https://html.duckduckgo.com/html/?q="
            + encoded_query
        )

        html_icerik = guvenli_istek(url, timeout=12)
        sonuclar = github_sonuclarini_ayikla(html_icerik)

        github_sonuclari = []

        for sonuc in sonuclar:
            link = sonuc["link"].lower()

            if (
                "github.com" in link
                and "github.com/search" not in link
            ):
                github_sonuclari.append(sonuc)

        if github_sonuclari:
            cikti = []
            cikti.append(
                f"GitHub Kod ve Kaynak Sonuçları ({sorgu}):"
            )
            cikti.append("")

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

            cikti.append("GitHub taraması tamamlandı.")

            return "\n".join(cikti)

        return github_yedek_arama(sorgu)

    except Exception as e:
        return (
            "GitHub araması sırasında bağlantı sorunu oluştu.\n\n"
            f"Hata: {e}\n\n"
            "Yedek arama sistemi çalıştırılıyor...\n\n"
            + github_yedek_arama(sorgu)
        )


def github_yedek_arama(sorgu):
    try:
        arama_sorgusu = f"github {sorgu} source code repository"
        encoded_query = urllib.parse.quote_plus(arama_sorgusu)

        url = (
            "https://html.duckduckgo.com/html/?q="
            + encoded_query
        )

        html_icerik = guvenli_istek(url, timeout=10)
        sonuclar = github_sonuclarini_ayikla(html_icerik)

        if sonuclar:
            cikti = [
                "GitHub için genişletilmiş arama sonuçları:",
                ""
            ]

            sayac = 0

            for sonuc in sonuclar:
                if "github.com" not in sonuc["link"].lower():
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

        encoded_query = urllib.parse.quote_plus(arama_sorgusu)

        url = (
            "https://html.duckduckgo.com/html/?q="
            + encoded_query
        )

        html_icerik = guvenli_istek(url, timeout=10)

        bulunan_metinler = []

        snippetler = re.findall(
            r'class="result__snippet[^"]*"'
            r'[^>]*>(.*?)</(?:a|div)>',
            html_icerik,
            flags=re.IGNORECASE | re.DOTALL
        )

        for snip in snippetler[:8]:
            temiz = html_temizle(snip)

            if (
                len(temiz) > 20
                and temiz not in bulunan_metinler
            ):
                if not temiz.endswith(
                    (".", "!", "?", "`", "}")
                ):
                    temiz += "."

                bulunan_metinler.append(temiz)

        if bulunan_metinler:
            birlesmis_ozet = " ".join(
                bulunan_metinler[:5]
            )

            return (
                "Canlı Web Araştırma Özeti:\n\n"
                "• " + birlesmis_ozet
            )

        return duckduckgo_api_arama(sorgu)

    except Exception as e:
        return (
            "Arama sırasında bağlantı hatası oluştu: "
            f"{e}"
        )


def duckduckgo_api_arama(sorgu):
    try:
        encoded_query = urllib.parse.quote_plus(sorgu)

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
            headers={"User-Agent": "Mozilla/5.0"}
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

        ozet = api_veri.get("AbstractText", "")
        ilgili_konular = api_veri.get(
            "RelatedTopics",
            []
        )

        sonuc_metni = []

        if ozet:
            sonuc_metni.append(ozet)

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
                + " ".join(sonuc_metni[:3])
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


def canli_arastir(sorgu, kod_modu_aktif=False):
    if kod_modu_aktif:
        return github_arastir(sorgu)

    return normal_web_arastir(sorgu)


hafiza = json_yukle(HAFIZA_DOSYASI)
gecmis = json_yukle(GECMIS_DOSYASI)
ses_ayari = json_yukle(SES_AYAR_DOSYASI)


class YapayZekaUygulamasi:

    def __init__(self, root):
        self.root = root
        self.root.title("Canlı Araştırma Asistanı 🤖")
        self.root.geometry("950x680")
        self.root.minsize(750, 500)

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

        self.root.configure(bg=self.bg_koyu)

        self.admin_modu = False
        self.sohbet_kod_modlari = {}
        self.codemod_aktif = False
        self.yazma_id = 0
        self.gecmis_acik = True
        self.tam_ekran = False
        self.ses_menu = None
        self.klavye_sesi_aktif = False

        try:
            self.ses_seviyesi = int(
                ses_ayari.get("ses", 35)
            )
        except Exception:
            self.ses_seviyesi = 35

        self.ses_seviyesi = max(
            0,
            min(100, self.ses_seviyesi)
        )

        self.ses_seviyesini_uygula()

        self.aktif_oturum = datetime.now().strftime(
            "Sohbet - %H:%M %d.%m"
        )

        if self.aktif_oturum not in gecmis:
            gecmis[self.aktif_oturum] = []

        self.sohbet_kod_modlari[
            self.aktif_oturum
        ] = False

        self.sol_frame = tk.Frame(
            root,
            bg=self.bg_acik,
            width=240
        )
        self.sol_frame.pack(
            side=tk.LEFT,
            fill=tk.Y
        )
        self.sol_frame.pack_propagate(False)

        self.gecmis_baslik = tk.Label(
            self.sol_frame,
            text="💬 Sohbet Geçmişi",
            bg=self.bg_acik,
            fg="#FFFFFF",
            font=("Segoe UI", 11, "bold")
        )
        self.gecmis_baslik.pack(pady=15)

        self.gecmis_liste = tk.Listbox(
            self.sol_frame,
            bg="#050609",
            fg="#FFFFFF",
            font=("Segoe UI", 9),
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

        self.gecmis_listesini_guncelle()

        self.sag_frame = tk.Frame(
            root,
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
        self.ust_bar.pack(fill=tk.X)
        self.ust_bar.pack_propagate(False)

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
            font=("Segoe UI", 9, "bold")
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

        self.sohbet_alani = scrolledtext.ScrolledText(
            self.sag_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
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

        self.sohbet_alani.config(state=tk.DISABLED)

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
            font=("Segoe UI", 12),
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
            lambda event: self.mesaj_gonder()
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

        if not gecmis[self.aktif_oturum]:
            self.mesaja_yaz(
                "Yapay Zeka",
                "Sistem hazır! GitHub, web ve CodeMod sistemleri hazır."
            )

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
            self.buton_hover(b, True)
        )

        btn.bind(
            "<Leave>",
            lambda e, b=btn:
            self.buton_hover(b, False)
        )

        return dis

    def buton_hover(self, buton, aktif):
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
            oran = self.ses_seviyesi / 100.0
            deger = int(65535 * oran)
            stereo_deger = deger | (deger << 16)

            ctypes.windll.winmm.waveOutSetVolume(
                0xFFFFFFFF,
                stereo_deger
            )
        except Exception:
            pass

    def ses_ayarini_kaydet(self):
        json_kaydet(
            SES_AYAR_DOSYASI,
            {"ses": self.ses_seviyesi}
        )

    def ses_degistir(self, deger):
        try:
            self.ses_seviyesi = int(float(deger))
        except Exception:
            return

        self.ses_seviyesi = max(
            0,
            min(100, self.ses_seviyesi)
        )

        self.ses_seviyesini_uygula()
        self.ses_ayarini_kaydet()

        if hasattr(self, "ses_deger_label"):
            self.ses_deger_label.config(
                text=f"%{self.ses_seviyesi}"
            )

        if hasattr(self, "ses_icon_label"):
            if self.ses_seviyesi == 0:
                ikon = "🔇"
            elif self.ses_seviyesi < 35:
                ikon = "🔈"
            elif self.ses_seviyesi < 70:
                ikon = "🔉"
            else:
                ikon = "🔊"

            self.ses_icon_label.config(text=ikon)

    def ses_menusu_toggle(self):
        if (
            self.ses_menu
            and self.ses_menu.winfo_exists()
        ):
            self.ses_menu.destroy()
            self.ses_menu = None
            return

        self.ses_menu = tk.Toplevel(self.root)

        pencere = self.ses_menu
        pencere.overrideredirect(True)
        pencere.configure(bg="#000000")

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
            fg=(
                self.code_kirmizi_acik
                if self.codemod_aktif
                else "#FFFFFF"
            ),
            font=("Segoe UI", 10, "bold")
        )
        baslik.pack(
            padx=15,
            pady=(12, 5)
        )

        bilgi = tk.Frame(
            ana,
            bg="#090B0F"
        )
        bilgi.pack(
            fill=tk.X,
            padx=15
        )

        self.ses_icon_label = tk.Label(
            bilgi,
            text="🔊",
            bg="#090B0F",
            fg="#FFFFFF",
            font=("Segoe UI Emoji", 12)
        )
        self.ses_icon_label.pack(side=tk.LEFT)

        self.ses_deger_label = tk.Label(
            bilgi,
            text=f"%{self.ses_seviyesi}",
            bg="#090B0F",
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold")
        )
        self.ses_deger_label.pack(side=tk.RIGHT)

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

        self.ses_slider.set(self.ses_seviyesi)

        self.ses_slider.pack(
            padx=15,
            pady=(3, 10)
        )

        bilgi2 = tk.Label(
            ana,
            text="Klavye yazma sesi",
            bg="#090B0F",
            fg="#FFFFFF",
            font=("Segoe UI", 8)
        )
        bilgi2.pack(pady=(0, 10))

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
            lambda e: self.ses_menu_kapat()
        )

        pencere.focus_force()

    def ses_menu_kapat(self):
        if (
            self.ses_menu
            and self.ses_menu.winfo_exists()
        ):
            self.ses_menu.destroy()
            self.ses_menu = None

    def ses_cal(self, dosya, loop=False):
        if not os.path.exists(dosya):
            return

        if self.ses_seviyesi <= 0:
            return

        try:
            self.ses_seviyesini_uygula()

            flags = (
                winsound.SND_FILENAME
                | winsound.SND_ASYNC
            )

            if loop:
                flags |= winsound.SND_LOOP

            winsound.PlaySound(
                dosya,
                flags
            )

        except Exception:
            pass

    def klavye_sesini_baslat(self):
        if self.klavye_sesi_aktif:
            return

        if not self.codemod_aktif:
            return

        if not os.path.exists(KLAVYE_SESI):
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

    def ses_durdur(self):
        try:
            winsound.PlaySound(
                None,
                winsound.SND_PURGE
            )
        except Exception:
            pass

        self.klavye_sesi_aktif = False

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
                fill=tk.Y,
                before=self.sag_frame
            )

            self.gecmis_acik = True

            self.gecmis_toggle_btn.winfo_children()[0].config(
                text="☰ Geçmiş Kapat"
            )

    def tam_ekran_degistir(self):
        self.tam_ekran = not self.tam_ekran

        self.root.attributes(
            "-fullscreen",
            self.tam_ekran
        )

        self.tam_ekran_btn.winfo_children()[0].config(
            text=(
                "⛶ Pencere Modu"
                if self.tam_ekran
                else "⛶ Tam Ekran"
            )
        )

    def web_sitesini_ac(self):
        if WEB_SITESI_URL == "BURAYA_WEB_SITENI_YAZ":
            yeni_url = simpledialog.askstring(
                "Web Sitem",
                "Web sitenin adresini yaz:",
                parent=self.root
            )

            if not yeni_url:
                return

            yeni_url = yeni_url.strip()

            if not yeni_url.startswith(
                ("http://", "https://")
            ):
                yeni_url = "https://" + yeni_url

            webbrowser.open_new_tab(yeni_url)
            return

        webbrowser.open_new_tab(WEB_SITESI_URL)

    def codemod_yaz(self, gonderen, metin):
        self.yazma_id += 1
        aktif_id = self.yazma_id

        tam_mesaj = f"{gonderen}: "

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

            if index[0] >= len(metin):
                self.klavye_sesini_durdur()

                if self.aktif_oturum in gecmis:
                    gecmis[
                        self.aktif_oturum
                    ].append(
                        f"{gonderen}: {metin}"
                    )

                    json_kaydet(
                        GECMIS_DOSYASI,
                        gecmis
                    )

                return

            karakter = metin[index[0]]

            self.sohbet_alani.config(
                state=tk.NORMAL
            )

            self.sohbet_alani.insert(
                tk.END,
                karakter,
                tag
            )

            self.sohbet_alani.see(tk.END)

            self.sohbet_alani.config(
                state=tk.DISABLED
            )

            index[0] += 1

            hiz = 5

            if karakter in ".,!?;:":
                hiz = 10
            elif karakter == "\n":
                hiz = 10

            self.root.after(
                hiz,
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

        gecmis[self.aktif_oturum] = []

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

        self.mesaja_yaz(
            "Yapay Zeka",
            "Yeni sohbet başlatıldı."
        )

    def sohbet_sil(self):
        secim = self.gecmis_liste.curselection()

        if not secim:
            messagebox.showinfo(
                "Sohbet Sil",
                "Önce silmek istediğin sohbeti seç."
            )
            return

        secilen_metin = (
            self.gecmis_liste.get(
                secim[0]
            ).replace("🕒 ", "")
        )

        oturum_adi = secilen_metin.split(
            " 💻[CodeMod]"
        )[0]

        onay = messagebox.askyesno(
            "Sohbet Sil",
            f"'{oturum_adi}' sohbeti silinsin mi?"
        )

        if not onay:
            return

        if oturum_adi in gecmis:
            del gecmis[oturum_adi]

        if oturum_adi in self.sohbet_kod_modlari:
            del self.sohbet_kod_modlari[oturum_adi]

        if self.aktif_oturum == oturum_adi:
            self.aktif_oturum = datetime.now().strftime(
                "Sohbet - %H:%M %d.%m"
            )

            while self.aktif_oturum in gecmis:
                self.aktif_oturum = datetime.now().strftime(
                    "Sohbet - %H:%M:%S %d.%m"
                )

            gecmis[self.aktif_oturum] = []

            self.sohbet_kod_modlari[
                self.aktif_oturum
            ] = self.codemod_aktif

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

        json_kaydet(
            GECMIS_DOSYASI,
            gecmis
        )

        self.gecmis_listesini_guncelle()

        self.mesaja_yaz(
            "Sistem",
            "Sohbet silindi."
        )

    def sohbet_ismini_degistir(self, event=None):
        secim = self.gecmis_liste.curselection()

        if not secim:
            return

        secilen_metin = (
            self.gecmis_liste.get(
                secim[0]
            ).replace("🕒 ", "")
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

        if yeni_isim == eski_isim:
            return

        if yeni_isim in gecmis:
            messagebox.showerror(
                "Hata",
                "Bu isimde bir sohbet zaten var."
            )
            return

        gecmis[yeni_isim] = gecmis.pop(eski_isim)

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

    def gecmis_listesini_guncelle(self):
        self.gecmis_liste.delete(0, tk.END)

        for oturum_adi in reversed(
            list(gecmis.keys())
        ):
            etiket = oturum_adi

            if self.sohbet_kod_modlari.get(
                oturum_adi,
                False
            ):
                etiket += " 💻[CodeMod]"

            self.gecmis_liste.insert(
                tk.END,
                "🕒 " + etiket
            )

    def eski_sohbeti_yukle(self, event=None):
        secim = self.gecmis_liste.curselection()

        if not secim:
            return

        secilen_metin = (
            self.gecmis_liste.get(
                secim[0]
            ).replace("🕒 ", "")
        )

        oturum_adi = secilen_metin.split(
            " 💻[CodeMod]"
        )[0]

        self.aktif_oturum = oturum_adi

        sohbet_modu = self.sohbet_kod_modlari.get(
            oturum_adi,
            False
        )

        if sohbet_modu and not self.codemod_aktif:
            self.codemod_ac()
        elif not sohbet_modu and self.codemod_aktif:
            self.codemod_kapat()

        self.sohbet_alani.config(
            state=tk.NORMAL
        )

        self.sohbet_alani.delete(
            1.0,
            tk.END
        )

        if oturum_adi in gecmis:
            for mesaj in gecmis[oturum_adi]:
                if mesaj.startswith("Sistem:"):
                    tag = "sistem"
                elif mesaj.startswith("Sen:"):
                    tag = "kullanici"
                else:
                    tag = "bot"

                self.sohbet_alani.insert(
                    tk.END,
                    mesaj + "\n\n",
                    tag
                )

        self.sohbet_alani.see(tk.END)

        self.sohbet_alani.config(
            state=tk.DISABLED
        )

        durum_str = (
            "AKTİF 💻"
            if self.codemod_aktif
            else "KAPALI"
        )

        self.baslik.config(
            text=(
                f"✨ ASİSTAN | "
                f"CodeMod: {durum_str}"
            )
        )

    def mesaja_yaz(self, gonderen, metin):
        if self.codemod_aktif:
            self.codemod_yaz(
                gonderen,
                metin
            )
            return

        tam_mesaj = f"{gonderen}: {metin}"

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

        self.sohbet_alani.see(tk.END)

        self.sohbet_alani.config(
            state=tk.DISABLED
        )

        if self.aktif_oturum in gecmis:
            gecmis[
                self.aktif_oturum
            ].append(tam_mesaj)

            json_kaydet(
                GECMIS_DOSYASI,
                gecmis
            )

    def tema_uygula(self):
        if self.codemod_aktif:
            koyu = self.code_bg_koyu
            acik = self.code_bg_acik
            panel = self.code_panel
            ana = self.code_kirmizi
            ana_acik = self.code_kirmizi_acik
            yazi = "#FFFFFF"
        else:
            koyu = self.normal_bg_koyu
            acik = self.normal_bg_acik
            panel = self.normal_panel
            ana = self.normal_turkuaz
            ana_acik = self.normal_turkuaz_acik
            yazi = "#FFFFFF"

        self.bg_koyu = koyu
        self.bg_acik = acik
        self.panel = panel
        self.turkuaz = ana
        self.turkuaz_acik = ana_acik
        self.yazi_renk = yazi

        self.root.config(bg=koyu)
        self.sol_frame.config(bg=acik)
        self.sag_frame.config(bg=koyu)
        self.ust_bar.config(bg=acik)
        self.ust_komutlar.config(bg=acik)
        self.alt_frame.config(bg=koyu)

        self.ust_cizgi.config(bg=ana)

        for buton_konteyner in [
            self.gecmis_toggle_btn,
            self.yeni_sohbet_btn,
            self.sil_sohbet_btn,
            self.tam_ekran_btn,
            self.web_site_btn,
            self.ses_btn
        ]:
            buton_konteyner.config(bg="#000000")

            if buton_konteyner.winfo_children():
                b = buton_konteyner.winfo_children()[0]

                b.config(
                    bg=ana,
                    fg=(
                        "#FFFFFF"
                        if self.codemod_aktif
                        else "#000000"
                    ),
                    activebackground=ana_acik,
                    activeforeground="#FFFFFF"
                )

        self.gecmis_baslik.config(
            bg=acik,
            fg="#FFFFFF"
        )

        self.baslik.config(
            bg=acik,
            fg=(
                "#FF1833"
                if self.codemod_aktif
                else "#FFFFFF"
            )
        )

        self.gecmis_liste.config(
            bg="#050505" if self.codemod_aktif else "#050609",
            fg="#FFFFFF",
            selectbackground=ana,
            selectforeground="#FFFFFF"
        )

        self.giris_kutusu.config(
            bg="#080808" if self.codemod_aktif else "#090B0F",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            highlightcolor=ana
        )

        self.gonder_butonu.config(bg="#000000")

        if self.gonder_butonu.winfo_children():
            b = self.gonder_butonu.winfo_children()[0]

            b.config(
                bg=ana,
                fg=(
                    "#FFFFFF"
                    if self.codemod_aktif
                    else "#000000"
                ),
                activebackground=ana_acik,
                activeforeground="#FFFFFF"
            )

        self.sohbet_alani.config(
            bg=koyu,
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            highlightbackground="#111111"
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
            foreground="#FF1833"
            if self.codemod_aktif
            else "#FF3048"
        )

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
        ham_metin = self.giris_kutusu.get().strip()

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
            self.admin_modu = not self.admin_modu

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

        if self.aktif_oturum.startswith("Sohbet -"):
            yeni_isim = (
                ham_metin[:25]
                + (
                    "..."
                    if len(ham_metin) > 25
                    else ""
                )
            )

            orijinal_isim = yeni_isim
            sayac = 2

            while yeni_isim in gecmis:
                yeni_isim = (
                    f"{orijinal_isim} ({sayac})"
                )
                sayac += 1

            gecmis[yeni_isim] = gecmis.pop(
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

        kod_modu_aktif = self.sohbet_kod_modlari.get(
            self.aktif_oturum,
            self.codemod_aktif
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


if __name__ == "__main__":
    root = tk.Tk()
    app = YapayZekaUygulamasi(root)
    root.mainloop()