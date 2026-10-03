```python
# -*- coding: utf-8 -*-
"""
Geliştirilmiş Basit Yapay Zeka
Yazım hatalarını ve eksik harfleri anlayabilir.
"""

from datetime import datetime
from difflib import SequenceMatcher
import random
import re


# =========================================================
# BENZERLİK SİSTEMİ
# =========================================================

def benzerlik(metin1, metin2):
    """
    İki metnin benzerlik oranını döndürür.
    0.0 = hiç benzemiyor
    1.0 = tamamen aynı
    """
    return SequenceMatcher(None, metin1, metin2).ratio()


def benzer_mi(metin, kelime, esik=0.70):
    """
    Kullanıcının yazdığı metin ile hedef kelime
    yeterince benzer mi kontrol eder.
    """
    return benzerlik(metin, kelime) >= esik


def temizle(metin):
    """
    Metni temizler:
    - Küçük harfe çevirir
    - Gereksiz boşlukları kaldırır
    - Noktalama işaretlerini temizler
    """
    metin = metin.lower().strip()

    # Türkçe karakterleri koruyarak noktalama işaretlerini kaldır
    metin = re.sub(r"[^\w\sçğıöşüÇĞİÖŞÜ]", "", metin)

    # Birden fazla boşluğu teke indir
    metin = re.sub(r"\s+", " ", metin)

    return metin


def kelime_benzer_mi(metin, hedefler, esik=0.70):
    """
    Metindeki kelimelerden herhangi biri hedef kelimelerden
    birine yeterince benziyor mu kontrol eder.

    Örneğin:
    'merhab' -> 'merhaba'
    'selaam' -> 'selam'
    'tesekkur' -> 'teşekkür'
    """

    kelimeler = metin.split()

    for kelime in kelimeler:

        for hedef in hedefler:

            if benzer_mi(kelime, hedef, esik):
                return True

    return False


def ifade_benzer_mi(metin, hedefler, esik=0.65):
    """
    Birden fazla kelimeden oluşan ifadeleri kontrol eder.

    Örneğin:
    'adın nee' -> 'adın ne'
    'saat kac' -> 'saat kaç'
    """

    for hedef in hedefler:

        # Tam metin karşılaştırması
        if benzer_mi(metin, hedef, esik):
            return True

        # Hedef ifadenin parçalarını kontrol et
        hedef_kelimeler = hedef.split()

        if len(hedef_kelimeler) == len(metin.split()):

            toplam = 0

            for kullanici_kelime, hedef_kelime in zip(
                metin.split(),
                hedef_kelimeler
            ):
                toplam += benzerlik(kullanici_kelime, hedef_kelime)

            ortalama = toplam / len(hedef_kelimeler)

            if ortalama >= esik:
                return True

    return False


# =========================================================
# BAŞLANGIÇ
# =========================================================

print("===================================")
print("       BASİT YAPAY ZEKA 🤖")
print("===================================")
print("Merhaba! Ben senin geliştirilmiş yapay zekanım.")
print("Benimle sohbet edebilirsin.")
print("Yazım hatalarını da mümkün olduğunca anlayabilirim.")
print("Çıkmak için 'çıkış' yaz.\n")


# =========================================================
# ANA DÖNGÜ
# =========================================================

while True:

    a = input("Sen: ")

    # Metni temizle
    a = temizle(a)


    # Boş mesaj
    if not a:
        print("Yapay Zeka: Bir şeyler yazabilirsin. 🤖")
        continue


    # =====================================================
    # ÇIKIŞ
    # =====================================================

    if (
        ifade_benzer_mi(
            a,
            ["çıkış", "exit", "kapat"],
            0.70
        )
    ):

        print("Yapay Zeka: Görüşürüz! 👋")
        break


    # =====================================================
    # MERHABA / SELAM
    # =====================================================

    elif (
        kelime_benzer_mi(
            a,
            [
                "merhaba",
                "selam",
                "selamlar",
                "hey",
                "naber"
            ],
            0.70
        )
        or
        "ne haber" in a
    ):

        saat = datetime.now().hour

        if saat < 12:
            print("Yapay Zeka: Günaydın! ☀️")

        elif saat < 18:
            print("Yapay Zeka: İyi günler! 😊")

        else:
            print("Yapay Zeka: İyi akşamlar! 🌙")


    # =====================================================
    # NASILSIN
    # =====================================================

    elif (
        ifade_benzer_mi(
            a,
            [
                "nasılsın",
                "naber",
                "ne haber",
                "iyi misin",
                "ne yapıyorsun"
            ],
            0.65
        )
    ):

        cevaplar = [
            "İyiyim, teşekkür ederim! 😄",
            "Gayet iyiyim! Sen nasılsın?",
            "Harikayım! Senin nasıl gidiyor?",
            "Ben bir yapay zekayım ama gayet iyiyim. 🤖"
        ]

        print("Yapay Zeka:", random.choice(cevaplar))


    # =====================================================
    # SEN NASILSIN
    # =====================================================

    elif (
        ifade_benzer_mi(
            a,
            [
                "ben iyiyim",
                "iyiyim",
                "gayet iyiyim",
                "çok iyiyim"
            ],
            0.70
        )
    ):

        print("Yapay Zeka: Buna sevindim! 😊")


    # =====================================================
    # TEŞEKKÜR
    # =====================================================

    elif (
        kelime_benzer_mi(
            a,
            [
                "teşekkür",
                "teşekkürler",
                "sağol"
            ],
            0.65
        )
        or
        "sağ ol" in a
    ):

        print("Yapay Zeka: Rica ederim! 😊")


    # =====================================================
    # İSMİNİ SORMA
    # =====================================================

    elif (
        ifade_benzer_mi(
            a,
            [
                "adın ne",
                "ismin ne",
                "sen kimsin"
            ],
            0.65
        )
    ):

        print(
            "Yapay Zeka: Ben senin Python ile yaptığın "
            "basit yapay zekayım. 🤖"
        )


    # =====================================================
    # YAŞ
    # =====================================================

    elif (
        ifade_benzer_mi(
            a,
            [
                "kaç yaşındasın",
                "kaç yaşındasın"
            ],
            0.70
        )
    ):

        print(
            "Yapay Zeka: Benim yaşım yok. "
            "Daha yeni oluşturuldum! 😄"
        )


    # =====================================================
    # SAAT
    # =====================================================

    elif (
        ifade_benzer_mi(
            a,
            [
                "saat kaç",
                "saat"
            ],
            0.70
        )
    ):

        saat = datetime.now().strftime("%H:%M")

        print("Yapay Zeka: Şu an saat", saat)


    # =====================================================
    # TARİH
    # =====================================================

    elif (
        ifade_benzer_mi(
            a,
            [
                "bugün hangi gün",
                "tarih ne",
                "bugünün tarihi"
            ],
            0.65
        )
    ):

        tarih = datetime.now().strftime("%d/%m/%Y")

        print("Yapay Zeka: Bugünün tarihi", tarih)


    # =====================================================
    # GÜNÜN NASIL
    # =====================================================

    elif (
        ifade_benzer_mi(
            a,
            [
                "günün nasıl",
                "bugün nasıl"
            ],
            0.70
        )
    ):

        print(
            "Yapay Zeka: Benim günüm güzel geçiyor! "
            "Seninki nasıl? 😄"
        )


    # =====================================================
    # MATEMATİK
    # =====================================================

    elif "matematik" in a:

        print(
            "Yapay Zeka: Matematik konusunda bana "
            "basit işlemler sorabilirsin."
        )

        print("Örneğin: 25 + 30")


    # =====================================================
    # MATEMATİK İŞLEMLERİ
    # =====================================================

    elif (
        "2+2" in a
        or
        "2 + 2" in a
    ):

        print("Yapay Zeka: 2 + 2 = 4 😎")


    elif (
        "5+5" in a
        or
        "5 + 5" in a
    ):

        print("Yapay Zeka: 5 + 5 = 10")


    elif (
        "10+10" in a
        or
        "10 + 10" in a
    ):

        print("Yapay Zeka: 10 + 10 = 20")


    elif (
        "10*10" in a
        or
        "10 * 10" in a
    ):

        print("Yapay Zeka: 10 × 10 = 100")


    elif (
        "100/10" in a
        or
        "100 / 10" in a
    ):

        print("Yapay Zeka: 100 ÷ 10 = 10")


    # =====================================================
    # ESPRİ
    # =====================================================

    elif (
        "espri" in a
        or
        "şaka" in a
    ):

        espriler = [
            "Bilgisayar neden doktora gitmiş? Virüsü varmış! 😂",
            "Python neden yılanmış? Çünkü adı Python! 🐍😂",
            "Programcı neden kahve içer? Çünkü Java'sı vardır! ☕"
        ]

        print(
            "Yapay Zeka:",
            random.choice(espriler)
        )


    # =====================================================
    # OYUN
    # =====================================================

    elif "oyun" in a:

        print(
            "Yapay Zeka: Benimle sayı tahmin oyunu "
            "oynayabilirsin! 🎮"
        )


    # =====================================================
    # FAVORİ
    # =====================================================

    elif (
        "seni seviyorum" in a
        or
        "seni sevom" in a
    ):

        print(
            "Yapay Zeka: Ben de seninle sohbet etmeyi "
            "seviyorum! ❤️"
        )


    # =====================================================
    # UYKU
    # =====================================================

    elif (
        "iyi geceler" in a
        or
        "yatıyorum" in a
        or
        "uyuyacağım" in a
    ):

        print(
            "Yapay Zeka: İyi geceler! "
            "Tatlı rüyalar. 🌙"
        )


    # =====================================================
    # GÖRÜŞME
    # =====================================================

    elif (
        "görüşürüz" in a
        or
        "hoşça kal" in a
        or
        "bay bay" in a
    ):

        print("Yapay Zeka: Görüşürüz! 👋")


    # =====================================================
    # HAVA DURUMU
    # =====================================================

    elif "hava nasıl" in a:

        print(
            "Yapay Zeka: Henüz internetten hava "
            "durumunu öğrenemiyorum. 🌤️"
        )


    # =====================================================
    # ANLAŞILAMAYAN MESAJ
    # =====================================================

    else:

        cevaplar = [
            "Bunu biraz daha açıklar mısın?",
            "Hmm, bunu henüz tam anlayamadım. 🤔",
            "İlginç! Biraz daha anlatır mısın?",
            "Bunu öğrenmem gerekiyor. 😄",
            "Şu anda buna verecek bir cevabım yok.",
            "Başka bir şeyden bahsedelim mi?",
            "Bunu not aldım! 🤖",
            "Hmmm... bunu düşünüyorum. 🤔"
        ]

        print(
            "Yapay Zeka:",
            random.choice(cevaplar)
        )
```
