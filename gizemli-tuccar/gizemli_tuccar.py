# -*- coding: utf-8 -*-
"""Gizemli Tüccarın Oyunu

Pokémon tarzı, piksel sanatlı anime kart savaşı.
Terminalde çalışır, ek kütüphane gerekmez:  python gizemli_tuccar.py
(sprites.py ile aynı klasörde olmalı)
"""

import math
import os
import random
import shutil
import sys
import textwrap
import time

from sprites import SPRITES

# ----------------------------------------------------------------------------
# Ayarlar
# ----------------------------------------------------------------------------
GEN, YUK = 78, 38          # sahne: 78 sütun x 19 satır (her satır 2 piksel yüksekliğinde)
SPR_G, SPR_Y = 32, 36      # bir sprite'ın boyutu (piksel)
SAHNE_SATIR = YUK // 2     # sahnenin kapladığı terminal satırı (19)
HIZ = float(os.environ.get('GT_HIZ', '1'))   # 0 yazarsan bekleme olmadan çalışır (test için)

BEYAZ = (250, 250, 250)
KOYU = (30, 32, 60)
PANEL = (248, 244, 220)    # HUD zemini
KUTU = (22, 26, 58)        # mesaj kutusu zemini
ALTIN = (255, 214, 64)
SIFIRLA = '\033[0m'

O_X, R_X, S_Y = 4, 42, 2   # oyuncu / rakip sprite konumu


def bekle(saniye):
    if HIZ > 0:
        time.sleep(saniye * HIZ)


# ----------------------------------------------------------------------------
# Kartlar   (Sağlık / Güç değerleri orijinal oyundaki gibi)
# ----------------------------------------------------------------------------
def kart(isim, kisa, sprite, saglik, guc, hamle, renk, tip, hikaye):
    return {'Isim': isim, 'Kisa': kisa, 'Sprite': sprite, 'Saglik': saglik, 'Guc': guc,
            'Hamle': hamle, 'Renk': renk, 'Tip': tip, 'Hikaye': hikaye}


Gon = kart('Gon Freecs', 'Gon', 'gon', 5, 7, 'Jajanken: Guu!', (255, 176, 48), 'kure',
           "Gon Freecs, Balina Adası'ndan gelmiş genç bir avcıdır. Kendisi çok kuvvetlidir "
           "fakat genç olduğu için de bir o kadar dayanıksızdır.")
Naruto = kart('Naruto Uzumaki', 'Naruto', 'naruto', 10, 8, 'Rasengan', (74, 168, 255), 'kure',
              "Naruto Uzumaki, Gizli Yaprak Köyü'nden gelmiş genç bir Hokage'dir. Kendisine 9 kuyruklu "
              "tilki mühürlenmiştir ve kendisi evrenin en güçlü savaşçılarından bir tanesidir. "
              "Birçok teknikle tanınır.")
Johnny_Joestar = kart('Johnny Joestar', 'Johnny', 'johnny', 5, 4, 'Tusk ACT 1: Spin', (255, 224, 96), 'kure',
                      "Johnny Joestar, Amerikalı bir Stand kullanıcısıdır. Kendisi bir çatışmadan sonra "
                      "ayaklarını kullanamaz olmuş ve fakir kalmıştır. Parasını kazanmak için Steel Ball Run "
                      "koşusuna katılmıştır. Standında spin gücünü kullanarak insanların uzuvlarını uyuşturur.")
Spike_Spiegel = kart('Spike Spiegel', 'Spike', 'spike', 5, 2, 'Jeet Kune Do', (255, 255, 255), 'yakin',
                     "Mars doğumlu Spike, 27 yaşında uzayda gezgin bir ödül avcısıdır (Cowboy). Kendisi "
                     "Bebop adlı uzay gemisinde eski polis Jet Black ile beraber uzayda ödül avlar.")
Shinji_Ikari_EVA01 = kart('Shinji Ikari EVA-01', 'EVA-01', 'eva01', 10, 5, 'AT Field Darbesi', (255, 154, 48), 'kure',
                          "Lise öğrencisi olan Shinji Ikari, aynı zamanda Tokyo şehrinde bir meka-pilottur. "
                          "Kendisinin bir meka pilot olarak 12 Melek'i öldürmesi gerek, yoksa bu melekler "
                          "Dünya'yı yok edecekler. Epey önemli bir iş açıkçası...")
Monkey_D_Luffy = kart('Monkey D. Luffy', 'Luffy', 'luffy', 4, 5, 'Gomu Gomu Pistol', (255, 106, 58), 'yakin',
                      "Kendisi Yeldeğirmeni Kasabası'ndan gelen Luffy, bir korsandır ve kendi tayfasıyla eski "
                      "büyük korsan Gol D. Roger'ın sakladığı büyük hazineyi Grand Line Okyanusu'nda arar.")
Dio_Brando = kart('Dio Brando', 'Dio', 'dio', 10, 7, 'The World: ZA WARUDO!', (255, 227, 90), 'yakin',
                  "Dio Brando, Londra doğumlu uzun ömürlü bir vampirdir. Joestar ailesiyle alıp veremediği "
                  "vardır fakat her Joestar onu başarılı bir şekilde durduruyor. Standı olan The World'ün "
                  "zamanı kontrol etme ve büyük hasar verme gibi özellikleri vardır. "
                  "Bakalım Johnny onu durdurabilecek mi...")
Yuji_Itadori = kart('Yuji Itadori', 'Yuji', 'yuji', 5, 4, 'Black Flash', (255, 58, 90), 'kure',
                    "Yuji Itadori, Tokyo doğumlu bir lise öğrencisidir. Bir gün okulda arkadaşlarıyla bir "
                    "kutu bulur; kutunun içinde Sukuna adlı büyük bir lanet vardır. Yuji bu laneti yutar ve "
                    "Sukuna ile birlikte yaşamak zorunda kalır. Arkadaşlarına yardım etmek için bu büyük "
                    "güçten faydalanır. Bu yeteneği fark eden büyücü Gojo Satoru, Yuji'yi Jujutsu Teknik "
                    "Lisesi'ne kaydeder. Bakalım Yuji, Sukuna ile beraber büyük bir güce sahip olabilecek mi...")
