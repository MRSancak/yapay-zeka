# -*- coding: utf-8 -*-
"""
Geliştirilmiş Öğrenebilen Yapay Zeka (Dinamik Hafıza ve Oyun Modülü)
"""

from datetime import datetime
from difflib import SequenceMatcher
import json
import os
import random
import re

# =========================================================
# HAFIZA YÖNETİMİ (KENDİ KENDİNE ÖĞRENME)
# =========================================================

HAFIZA_DOSYASI = "hafiza.json"


def hafizayi_yukle():
  if os.path.exists(HAFIZA_DOSYASI):
    with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {"bilgiler": {}, "oyunlar": {}}
  return {"bilgiler": {}, "oyunlar": {}}


def hafizaya_kaydet(veri):
  with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
    json.dump(veri, f, ensure_ascii=False, indent=4)


# Hafızayı başlat
hafiza = hafizayi_yukle()


# =========================================================
# BENZERLİK SİSTEMİ
# =========================================================


def benzerlik(metin1, metin2):
  return SequenceMatcher(None, metin1, metin2).ratio()


def benzer_mi(metin, kelime, esik=0.70):
  return benzerlik(metin, kelime) >= esik


def temizle(metin):
  metin = metin.lower().strip()
  metin = re.sub(r"[^\w\sçğıöşüÇĞİÖŞÜ]", "", metin)
  metin = re.sub(r"\s+", " ", metin)
  return metin


def kelime_benzer_mi(metin, hedefler, esik=0.70):
  kelimeler = metin.split()
  for kelime in kelimeler:
    for hedef in hedefler:
      if benzer_mi(kelime, hedef, esik):
        return True
  return False


def ifade_benzer_mi(metin, hedefler, esik=0.65):
  for hedef in hedefler:
    if benzer_mi(metin, hedef, esik):
      return True
    hedef_kelimeler = hedef.split()
    if len(hedef_kelimeler) == len(metin.split()):
      toplam = sum(
          benzerlik(k, h) for k, h in zip(metin.split(), hedef_kelimeler)
      )
      if (toplam / len(hedef_kelimeler)) >= esik:
        return True
  return False


# =========================================================
# BAŞLANGIÇ
# =========================================================

print("===================================")
print("       GELİŞMİŞ ÖĞRENEN ZEKA 🤖")
print("===================================")
print("Merhaba! Ben senin öğrenebilen yapay zekanım.")
print("Bana bilmediğim şeyleri öğretmeni isteyebilirim.")
print("Çıkmak için 'çıkış' yaz.\n")


# =========================================================
# ANA DÖNGÜ
# =========================================================

aktif_oyun = None  # Devam eden bir oyun varsa burada tutulacak

