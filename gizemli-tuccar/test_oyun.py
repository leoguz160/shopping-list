# -*- coding: utf-8 -*-
"""Oyunun testleri.   Çalıştır:  python -m unittest -v"""
import contextlib
import io
import os
import random
import unittest

os.environ['GT_HIZ'] = '0'          # testlerde bekleme olmasın

import gizemli_tuccar as oyun
from sprites import SPRITES


class SessizEkran(oyun.Ekran):
    """Çıktı vermeyen, cevapları hazır okuyan sahte ekran."""

    def __init__(self, cevaplar):
        super().__init__('yok')
        self.cevaplar = cevaplar
        self.sayac = 0

    def mesaj_sabit(self, satir1, satir2=''):
        pass

    def mesaj_yaz(self, satir1, satir2=''):
        pass

    def sor(self):
        self.sayac += 1
        return self.cevaplar(self.sayac)


def tum_kartlar():
    return oyun.kartlarim + oyun.bilgisayar_kartlari


def savas_et(benim, rakip, ekran):
    """Savaşı oynatır; renksiz moddaki ASCII çıktıyı yutar."""
    with contextlib.redirect_stdout(io.StringIO()):
        return oyun.savas(benim, rakip, ekran)


class KartTesti(unittest.TestCase):
    def test_hepsinin_sprite_i_ve_ayni_anahtarlari_var(self):
        # Orijinaldeki hata: Gon'da 'Sağlık'/'Güç', diğerlerinde 'Saglik'/'Guc' vardı.
        for k in tum_kartlar():
            self.assertIn('Saglik', k)
            self.assertIn('Guc', k)
            self.assertIn(k['Sprite'], SPRITES)

    def test_sprite_boyutlari_ve_paleti(self):
        for ad, sp in SPRITES.items():
            self.assertEqual(len(sp['satirlar']), oyun.SPR_Y, ad)
            for satir in sp['satirlar']:
                self.assertEqual(len(satir), oyun.SPR_G, ad)
                for harf in set(satir) - {'.'}:
                    self.assertIn(harf, sp['palet'], f'{ad}: {harf} paletde yok')

    def test_ismi_yazarak_kart_bulma(self):
        # Orijinaldeki hata: yazılan isim hiçbir kartla eşleşmiyor, kart string kalıyordu.
        self.assertEqual(oyun.kart_bul('Naruto', oyun.kartlarim), [1])
        self.assertEqual(oyun.kart_bul('  GON ', oyun.kartlarim), [4])
        self.assertEqual(oyun.kart_bul('yuji', oyun.kartlarim), [0])
        self.assertEqual(oyun.kart_bul('goku', oyun.kartlarim), [])          # rakibin kartı
        self.assertEqual(oyun.kart_bul('goku', oyun.bilgisayar_kartlari), [2])
        self.assertEqual(oyun.kart_bul('go', oyun.kartlarim), [])            # çok kısa

    def test_turkce_harfler_sadelesir(self):
        self.assertEqual(oyun.norm('Saldır'), 'saldir')
        self.assertEqual(oyun.norm('ÖZEL'), 'ozel')
        self.assertEqual(oyun.norm('İşçi'), 'isci')


class SavasTesti(unittest.TestCase):
    def test_savas_her_zaman_biter_ve_kartlar_degismez(self):
        onceki = {k['Isim']: (k['Saglik'], k['Guc']) for k in tum_kartlar()}
        rastgele = lambda n: random.choice(['1', '1', '2', '3', 'abc', ''])   # geçersiz girdiler dahil
        for benim in oyun.kartlarim:
            for rakip in oyun.bilgisayar_kartlari:
                for tohum in range(15):
                    random.seed(tohum)
                    ekran = SessizEkran(rastgele)
                    sonuc = savas_et(benim, rakip, ekran)
                    self.assertIsInstance(sonuc, bool)
                    self.assertLess(ekran.sayac, 500)
        # Orijinaldeki hata: savaş kart sözlüklerinin Sağlık değerini kalıcı olarak düşürüyordu.
        sonraki = {k['Isim']: (k['Saglik'], k['Guc']) for k in tum_kartlar()}
        self.assertEqual(onceki, sonraki)

    def test_guc_sagliga_esit_veya_buyukse_tek_vurusta_yener(self):
        # Orijinal kural: Güç >= rakibin Sağlığı -> rakip yenildi.
        o, r = oyun.Savasci(oyun.Naruto, 'oyuncu'), oyun.Savasci(oyun.Monkey_D_Luffy, 'rakip')
        oyun.hasar_uygula(r, o.guc)
        self.assertFalse(r.hayatta)
        self.assertEqual(r.saglik, 0)

    def test_savunma_hasari_yariya_indirir(self):
        r = oyun.Savasci(oyun.Goku, 'rakip')
        r.savunuyor = True
        self.assertEqual(oyun.hasar_uygula(r, 8), 4)
        self.assertEqual(r.saglik, 6)

    def test_ozel_hamle_bir_kez_kullanilir(self):
        random.seed(1)
        ekran = SessizEkran(lambda n: '2')      # hep özel hamle istiyor
        savas_et(oyun.Goku, oyun.Dio_Brando, ekran)       # takılıp kalmamalı

    def test_ozel_hamle_cift_hasar_verir_ya_da_iskalar(self):
        s = oyun.Savasci(oyun.Goku, 'oyuncu')
        sonuclar = {oyun.hasar_hesapla(s, 'ozel')[0] for _ in range(300)}
        self.assertEqual(sonuclar, {0, s.guc * 2})


if __name__ == '__main__':
    unittest.main()