Killua_Zoldyck = kart('Killua Zoldyck', 'Killua', 'killua', 5, 4, 'Godspeed', (255, 232, 74), 'yakin',
                      "Killua Zoldyck, Zoldyck ailesinin en genç çocuğudur. Kendisi bir suikastçıdır ve birçok "
                      "suikast tekniği bilir. Gon Freecs ile tanışır ve onunla beraber büyük bir maceraya "
                      "atılır. Bakalım Killua, Gon ile beraber büyük bir maceraya atılabilecek mi...")
Goku = kart('Goku', 'Goku', 'goku', 10, 8, 'Kamehameha', (90, 208, 255), 'isin',
            "Goku, bir Saiyan olarak Doğu Dünyası'nda doğmuş ve büyümüş bir uzaylı savaşçıdır. Kendisi "
            "rakibiyle karşılaştığında büyük bir güce sahip olur ve onun görevi 7 tane Dragon Ball'u bulmak "
            "ve bunu kullanarak büyük bir ejderhayı çağırmaktır. Fakat karşısına büyük rakipler çıkacaktır.")

Vegeta = kart('Vegeta', 'Vegeta', 'vegeta', 10, 7, 'Final Flash', (255, 220, 90), 'isin',
              "Vegeta, yok olmuş Saiyan gezegeninin gururlu prensidir. Goku'yla sonsuz bir rekabeti vardır ve "
              "ondan daha güçlü olmak için durmadan antrenman yapar. Havaya dikilmiş saçları ve Saiyan savaş "
              "zırhıyla tanınır.")
Tanjiro_Kamado = kart('Tanjiro Kamado', 'Tanjiro', 'tanjiro', 6, 5, 'Hinokami Kagura', (255, 120, 40), 'yakin',
                      "Tanjiro Kamado, ailesi bir iblis tarafından öldürüldükten sonra iblise dönüşen kız kardeşi "
                      "Nezuko'yu tekrar insan yapmak için İblis Avcısı olan iyi kalpli bir gençtir. Çok güçlü bir "
                      "koku alma duyusu vardır ve Ateş Tanrısı Dansı'nı kullanır.")
Izuku_Midoriya = kart('Izuku Midoriya', 'Deku', 'deku', 7, 6, 'Detroit Smash', (90, 255, 210), 'yakin',
                      "Izuku Midoriya, güçsüz doğmuş ama kahraman olma hayalinden vazgeçmeyen bir gençtir. Tüm "
                      "zamanların en büyük kahramanı All Might'ın gücü One For All'u miras alır ve U.A. Lisesi'nde "
                      "kahraman olmak için eğitim görür.")
Mikasa_Ackerman = kart('Mikasa Ackerman', 'Mikasa', 'mikasa', 6, 6, '3D Manevra Kesişi', (140, 160, 205), 'yakin',
                       "Mikasa Ackerman, çocukluk arkadaşı Eren Yeager'ı korumak için her şeyi yapan usta bir "
                       "askerdir. Olağanüstü Ackerman gücü ve üç boyutlu manevra ekipmanıyla devleri tek başına "
                       "doğrar. Kırmızı atkısını asla çıkarmaz.")
Sailor_Moon = kart('Sailor Moon', 'Moon', 'sailormoon', 5, 4, 'Moon Tiara Action', (255, 150, 200), 'kure',
                   "Usagi Tsukino, sevimli ve biraz uykucu bir lise öğrencisidir. Sailor Moon'a dönüşerek "
                   "'Ay adına seni cezalandıracağım!' der ve Gümüş Kristal'in gücüyle kötülüğe karşı savaşır.")
Sasuke_Uchiha = kart('Sasuke Uchiha', 'Sasuke', 'sasuke', 8, 7, 'Chidori', (60, 110, 255), 'yakin',
                     "Sasuke Uchiha, Uchiha klanından hayatta kalan son ninjalardandır. Abisinden intikam almak "
                     "için güç peşinde koşar. Sharingan gözleri ve Chidori tekniğiyle bilinir; Naruto'nun en büyük "
                     "rakibi ve arkadaşıdır.")
Roronoa_Zoro = kart('Roronoa Zoro', 'Zoro', 'zoro', 7, 6, 'Üç Kılıç: Oni Giri', (200, 255, 120), 'yakin',
                    "Roronoa Zoro, dünyanın en büyük kılıç ustası olmak isteyen Hasır Şapka Korsanları'nın "
                    "kılıç ustasıdır. Üç kılıçla savaşır, sürekli yolunu kaybeder ama Luffy'ye olan sadakatinden "
                    "asla ödün vermez.")
Gojo_Satoru = kart('Gojo Satoru', 'Gojo', 'gojo', 9, 8, 'Hollow Purple', (190, 110, 255), 'kure',
                   "Gojo Satoru, Jujutsu Teknik Lisesi'nin öğretmeni ve en güçlü büyücüsüdür. Altı Göz ve "
                   "Sonsuzluk tekniği sayesinde hiçbir saldırı ona dokunamaz. Gözlerini siyah bir bağla örter ve "
                   "Yuji'nin hocasıdır.")
Saitama = kart('Saitama', 'Saitama', 'saitama', 10, 8, 'Ciddi Yumruk', (255, 200, 60), 'yakin',
               "Saitama, her düşmanı tek yumrukta yenen, bu yüzden hayatı sıkıcı geçen bir kahramandır. Kel "
               "kafası, sarı kostümü, kırmızı eldivenleri ve beyaz pelerini ile tanınır. En büyük derdi "
               "indirimdeki market ürünlerini kaçırmamaktır.")
Ichigo_Kurosaki = kart('Ichigo Kurosaki', 'Ichigo', 'ichigo', 8, 7, 'Getsuga Tenshou', (92, 72, 230), 'kure',
                       "Ichigo Kurosaki, ölen ruhları görebilen turuncu saçlı bir lise öğrencisidir. Shinigami "
                       "güçlerini devralır ve dev kılıcı Zangetsu ile Hollow'lara karşı savaşır. Sevdiklerini "
                       "korumak için Getsuga Tenshou'yu kullanır.")