while True:
  a = input("Sen: ")
  a = temizle(a)

  if not a:
    print("Yapay Zeka: Bir şeyler yazabilirsin. 🤖")
    continue

  # ÇIKIŞ
  if ifade_benzer_mi(a, ["çıkış", "exit", "kapat"], 0.70):
    print("Yapay Zeka: Görüşürüz! 👋")
    break

  # =====================================================
  # AKTİF OYUN KONTROLÜ (Sayı Tahmin Örneği)
  # =====================================================
  if aktif_oyun == "sayi_tahmimi":
    # Kullanıcının yazdığı metinden sayıları çekelim
    rakamlar = re.findall(r"\d+", a)
    if rakamlar:
      tahmin = int(rakamlar[0])
      if tahmin < hedef_sayi:
        print("Yapay Zeka: Daha **büyük** bir sayı söyle! 🔼")
      elif tahmin > hedef_sayi:
        print("Yapay Zeka: Daha **küçük** bir sayı söyle! 🔽")
      else:
        print("Yapay Zeka: Tebrikler! Doğru bildin! 🎉🏆")
        aktif_oyun = None
    else:
      print(
          "Yapay Zeka: Lütfen 1 ile 10 arasında bir sayı tahmin et (veya oyundan"
          " çıkmak için 'iptal' yaz)."
      )
      if "iptal" in a:
        aktif_oyun = None
        print("Yapay Zeka: Oyun iptal edildi.")
    continue

  # =====================================================
  # HAFIZADAKİ ÖZEL KOMUTLAR KONTROLÜ
  # =====================================================
  bulundu = False
  for anahtar, cevap in hafiza.get("bilgiler", {}).items():
    if benzer_mi(a, anahtar, 0.75) or anahtar in a:
      print(f"Yapay Zeka: {cevap}")
      bulundu = True
      break

  if bulundu:
    continue

  # =====================================================
  # STANDART ÖZELLİKLER (SELAM, SAAT, MATEMATİK VB.)
  # =====================================================
  if kelime_benzer_mi(
      a, ["merhaba", "selam", "selamlar", "hey", "naber"], 0.70
  ) or "ne haber" in a:
    saat = datetime.now().hour
    if saat < 12:
      print("Yapay Zeka: Günaydın! ☀️")
    elif saat < 18:
      print("Yapay Zeka: İyi günler! 😊")
    else:
      print("Yapay Zeka: İyi akşamlar! 🌙")

  elif ifade_benzer_mi(
      a, ["nasılsın", "naber", "ne haber", "iyi misin", "ne yapıyorsun"], 0.65
  ):
    print(
        "Yapay Zeka:",
        random.choice([
            "İyiyim, teşekkür ederim! 😄",
            "Gayet iyiyim! Sen nasılsın?",
            "Harikayım!",
        ]),
    )

  elif ifade_benzer_mi(a, ["saat kaç", "saat"], 0.70):
    print("Yapay Zeka: Şu an saat", datetime.now().strftime("%H:%M"))

  elif ifade_benzer_mi(a, ["bugün hangi gün", "tarih ne"], 0.65):
    print("Yapay Zeka: Bugünün tarihi", datetime.now().strftime("%d/%m/%Y"))

  # SAYI TAHMİN OYUNU BAŞLATMA TETİKLEYİCİSİ
  elif (
      "sayı tut" in a
      or "sayı tahmin" in a
      or "oyun oyna" in a
      or "1 ile 10" in a
      or "1 ile 6" in a
  ):
    hedef_sayi = random.randint(1, 10)
    aktif_oyun = "sayi_tahmimi"
    print(
        "Yapay Zeka: Harika! 1 ile 10 arasında bir sayı tuttum. Tahminini"
        " söyle bakalım! 🎮"
    )

  # =====================================================
  # ÖĞRENME SİSTEMİ (ANLAŞILAMAYAN MESAJ İÇİN SEÇENEK SUNMA)
  # =====================================================
  else:
    print("\n[Yapay Zeka Öğrenme Modu] 🧠")
    print(f"Hmm, '{a}' ifadesini tam olarak çözemedim.")
    print("Bu yazdığın şey nedir? Lütfen bir kategori seç:")
    print("1 -> Bu bir oyun mu? (Örn: Sayı tahmin, kelime oyunu vb.)")
    print("2 -> Bu bir kod / teknik soru mu?")
    print("3 -> Bu günlük sohbet / bilgi / espri mi?")
    print("4 -> Hiçbiri / İptal")

    secim = input("Seçimin (1/2/3/4): ").strip()

    if secim == "1":
      print("Yapay Zeka: Anladım, bu bir oyun! Hangi oyunu açmamı istersin?")
      print("1. Sayı Tahmin Oyunu")
      oyun_secim = input("Oyun seçimi (1): ").strip()
      if oyun_secim == "1" or "sayı" in a:
        hafiza["oyunlar"][a] = "sayi_tahmimi"
        hafizayi_kaydet(hafiza)
        print("Yapay Zeka: Bunu sayı tahmin oyunu olarak hafızama kaydettim! 😎")
        hedef_sayi = random.randint(1, 10)
        aktif_oyun = "sayi_tahmimi"
        print(
            "Yapay Zeka: 1 ile 10 arasında bir sayı tuttum. Tahminini söyle"
            " bakalım!"
        )

    elif secim == "2":
      dogru_cevap = input(
          "Yapay Zeka: Bu koda/soruya ne tür bir yanıt vermeliyim? -> "
      )
      hafiza["bilgiler"][a] = dogru_cevap
      hafizayi_kaydet(hafiza)
      print(
          "Yapay Zeka: Harika! Bu bilgiyi öğrendim ve koduma ekledim. Artık"
          " hatırlarım! 🚀"
      )

    elif secim == "3":
      dogru_cevap = input(
          "Yapay Zeka: Buna karşılık ne söylemeliyim? (Örn: Espri veya bilgi)"
          " -> "
      )
      hafiza["bilgiler"][a] = dogru_cevap
      hafizayi_kaydet(hafiza)
      print(
          "Yapay Zeka: Not aldım! Bundan sonra buna bu yanıtı vereceğim. ✨"
      )

    else:
      print("Yapay Zeka: Tamamdır, bunu şimdilik pas geçiyorum. 😊")
