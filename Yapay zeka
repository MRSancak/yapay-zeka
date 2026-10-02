# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 10:25:35 2026
"""
from datetime import datetime
import random

print("===================================")
print("       BASİT YAPAY ZEKA 🤖")
print("===================================")
print("Merhaba! Ben senin basit yapay zekanım.")
print("Benimle sohbet edebilirsin.")
print("Çıkmak için 'çıkış' yaz.\n")


while True:

    a: str
    a = input("Sen: ")

    a = a.lower().strip()

    # Çıkış
    if a == "çıkış" or a == "exit" or a == "kapat":

        print("Yapay Zeka: Görüşürüz! 👋")
        break


    # MERHABA / SELAM
    elif ("merhaba" in a or
          "selam" in a or
          "selamlar" in a or
          "hey" in a or
          "naber" in a or
          "ne haber" in a):

        saat = datetime.now().hour

        if saat < 12:
            print("Yapay Zeka: Günaydın! ☀️")
        elif saat < 18:
            print("Yapay Zeka: İyi günler! 😊")
        else:
            print("Yapay Zeka: İyi akşamlar! 🌙")


    # NASILSIN
    elif ("nasılsın" in a or
          "naber" in a or
          "ne yapıyorsun" in a or
          "iyi misin" in a):

        cevaplar = [
            "İyiyim, teşekkür ederim! 😄",
            "Gayet iyiyim! Sen nasılsın?",
            "Harikayım! Senin nasıl gidiyor?",
            "Ben bir yapay zekayım ama gayet iyiyim. 🤖"
        ]

        print("Yapay Zeka:", random.choice(cevaplar))


    # SEN NASILSIN
    elif "ben iyiyim" in a or "iyiyim" in a:

        print("Yapay Zeka: Buna sevindim! 😊")


    # TEŞEKKÜR
    elif ("teşekkür" in a or
          "sağ ol" in a or
          "sağol" in a):

        print("Yapay Zeka: Rica ederim! 😊")


    # İSMİNİ SORMA
    elif ("adın ne" in a or
          "ismin ne" in a or
          "kimsin" in a):

        print("Yapay Zeka: Ben senin Python ile yaptığın basit yapay zekayım. 🤖")


    # YAŞ
    elif "kaç yaşındasın" in a:

        print("Yapay Zeka: Benim yaşım yok. Daha yeni oluşturuldum! 😄")


    # SAAT
    elif "saat kaç" in a or "saat" == a:

        saat = datetime.now().strftime("%H:%M")

        print("Yapay Zeka: Şu an saat", saat)


    # TARİH
    elif ("bugün hangi gün" in a or
          "tarih ne" in a or
          "bugünün tarihi" in a):

        tarih = datetime.now().strftime("%d/%m/%Y")

        print("Yapay Zeka: Bugünün tarihi", tarih)


    # GÜNÜN NASIL
    elif ("günün nasıl" in a or
          "bugün nasıl" in a):

        print("Yapay Zeka: Benim günüm güzel geçiyor! Seninki nasıl? 😄")


    # MATEMATİK
    elif "matematik" in a:

        print("Yapay Zeka: Matematik konusunda bana basit işlemler sorabilirsin.")
        print("Örneğin: 25 + 30")

    elif "2+2" in a or "2 + 2" in a:

        print("Yapay Zeka: 2 + 2 = 4 😎")


    # KOLAY MATEMATİK SORULARI
    elif "5+5" in a or "5 + 5" in a:

        print("Yapay Zeka: 5 + 5 = 10")


    elif "10+10" in a or "10 + 10" in a:

        print("Yapay Zeka: 10 + 10 = 20")


    elif "10*10" in a or "10 * 10" in a:

        print("Yapay Zeka: 10 × 10 = 100")


    elif "100/10" in a or "100 / 10" in a:

        print("Yapay Zeka: 100 ÷ 10 = 10")


    # ESPRİ
    elif ("espri yap" in a or
          "şaka yap" in a or
          "espri" in a):

        espriler = [
            "Bilgisayar neden doktora gitmiş? Virüsü varmış! 😂",
            "Python neden yılanmış? Çünkü adı Python! 🐍😂",
            "Programcı neden kahve içer? Çünkü Java'sı vardır! ☕"
        ]

        print("Yapay Zeka:", random.choice(espriler))


    # OYUN
    elif "oyun" in a:

        print("Yapay Zeka: Benimle sayı tahmin oyunu oynayabilirsin! 🎮")


    # FAVORİ
    elif "seni seviyorum" in a:

        print("Yapay Zeka: Ben de seninle sohbet etmeyi seviyorum! ❤️")


    # UYKU
    elif ("iyi geceler" in a or
          "yatıyorum" in a or
          "uyuyacağım" in a):

        print("Yapay Zeka: İyi geceler! Tatlı rüyalar. 🌙")


    # GÖRÜŞME
    elif ("görüşürüz" in a or
          "hoşça kal" in a or
          "bay bay" in a):

        print("Yapay Zeka: Görüşürüz! 👋")


    # KİMLİK
    elif "sen kimsin" in a:

        print("Yapay Zeka: Ben Python ile yapılmış küçük bir sohbet botuyum. 🤖")


    # HAVA DURUMU
    elif "hava nasıl" in a:

        print("Yapay Zeka: Henüz internetten hava durumunu öğrenemiyorum. 🌤️")


    # RASTGELE CEVAPLAR
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

        print("Yapay Zeka:", random.choice(cevaplar))