kartlarim = [Yuji_Itadori, Naruto, Johnny_Joestar, Shinji_Ikari_EVA01, Gon,
             Vegeta, Tanjiro_Kamado, Izuku_Midoriya, Mikasa_Ackerman, Sailor_Moon]
bilgisayar_kartlari = [Dio_Brando, Killua_Zoldyck, Goku, Spike_Spiegel, Monkey_D_Luffy,
                       Sasuke_Uchiha, Roronoa_Zoro, Gojo_Satoru, Saitama, Ichigo_Kurosaki]


# ----------------------------------------------------------------------------
# Küçük yardımcılar
# ----------------------------------------------------------------------------
_TR = str.maketrans('ıİşŞğĞüÜöÖçÇ', 'iissgguuoocc')


def norm(metin):
    """Türkçe harfleri sadeleştirir: 'Saldır' -> 'saldir' (yazım hatalarına karşı)."""
    return metin.translate(_TR).lower().strip()


def kart_bul(girdi, kartlar):
    g = norm(girdi)
    if len(g) < 3:
        return []
    return [i for i, k in enumerate(kartlar) if g in norm(k['Isim']) or g in norm(k['Kisa'])]


def hex_rgb(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def karistir(a, b, t):
    return (round(a[0] * (1 - t) + b[0] * t), round(a[1] * (1 - t) + b[1] * t), round(a[2] * (1 - t) + b[2] * t))


# ----------------------------------------------------------------------------
# Renk desteği (truecolor / 256 renk / renksiz)
# ----------------------------------------------------------------------------
def renk_modu_sec():
    zorla = os.environ.get('GT_RENK')
    if zorla in ('true', '256', 'yok'):
        return zorla
    tty_mi = getattr(sys.stdout, 'isatty', lambda: False)()
    if os.environ.get('NO_COLOR') or os.environ.get('TERM') == 'dumb' or not tty_mi:
        return 'yok'          # IDLE, Thonny, dosyaya yönlendirme vb.
    if os.name == 'nt':
        os.system('')         # Windows'ta ANSI renk desteğini açar
    ct = os.environ.get('COLORTERM', '').lower()
    if ct in ('truecolor', '24bit') or os.environ.get('WT_SESSION') or \
            os.environ.get('TERM_PROGRAM') in ('vscode', 'iTerm.app', 'WezTerm', 'ghostty'):
        return 'true'
    return '256'


MOD = 'yok'
_KUP = (0, 95, 135, 175, 215, 255)
_ONBELLEK = {}


def en_yakin_256(rgb):
    ri, gi, bi = (min(range(6), key=lambda i: abs(_KUP[i] - v)) for v in rgb)
    kup = (_KUP[ri], _KUP[gi], _KUP[bi])
    gri = max(0, min(23, round((sum(rgb) / 3 - 8) / 10)))
    gv = 8 + 10 * gri

    def uzak(c):
        return sum((a - b) ** 2 for a, b in zip(c, rgb))
    if uzak((gv, gv, gv)) < uzak(kup):
        return 232 + gri
    return 16 + 36 * ri + 6 * gi + bi


def kod(renk, taban):
    """ANSI renk kodu. taban: 38 = yazı rengi, 48 = zemin rengi."""
    anahtar = (renk, taban, MOD)
    k = _ONBELLEK.get(anahtar)
    if k is None:
        if MOD == 'true':
            k = '\033[%d;2;%d;%d;%dm' % (taban, *renk)
        else:
            k = '\033[%d;5;%dm' % (taban, en_yakin_256(renk))
        _ONBELLEK[anahtar] = k
    return k


# ----------------------------------------------------------------------------
# Sprite'lar ve sahne (piksel tamponu)
# ----------------------------------------------------------------------------
_SPRITE_ONBELLEK = {}


def sprite_al(anahtar):
    if anahtar not in _SPRITE_ONBELLEK:
        d = SPRITES[anahtar]
        palet = {harf: hex_rgb(r) for harf, r in d['palet'].items()}
        _SPRITE_ONBELLEK[anahtar] = [[palet.get(ch) for ch in satir] for satir in d['satirlar']]
    return _SPRITE_ONBELLEK[anahtar]


def elips_doldur(buf, cx, cy, rx, ry, renk):
    for y in range(max(0, int(cy - ry)), min(YUK, int(cy + ry) + 1)):
        for x in range(max(0, int(cx - rx)), min(GEN, int(cx + rx) + 1)):
            dx, dy = (x + .5 - cx) / rx, (y + .5 - cy) / ry
            if dx * dx + dy * dy <= 1:
                buf[y][x] = renk


def arka_plan_olustur():
    rng = random.Random(7)
    ufuk = 26
    ust, alt = (88, 168, 236), (196, 232, 255)
    buf = []
    for y in range(YUK):
        if y < ufuk:
            buf.append([karistir(ust, alt, y / ufuk)] * GEN)
        else:
            buf.append([(98, 192, 90) if ((y - ufuk) // 3) % 2 == 0 else (88, 180, 82)] * GEN)
    for x in range(GEN):                                       # uzaktaki tepeler
        h = int(3 + 2.2 * math.sin(x / 7.0) + 1.6 * math.sin(x / 3.1 + 1))
        for y in range(ufuk - h, ufuk):
            buf[y][x] = (70, 160, 98) if y == ufuk - h else (52, 138, 82)
    for cx, cy, w in ((12, 6, 7), (35, 10, 5), (58, 5, 8), (70, 11, 4)):    # bulutlar
        elips_doldur(buf, cx, cy, w, 2.2, (255, 255, 255))
        elips_doldur(buf, cx + w * .5, cy - 1, w * .6, 1.8, (255, 255, 255))
        elips_doldur(buf, cx, cy + 1.2, w * .9, 1.2, (226, 240, 252))
    for _ in range(110):                                       # çimen tüyleri
        buf[rng.randrange(ufuk + 1, YUK)][rng.randrange(GEN)] = (66, 156, 62)
    return buf


ARKA_PLAN = arka_plan_olustur()


class Sahne:
    """Tek bir kare: arka plan + karakterler + efektler + yazılar."""

    def __init__(self):
        self.buf = [satir[:] for satir in ARKA_PLAN]
        self.katman = {}          # (satir, sutun) -> (karakter, yazı rengi, zemin rengi)

    def platform(self, cx, cy):
        elips_doldur(self.buf, cx, cy + 1, 19, 3.4, (44, 98, 48))
        elips_doldur(self.buf, cx, cy, 19, 2.8, (172, 232, 128))

    def sprite(self, anahtar, x0, y0, tint=None, oran=0.0, kes=None):
        for y, satir in enumerate(sprite_al(anahtar)):
            yy = y0 + y
            if not 0 <= yy < YUK or (kes is not None and yy >= kes):
                continue
            for x, c in enumerate(satir):
                if c is not None and 0 <= x0 + x < GEN:
                    self.buf[yy][x0 + x] = karistir(c, tint, oran) if (tint and oran) else c

    def daire(self, cx, cy, r, renk):
        elips_doldur(self.buf, cx, cy, r, r, renk)

    def dikdortgen(self, x0, y0, x1, y1, renk):
        for y in range(max(0, int(y0)), min(YUK, int(y1) + 1)):
            for x in range(max(0, int(x0)), min(GEN, int(x1) + 1)):
                self.buf[y][x] = renk

    def parlat(self, oran, renk=BEYAZ):
        self.buf = [[karistir(c, renk, oran) for c in satir] for satir in self.buf]

    def panel(self, r0, c0, genislik, yukseklik, bg):
        for r in range(r0, r0 + yukseklik):
            for c in range(c0, c0 + genislik):
                self.katman[(r, c)] = (' ', BEYAZ, bg)

    def yazi(self, r, c, metin, fg=BEYAZ, bg=KUTU):
        for i, ch in enumerate(metin):
            if 0 <= c + i < GEN:
                self.katman[(r, c + i)] = (ch, fg, bg)

    def hud(self, s, c0):
        oran = s.saglik / s.max
        renk = (88, 208, 112) if oran > .5 else (240, 208, 64) if oran > .25 else (224, 72, 72)
        isaret = '◈ ' if s.savunuyor else '★ ' if s.ozel_var else '  '
        dolu = math.ceil(10 * oran) if s.saglik > 0 else 0
        parcalar = [(f' {isaret}{s.kisa:<8}', KOYU), (f'Güç {s.guc:<2} CAN ', KOYU),
                    ('█' * dolu, renk), ('█' * (10 - dolu), (206, 200, 178)), (f' {s.saglik:>2}/{s.max:<2} ', KOYU)]
        c = c0
        for metin, fg in parcalar:
            self.yazi(0, c, metin, fg, PANEL)
            c += len(metin)


def sahne_satirlari(sahne):
    satirlar = []
    for r in range(SAHNE_SATIR):
        parca, fg, bg = [], None, None
        for c in range(GEN):
            h = sahne.katman.get((r, c))
            if h:
                ch, f, b = h
            else:
                ust, alt = sahne.buf[2 * r][c], sahne.buf[2 * r + 1][c]
                ch, f, b = (' ', None, ust) if ust == alt else ('▀', ust, alt)
            if b != bg:
                parca.append(kod(b, 48))
                bg = b
            if ch != ' ' and f != fg:
                parca.append(kod(f, 38))
                fg = f
            parca.append(ch)
        parca.append(SIFIRLA)
        satirlar.append(''.join(parca))
    return satirlar


def kutu_satirlari(mesaj):
    satirlar = [kod(KUTU, 48) + kod(ALTIN, 38) + '━' * GEN + SIFIRLA]
    for metin in mesaj:
        satirlar.append(kod(KUTU, 48) + kod(BEYAZ, 38) + (' ' + metin).ljust(GEN)[:GEN] + SIFIRLA)
    return satirlar


# ----------------------------------------------------------------------------
# Renksiz mod için ASCII sprite (IDLE / Thonny gibi ortamlar)
# ----------------------------------------------------------------------------
def ascii_sprite(anahtar):
    px = sprite_al(anahtar)
    rampa = '@%#*+=-:. '
    satirlar = []
    for y in range(0, SPR_Y, 2):
        s = ''
        for x in range(SPR_G):
            renkler = [c for c in (px[y][x], px[y + 1][x]) if c]
            if not renkler:
                s += ' '
                continue
            parlak = sum(sum(c) / 3 for c in renkler) / len(renkler)
            s += rampa[min(9, int(parlak / 25.6))]
        satirlar.append(s.rstrip())
    return satirlar


# ----------------------------------------------------------------------------
# Ekran: çizim, mesaj kutusu, girdi
# ----------------------------------------------------------------------------
class Ekran:
    def __init__(self, mod):
        self.mod = mod
        self.renkli = mod != 'yok'
        self.mesaj = ['', '']
        self.son = None

    def yaz(self, s):
        sys.stdout.write(s)
        sys.stdout.flush()

    def baslat(self):
        if self.renkli:
            self.yaz('\033[?1049h\033[?25l\033[2J')      # ayrı ekran + imleci gizle

    def bitir(self):
        if self.renkli:
            self.yaz(SIFIRLA + '\033[?25h\033[?1049l')

    def ciz(self, sahne=None):
        if not self.renkli:
            return
        if sahne is not None:
            self.son = sahne
        if self.son is None:
            return
        satirlar = sahne_satirlari(self.son) + kutu_satirlari(self.mesaj)
        self.yaz('\033[H' + '\r\n'.join(satirlar) + SIFIRLA + '\033[J')

    def mesaj_sabit(self, satir1, satir2=''):
        self.mesaj = [satir1, satir2]
        if self.renkli:
            self.ciz()
        else:
            print(satir1)
            if satir2:
                print(satir2)

    def mesaj_yaz(self, satir1, satir2=''):
        """Mesajı daktilo gibi harf harf yazar, sonra kısa bir süre bekler."""
        if not self.renkli:
            print(satir1)
            if satir2:
                print(satir2)
            bekle(0.5)
            return
        self.mesaj = ['', '']
        self.ciz()
        for i, metin in enumerate((satir1, satir2)):
            if not metin:
                continue
            self.yaz('\033[%d;3H' % (SAHNE_SATIR + 2 + i) + kod(KUTU, 48) + kod(BEYAZ, 38))
            for ch in metin:
                self.yaz(ch)
                bekle(0.012)
            self.mesaj[i] = metin
        bekle(0.7)

    def sor(self):
        if self.renkli:
            self.yaz('\033[%d;1H' % (SAHNE_SATIR + 4) + SIFIRLA + '\033[K\033[?25h')
        self.yaz(' ▶ ')
        try:
            cevap = input()
        except EOFError:
            raise SystemExit
        finally:
            if self.renkli:
                self.yaz('\033[?25l')
        return cevap.strip()


# ----------------------------------------------------------------------------
# Savaşçı ve savaş kuralları
# ----------------------------------------------------------------------------
class Savasci:
    """Savaş sırasındaki kart durumu. Kartın kendisi değişmez (orijinal koddaki hata)."""

    def __init__(self, kart, taraf):
        self.kart = kart
        self.taraf = taraf                 # 'oyuncu' veya 'rakip'
        self.isim = kart['Isim']
        self.kisa = kart['Kisa']
        self.max = kart['Saglik']
        self.saglik = self.max
        self.guc = kart['Guc']
        self.ozel_var = True
        self.savunuyor = False

    @property
    def hayatta(self):
        return self.saglik > 0


def hasar_hesapla(saldiran, hamle):
    """(hasar, kritik_mi, isabet_mi)"""
    if hamle == 'ozel':
        if random.random() > 0.75:
            return 0, False, False
        return saldiran.guc * 2, False, True
    kritik = random.random() < 0.125
    return (math.ceil(saldiran.guc * 1.5) if kritik else saldiran.guc), kritik, True


def hasar_uygula(hedef, hasar):
    if hedef.savunuyor:
        hasar = max(1, math.ceil(hasar / 2))
    hedef.saglik = max(0, hedef.saglik - hasar)
    return hasar


def bilgisayar_hamlesi(ben):
    r = random.random()
    if ben.ozel_var and r < 0.30:
        return 'ozel'
    if r > 0.88:
        return 'savun'
    return 'saldir'


# ----------------------------------------------------------------------------
# Savaş sahnesi ve animasyonlar
# ----------------------------------------------------------------------------
def savas_sahnesi(o, r, ayar=None, efekt=None):
    ayar = ayar or {}
    s = Sahne()
    s.platform(O_X + 16, S_Y + 33)
    s.platform(R_X + 16, S_Y + 33)
    for sv, x0 in ((o, O_X), (r, R_X)):
        a = ayar.get(sv.taraf, {})
        if not a.get('gizli'):
            s.sprite(sv.kart['Sprite'], x0 + a.get('dx', 0), S_Y + a.get('dy', 0),
                     a.get('tint'), a.get('oran', 0), a.get('kes'))
    if efekt:
        efekt(s)
    s.hud(o, 1)
    s.hud(r, 40)
    return s


def kare_ciz(ekran, o, r, ayar=None, efekt=None, sure=0.04):
    if not ekran.renkli:
        return
    ekran.ciz(savas_sahnesi(o, r, ayar, efekt))
    bekle(sure)


def merkez(sv):
    return (O_X if sv.taraf == 'oyuncu' else R_X) + 16, S_Y + 18


def vurus_efekti(s, hedef, adim, renk=(255, 240, 120)):
    cx, cy = merkez(hedef)
    r = 2 + adim * 2.2
    for aci in range(0, 360, 45):
        x, y = cx + r * math.cos(math.radians(aci)), cy + r * math.sin(math.radians(aci))
        s.dikdortgen(x - 1, y - 1, x + 1, y + 1, renk if adim % 2 == 0 else BEYAZ)
    if adim < 3:
        s.daire(cx, cy, 4 - adim, BEYAZ)


def saldiri_animasyonu(ekran, o, r, a, d):
    if not ekran.renkli:
        return
    yon = 1 if a.taraf == 'oyuncu' else -1
    for dx in (0, 2, 5, 9, 13, 17):
        kare_ciz(ekran, o, r, {a.taraf: {'dx': yon * dx}}, sure=0.025)
    for i in range(6):
        vur = i % 2 == 0
        ayar = {a.taraf: {'dx': yon * (17 - i * 3)},
                d.taraf: {'dx': yon * (3 if vur else -3), 'tint': BEYAZ, 'oran': .7 if vur else 0}}
        kare_ciz(ekran, o, r, ayar, lambda s, i=i: vurus_efekti(s, d, i), 0.04)
    for dx in (5, 2, 0):
        kare_ciz(ekran, o, r, {a.taraf: {'dx': yon * dx}}, sure=0.025)


def ozel_animasyon(ekran, o, r, a, d, isabet):
    if not ekran.renkli:
        return
    renk, tip = a.kart['Renk'], a.kart['Tip']
    yon = 1 if a.taraf == 'oyuncu' else -1
    x0 = O_X if a.taraf == 'oyuncu' else R_X
    ax, ay = merkez(a)
    dx_, dy_ = merkez(d)
    on = ax + yon * 14                                    # saldıranın "elinin" önü
    ileri = yon * 18 if tip == 'yakin' else 0             # yakın dövüşte saldıran öne atılır

    for i in range(8):                                    # enerji toplama
        def topla(s, i=i):
            s.daire(on, ay, 1 + i * .5, renk)
            s.daire(on, ay, .6 + i * .25, BEYAZ)
        kare_ciz(ekran, o, r, {a.taraf: {'tint': renk, 'oran': .55 if i % 2 == 0 else .1}}, topla, 0.05)

    if tip == 'yakin':                                    # hızla dalış (arkada renkli iz)
        for adim in range(7):
            kon = yon * adim * 3

            def iz(s, kon=kon):
                for k in (3, 2, 1):
                    s.sprite(a.kart['Sprite'], x0 + kon - yon * k * 4, S_Y, renk, .7)
                s.sprite(a.kart['Sprite'], x0 + kon, S_Y)
            kare_ciz(ekran, o, r, {a.taraf: {'gizli': True}}, iz, 0.03)
    else:
        for adim in range(10):                            # mermi / ışın
            px = on + (dx_ - on) * (adim + 1) / 10

            def mermi(s, px=px):
                if tip == 'isin':
                    s.dikdortgen(min(on, px), ay - 3, max(on, px), ay + 3, renk)
                    s.dikdortgen(min(on, px), ay - 1, max(on, px), ay + 1, BEYAZ)
                    s.daire(px, ay, 5, renk)
                    s.daire(px, ay, 2.5, BEYAZ)
                else:
                    for k in range(3):
                        s.daire(px - yon * k * 4, ay, 4 - k, renk)
                    s.daire(px, ay, 2, BEYAZ)
            kare_ciz(ekran, o, r, None, mermi, 0.035)

    if not isabet:
        for dx in (3, 6, 6, 3, 0):                         # savunan yana kayarak kaçar
            kare_ciz(ekran, o, r, {a.taraf: {'dx': ileri}, d.taraf: {'dx': yon * dx}}, sure=0.04)
    else:
        for i in range(8):                                # patlama
            vur = i % 2 == 0
            ayar = {a.taraf: {'dx': ileri},
                    d.taraf: {'dx': yon * (4 if vur else -4), 'tint': renk if vur else BEYAZ, 'oran': .75}}

            def patla(s, i=i):
                if i < 3:
                    s.parlat(.45 - i * .13, renk)
                if i < 4:
                    s.daire(dx_, dy_, 3 + i * 1.2, renk)
                vurus_efekti(s, d, i, renk)
            kare_ciz(ekran, o, r, ayar, patla, 0.05)
    for kon in (ileri * 2 // 3, ileri // 3, 0):           # saldıran yerine döner
        if ileri:
            kare_ciz(ekran, o, r, {a.taraf: {'dx': kon}}, sure=0.03)


def kalkan_animasyonu(ekran, o, r, a):
    if not ekran.renkli:
        return
    cx, cy = merkez(a)
    for i in range(10):
        yaricap = 17 + (i % 3)
        renk = (120, 220, 255) if i % 2 == 0 else (200, 245, 255)

        def kalkan(s, yaricap=yaricap, renk=renk):
            for aci in range(0, 360, 6):
                x = cx + (yaricap - 1) * math.cos(math.radians(aci))
                y = cy + (yaricap + 1) * math.sin(math.radians(aci))
                s.dikdortgen(x - 1, y - 1, x + 1, y, renk)
        kare_ciz(ekran, o, r, None, kalkan, 0.05)


def can_dusur(ekran, hedef, eski, yeni, o, r):
    """HP çubuğunu birer birer eritir."""
    for v in range(eski - 1, yeni - 1, -1):
        hedef.saglik = v
        kare_ciz(ekran, o, r, None, None, 0.09)
    hedef.saglik = yeni


def bayilma_animasyonu(ekran, o, r, kaybeden):
    if not ekran.renkli:
        return
    for i in range(0, 36, 2):
        kare_ciz(ekran, o, r, {kaybeden.taraf: {'dy': i, 'kes': S_Y + 34, 'tint': (24, 20, 40), 'oran': min(.85, i / 24)}}, sure=0.05)
    kare_ciz(ekran, o, r, {kaybeden.taraf: {'gizli': True}}, sure=0.2)


def zafer_animasyonu(ekran, o, r, kazanan, kaybeden):
    if not ekran.renkli:
        return
    for dy in (0, -1, -2, -2, -1, 0, -1, -2, -2, -1, 0):
        kare_ciz(ekran, o, r, {kaybeden.taraf: {'gizli': True}, kazanan.taraf: {'dy': dy}}, sure=0.05)


def giris_animasyonu(ekran, o, r):
    for i in range(14):
        kare_ciz(ekran, o, r, {'oyuncu': {'gizli': True}, 'rakip': {'dx': (13 - i) * 5}}, sure=0.03)
    ekran.mesaj_yaz(f'Karşına {r.isim} çıktı!', f'Güç {r.guc}, Can {r.max}  -  Özel hamlesi: {r.kart["Hamle"]}')
    for i in range(14):
        kare_ciz(ekran, o, r, {'oyuncu': {'dx': -(13 - i) * 3}}, sure=0.03)
    ekran.mesaj_yaz(f'Hadi {o.isim}, sıra sende!')


def plain_durum(o, r):
    """Renksiz modda: iki sprite'ı yan yana ASCII olarak ve durum satırlarını yazar."""
    a, b = ascii_sprite(o.kart['Sprite']), ascii_sprite(r.kart['Sprite'])
    print()
    for x, y in zip(a, b):
        print(x.ljust(36) + y)
    print(f'{o.isim}: Can {o.saglik}/{o.max}, Güç {o.guc}'.ljust(36) + f'{r.isim}: Can {r.saglik}/{r.max}, Güç {r.guc}')


# ----------------------------------------------------------------------------
# Savaş akışı
# ----------------------------------------------------------------------------
def hamle_uygula(ekran, o, r, a, d, hamle):
    a.savunuyor = False                       # savunma, kendi sıran gelince biter
    onek = 'Rakip ' if a.taraf == 'rakip' else ''
    if hamle == 'savun':
        ekran.mesaj_yaz(f'{onek}{a.isim} savunmaya geçti!', 'Gelen hasar yarıya inecek ve 1 Can yenilendi.')
        kalkan_animasyonu(ekran, o, r, a)
        a.saglik = min(a.max, a.saglik + 1)
        a.savunuyor = True
        ekran.ciz(savas_sahnesi(o, r))
        return
    if hamle == 'ozel':
        a.ozel_var = False
        ekran.mesaj_yaz(f'{onek}{a.isim}: {a.kart["Hamle"]}!')
    else:
        ekran.mesaj_yaz('Saldırıyorsunuz!' if a.taraf == 'oyuncu' else f'Rakip sırası! {a.isim} saldırıyor!')
    hasar, kritik, isabet = hasar_hesapla(a, hamle)
    if hamle == 'ozel':
        ozel_animasyon(ekran, o, r, a, d, isabet)
    else:
        saldiri_animasyonu(ekran, o, r, a, d)
    if not isabet:
        ekran.mesaj_yaz('Iskaladı!', f'{d.isim} saldırıdan kıl payı kurtuldu.')
        return
    eski, savundu = d.saglik, d.savunuyor
    hasar = hasar_uygula(d, hasar)         # d.saglik artık yeni değer
    yeni = d.saglik
    d.saglik = eski                        # çubuk animasyonla yeni değere insin
    can_dusur(ekran, d, eski, yeni, o, r)
    d.savunuyor = False
    ek = ' KRİTİK VURUŞ!' if kritik else ''
    if not d.hayatta:
        return
    ekran.mesaj_yaz(f'{d.isim} {hasar} hasar aldı!{ek}',
                    'Savunma hasarı yarıya indirdi!' if savundu else ('Rakip yaralandı!' if d.taraf == 'rakip' else 'Yaralandınız!'))


def oyuncu_hamlesi(ekran, o):
    while True:
        ozel = o.kart['Hamle'] + ('' if o.ozel_var else ' (kullanıldı)')
        ekran.mesaj_sabit(f'Ne yapacaksın, {o.kisa}?     Can {o.saglik}/{o.max}   Güç {o.guc}',
                          f'[1] Saldır     [2] Özel: {ozel}     [3] Savun')
        c = norm(ekran.sor())
        if c in ('1', 's', 'saldir'):
            return 'saldir'
        if c in ('2', 'o', 'ozel'):
            if o.ozel_var:
                return 'ozel'
            ekran.mesaj_sabit('Özel hamleni bu savaşta zaten kullandın!', '')
            bekle(1.0)
        elif c in ('3', 'v', 'savun'):
            return 'savun'
        else:
            ekran.mesaj_sabit('Geçersiz seçim! 1, 2 veya 3 yaz.', '')
            bekle(1.0)


def savas(oyuncu_karti, rakip_karti, ekran):
    """Savaşı oynar. Oyuncu kazanırsa True döner."""
    o, r = Savasci(oyuncu_karti, 'oyuncu'), Savasci(rakip_karti, 'rakip')
    ekran.mesaj = ['', '']
    giris_animasyonu(ekran, o, r)
    while True:
        ekran.ciz(savas_sahnesi(o, r))
        if not ekran.renkli:
            plain_durum(o, r)
        hamle_uygula(ekran, o, r, o, r, oyuncu_hamlesi(ekran, o))
        if not r.hayatta:
            bayilma_animasyonu(ekran, o, r, r)
            zafer_animasyonu(ekran, o, r, o, r)
            ekran.mesaj_yaz('Rakip yenildi!', 'KAZANDINIZ!  Tebrikler!')
            return True
        hamle_uygula(ekran, o, r, r, o, bilgisayar_hamlesi(r))
        if not o.hayatta:
            bayilma_animasyonu(ekran, o, r, o)
            ekran.mesaj_yaz('Kaybettiniz!', f'{o.isim} yere yığıldı...')
            return False


# ----------------------------------------------------------------------------
# Başlık, kart seçimi, rakip çekilişi
# ----------------------------------------------------------------------------
def baslik_ekrani(ekran):
    if not ekran.renkli:
        print('=' * 50)
        print('      GİZEMLİ TÜCCARIN OYUNU')
        print('      Pokémon tarzı anime kart savaşı')
        print('=' * 50)
        ekran.mesaj_sabit('Başlamak için Enter tuşuna bas.')
        ekran.sor()
        return
    s = Sahne()
    secilen = random.sample(kartlarim + bilgisayar_kartlari, 3)
    for kart_, x0 in zip(secilen, (-1, 23, 47)):
        s.sprite(kart_['Sprite'], x0, 12)               # boydan değil, "poster" gibi bel hizasından kesilir
    s.panel(1, 12, 54, 5, KUTU)
    s.yazi(1, 12, '┌' + '─' * 52 + '┐', ALTIN)
    s.yazi(5, 12, '└' + '─' * 52 + '┘', ALTIN)
    for r_ in range(2, 5):
        s.yazi(r_, 12, '│', ALTIN)
        s.yazi(r_, 65, '│', ALTIN)
    s.yazi(2, 14, 'G İ Z E M L İ   T Ü C C A R I N   O Y U N U'.center(50), ALTIN)
    s.yazi(3, 14, 'Pokémon tarzı anime kart savaşı'.center(50), BEYAZ)
    s.yazi(4, 14, f'★  {len(kartlarim)} kart  ·  1 rakip  ·  tek kazanan  ★'.center(50), (160, 200, 255))
    ekran.mesaj_sabit("Başlamak için Enter'a bas...", '')
    ekran.ciz(s)
    ekran.sor()


def dolu_hucre(deger, azami, genislik=10):
    dolu = max(1, round(genislik * deger / azami)) if deger > 0 else 0
    return dolu


def kart_sahnesi(k, sira, kartlar, oyuncunun_mu):
    s = Sahne()
    s.platform(21, S_Y + 33)
    s.sprite(k['Sprite'], 5, S_Y)
    s.panel(0, 0, GEN, 1, KUTU)
    baslik = ' SENİN KARTLARIN ' if oyuncunun_mu else ' RAKİBİN KARTLARI '
    s.yazi(0, 0, baslik, KOYU, ALTIN if oyuncunun_mu else (255, 140, 140))
    c = len(baslik) + 2
    for i in range(len(kartlar)):
        etiket = f' {i + 1} '
        secili = i == sira
        s.yazi(0, c, etiket, KOYU if secili else BEYAZ, (255, 255, 255) if secili else KUTU)
        c += len(etiket) + 1
    s.panel(1, 37, 41, 18, KUTU)
    s.yazi(2, 38, k['Isim'], ALTIN)
    s.yazi(3, 38, 'CAN ', BEYAZ)
    s.yazi(3, 42, '█' * dolu_hucre(k['Saglik'], 10), (88, 208, 112))
    s.yazi(3, 42 + dolu_hucre(k['Saglik'], 10), '█' * (10 - dolu_hucre(k['Saglik'], 10)), (70, 76, 110))
    s.yazi(3, 53, str(k['Saglik']), BEYAZ)
    s.yazi(4, 38, 'GÜÇ ', BEYAZ)
    s.yazi(4, 42, '█' * dolu_hucre(k['Guc'], 10), (255, 150, 70))
    s.yazi(4, 42 + dolu_hucre(k['Guc'], 10), '█' * (10 - dolu_hucre(k['Guc'], 10)), (70, 76, 110))
    s.yazi(4, 53, str(k['Guc']), BEYAZ)
    s.yazi(5, 38, 'Özel: ', BEYAZ)
    s.yazi(5, 44, k['Hamle'], k['Renk'])
    satirlar = textwrap.wrap(k['Hikaye'], 39)
    for i, metin in enumerate(satirlar[:12]):
        s.yazi(7 + i, 38, metin, (225, 228, 245))
    return s


def kart_secimi(ekran):
    """Oyuncunun kartını seçtirir. Çıkmak istenirse None döner."""
    liste, sira, bildirim = 'oyuncu', 0, ''
    while True:
        kartlar = kartlarim if liste == 'oyuncu' else bilgisayar_kartlari
        k = kartlar[sira]
        if ekran.renkli:
            ekran.ciz(kart_sahnesi(k, sira, kartlar, liste == 'oyuncu'))
        else:
            print(f'\n--- {k["Isim"]}  (Can {k["Saglik"]}, Güç {k["Guc"]}, Özel: {k["Hamle"]}) ---')
            print('\n'.join(ascii_sprite(k['Sprite'])))
            print(textwrap.fill(k['Hikaye'], 70))
        ekran.mesaj_sabit(bildirim or f'Enter: sonraki   p: önceki   1-{len(kartlar)}: numara   r: rakip kartları   q: çık',
                          's: BU KARTI SEÇ  (kart ismini yazarak da seçebilirsin)' if liste == 'oyuncu'
                          else 'Bunlar rakibin kartları! (r: kendi kartlarına dön)')
        bildirim = ''
        c = norm(ekran.sor())
        if c in ('', 'n', 'ileri', '>', 'sonraki'):
            sira = (sira + 1) % len(kartlar)
        elif c in ('p', 'geri', '<', 'onceki'):
            sira = (sira - 1) % len(kartlar)
        elif c in ('r', 'rakip'):
            liste, sira = ('rakip' if liste == 'oyuncu' else 'oyuncu'), 0
        elif c in ('q', 'cik', 'cikis'):
            return None
        elif c in ('s', 'e', 'sec', 'evet'):
            if liste == 'oyuncu':
                return k
            bildirim = 'Bu rakibin kartı! Kendi kartlarına dönmek için r yaz.'
        elif c.isdigit() and 1 <= int(c) <= len(kartlar):
            sira = int(c) - 1
        else:
            benim, rakibin = kart_bul(c, kartlarim), kart_bul(c, bilgisayar_kartlari)
            if len(benim) == 1:
                return kartlarim[benim[0]]
            if len(rakibin) == 1:
                liste, sira = 'rakip', rakibin[0]
                bildirim = f'{bilgisayar_kartlari[sira]["Isim"]} rakibin kartı! Kendi kartlarından seç.'
            else:
                bildirim = f'Anlamadım. Numara (1-{len(kartlar)}), kart ismi, s (seç) veya Enter yaz.'


def rakip_cek(ekran):
    """Rakibin kartını 'Bu kimin Pokémon'u?' tarzı silüetle çeker."""
    secilen = random.choice(bilgisayar_kartlari)
    n = len(bilgisayar_kartlari)
    bas = bilgisayar_kartlari.index(secilen)
    if not ekran.renkli:
        ekran.mesaj_sabit(f'Rakibin kartı: {secilen["Isim"]}  (Can {secilen["Saglik"]}, Güç {secilen["Guc"]})')
        return secilen
    toplam = 16
    for i in range(toplam):
        idx = (bas - (toplam - 1 - i)) % n
        s = Sahne()
        s.platform(39, S_Y + 33)
        s.sprite(bilgisayar_kartlari[idx]['Sprite'], 23, S_Y, (14, 14, 40), .93)
        s.panel(0, 0, GEN, 1, KUTU)
        s.yazi(0, 0, ' RAKİBİN KARTI ÇEKİLİYOR...'.ljust(GEN), ALTIN)
        ekran.mesaj = ['Gizemli Tüccar kartları karıştırıyor...', '']
        ekran.ciz(s)
        bekle(0.06 + 0.014 * i * i / 4)
    for oran in (1.0, .6, .3, .1, 0):
        s = Sahne()
        s.platform(39, S_Y + 33)
        s.sprite(secilen['Sprite'], 23, S_Y)
        s.parlat(oran * .8)
        s.panel(0, 0, GEN, 1, KUTU)
        s.yazi(0, 0, ' RAKİBİN KARTI'.ljust(GEN), ALTIN)
        ekran.ciz(s)
        bekle(0.07)
    ekran.mesaj_yaz(f'Rakibin kartı: {secilen["Isim"]}!', f'Can {secilen["Saglik"]}  ·  Güç {secilen["Guc"]}  ·  Özel: {secilen["Hamle"]}')
    return secilen


def tekrar_mi(ekran):
    while True:
        ekran.mesaj_sabit('Tekrar oynamak ister misin?', '[e] Evet     [h] Hayır')
        c = norm(ekran.sor())
        if c in ('e', 'evet', 'y', 'yes'):
            return True
        if c in ('h', 'hayir', 'n', 'no', 'q'):
            return False


def boyut_kontrol(ekran):
    if not ekran.renkli:
        return
    kol, satir = shutil.get_terminal_size((80, 24))
    if kol < GEN + 2 or satir < SAHNE_SATIR + 5:
        print(f'Terminal penceren küçük ({kol}x{satir}). En az {GEN + 2}x{SAHNE_SATIR + 5} olmalı;')
        print('pencereyi büyüt (ya da yazı boyutunu küçült) ve Enter\'a bas.')
        try:
            input()
        except EOFError:
            raise SystemExit


def main():
    global MOD
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass
    MOD = renk_modu_sec()
    ekran = Ekran(MOD)
    boyut_kontrol(ekran)
    ekran.baslat()
    try:
        baslik_ekrani(ekran)
        while True:
            benim = kart_secimi(ekran)
            if benim is None:
                break
            rakip = rakip_cek(ekran)
            savas(benim, rakip, ekran)
            if not tekrar_mi(ekran):
                break
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        ekran.bitir()
    print('Görüşürüz! Gizemli Tüccar seni yine bekler...')


if __name__ == '__main__':
    main()
