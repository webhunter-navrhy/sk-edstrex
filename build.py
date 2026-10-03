"""Zostaví index.html + style.css s cache bustingom (?v=hash). Obsah je z edstrex.sk (podklady/stranky)."""
import hashlib, json
from pathlib import Path
D = Path(__file__).parent

# na čo všetko – zo stránky O nás
UCELY = ['Obchody', 'Kiosky', 'Bufety', 'Terasy', 'Showroomy', 'Garáže', 'Kancelárie', 'Reštaurácie', 'Škôlky', 'Školy',
         'Predajné stánky', 'Kontajnerové domy', 'Kaviarne', 'Byty', 'Altánky', 'Zastávky', 'Shop-moduly', 'Unimobunky',
         'Sanitárne moduly', 'Chatky', 'Apartmány', 'Zmenárne']
VYHODY = ['Slovenská certifikovaná výroba', 'Jednoduché konštrukčné riešenie', 'Moderný, estetický vzhľad', 'Rýchla realizácia',
          'Ľahká manipulácia s objektmi', 'Zabezpečujeme prevoz a montáž', 'Vysoké tepelnoizolačné vlastnosti', 'Celoročné využitie',
          'Bezproblémový presun modulov na iné miesto', 'Bezproblémové rozšírenie priestorov', 'Možnosť akéhokoľvek dodatočného vybavenia']

# ako pracujeme – časová os z ich webu (názov, dni, popis)
KROKY = [
    ('Žiadosť o cenovú ponuku', 1, 'Napíšete nám, čo potrebujete: účel stavby, približný rozmer a miesto.'),
    ('Komunikácia so zákazníkom', 1, 'Spolu doladíme dispozíciu, fasádu, okná, interiér aj vybavenie.'),
    ('Vypracovanie projektu', 1, 'Pripravíme projekt a 3D vizualizáciu, aby ste stavbu videli ešte pred výrobou.'),
    ('Uzatvorenie zmluvy', 1, 'Podpíšeme zmluvu a stavba ide do výroby.'),
    ('Zhotovenie modulovej stavby', 39, 'Oceľová konštrukcia, steny, strecha aj interiér vznikajú v našom výrobnom areáli v Michalovciach.'),
    ('Preprava', 1, 'Hotové moduly dovezieme špecializovaným kamiónom.'),
    ('Montáž, odovzdanie stavby', 1, 'Moduly osadíme na pripravené základy a stavbu Vám odovzdáme.'),
]
ZABERY_ALT = ['Kancelária EDSTREX', 'Kancelária EDSTREX – interiér', 'Vizualizácia modulovej stavby', 'Nová kancelária EDSTREX',
              'Výrobná hala EDSTREX', 'Preprava modulovej stavby', 'Osadzovanie modulu žeriavom', 'Hotový modulový dom']

FILTRE = [('vse', 'Všetko'), ('gastro', 'Gastro'), ('kancelarie', 'Kancelárie'), ('obchody', 'Obchody a služby'),
          ('byvanie', 'Bývanie'), ('houseboat', 'Houseboaty'), ('haly', 'Haly')]

# cenník – zo stránky Cenník (názov, rozmer v m (d, š) alebo plocha, cena, „od“)
CENNIK = [
    ('Základná modulová stavba', (6, 3), '5 400', False, ''),
    ('Základná modulová stavba', (6, 6), '10 300', False, ''),
    ('Modulová terasa so strechou', (6, 3), '3 700', True, ''),
    ('Modulový gastro stánok', (5, 3), '6 300', True, 's fasádnym prevedením'),
    ('Modulová terasa – záhradná kuchyňa', (6, 3), '6 700', True, ''),
    ('Záhradný domček – kancelária', (6, 3), '7 200', True, 's fasádnym prevedením'),
    ('Modulový apartmán', (12, 3.5), '19 900', True, 's fasádnym prevedením'),
    ('Modulový dom', 90, '38 000', True, 'vybavenie podľa požiadaviek'),
    ('Apartmán', (11.5, 6), '45 000', True, ''),
]
KRAJINY = ['Belgicko', 'Bulharsko', 'Chorvátsko', 'Česko', 'Dánsko', 'Estónsko', 'Fínsko', 'Francúzsko', 'Grécko', 'Holandsko',
           'Írsko', 'Litva', 'Lotyšsko', 'Luxembursko', 'Maďarsko', 'Nemecko', 'Poľsko', 'Portugalsko', 'Rakúsko', 'Rumunsko',
           'Slovensko', 'Slovinsko', 'Španielsko', 'Švajčiarsko', 'Švédsko', 'Taliansko', 'Veľká Británia']
TYPY = ['Kancelária', 'Gastro prevádzka', 'Predajňa / showroom', 'Rodinný dom', 'Apartmán', 'Záhradný domček', 'Terasa', 'Houseboat', 'Iné']

# zloženie modulovej stavby – zo stránky Zloženie modulových stavieb
VRSTVY = [
    ('strecha', 'Strecha', ['sendvičový panel so strešným profilom T-35 s PIR jadrom hrúbky 100 mm',
        'koeficient prestupu tepla (Uc): PIR 100 mm 0,22 · PIR 120 mm 0,16 · PIR 160 mm 0,14 W/(m²·K)',
        'prekrytie strešnou fóliou Fatrafol', 'vnútorná hrúbka oceľového plechu 0,50 – 0,55 mm', 'farebné prevedenie RAL 9006 / 9010']),
    ('steny', 'Vonkajšie steny', ['sendvičový panel PIR s hrúbkou 100 / 120 / 160 mm', 'koeficient prestupu tepla (Uc) 0,22 W/(m²·K)',
        'profily hladké alebo profilované', 'RAL 7016 (antracitová) alebo RAL 9006 (strieborná)']),
    ('priecky', 'Vnútorné steny', ['sendvičový panel PIR s hrúbkou 60 mm alebo vnútorný sadrokartón', 'farebné prevedenie RAL 9010']),
    ('kostra', 'Konštrukcia', ['oceľový skelet z uzavretých profilov + dodatočný rám pre okná a dvere',
        'oceľové prvky sú pred lakovaním prúdovo vyčistené, odmastené, penetrované epoxidovou farbou a lakované polyuretánovou farbou v odtieni RAL podľa výberu',
        'podlahové nosníky z oceľových profilov, zvárané každých 50 – 100 cm']),
    ('podlaha', 'Podlaha', ['tepelná izolácia na oceľovom rošte', 'MFP doska s hrúbkou 15 mm',
        'PVC linoleum podľa výberu, plávajúca podlaha, koberec alebo protišmyková hliníková podlaha']),
]


# ---------- izometrický modul (SVG) ----------
S, C = 34, 0.866
L, W, H = 6.0, 3.0, 2.9
E = 62  # rozostup vrstiev pri rozložení (px)
OX, OY = W * C * S + 14, 0  # posun, aby x≥0


def P(x, y, z):
    return (round(OX + (x - y) * C * S, 1), round((x + y) * 0.5 * S - z * S, 1))


def poly(pts, cls):
    return f'<polygon class="{cls}" points="{" ".join(f"{a},{b}" for a, b in pts)}"/>'


def box(x0, y0, z0, x1, y1, z1, pre=''):
    top = [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]
    rx = [P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)]  # stena x = x1
    fy = [P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)]  # stena y = y1
    return pre + poly(fy, 'fl') + poly(rx, 'fr') + poly(top, 'ft')


def line(a, b, cls='st'):
    return f'<line class="{cls}" x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>'


def quad_y(y, x0, x1, z0, z1, cls):
    return poly([P(x0, y, z0), P(x1, y, z0), P(x1, y, z1), P(x0, y, z1)], cls)


def quad_x(x, y0, y1, z0, z1, cls):
    return poly([P(x, y0, z0), P(x, y1, z0), P(x, y1, z1), P(x, y0, z1)], cls)


Z0, Z1 = 0.25, H - 0.2
vrstvy_svg = {}
vrstvy_svg['podlaha'] = box(0, 0, 0, L, W, Z0)
k = []
for (a, b) in [((0, 0), (L, 0)), ((0, 0), (0, W)), ((L, 0), (L, W)), ((0, W), (L, W))]:
    for z in (Z0, Z1):
        k.append(line(P(a[0], a[1], z), P(b[0], b[1], z)))
for x in (0, 2, 4, L):
    for y in (0, W):
        k.append(line(P(x, y, Z0), P(x, y, Z1)))
for x in (1, 2, 3, 4, 5):
    k.append(line(P(x, 0, Z0), P(x, W, Z0), 'st st--thin'))
vrstvy_svg['kostra'] = ''.join(k)
vrstvy_svg['priecky'] = quad_x(2.4, 0, W, Z0, Z1, 'fr') + quad_x(2.4, 1.6, 2.5, Z0, 2.25, 'hole') + quad_y(1.5, 2.4, L, Z0, Z1, 'fl op')
st = [quad_y(0, 0, L, Z0, Z1, 'fb'), quad_x(0, 0, W, Z0, Z1, 'fb'),
      quad_y(W, 0, L, Z0, Z1, 'fl'), quad_x(L, 0, W, Z0, Z1, 'fr'),
      quad_y(W, 0.5, 2.1, 0.75, 2.35, 'gl'), quad_y(W, 2.5, 5.5, 0.4, 2.35, 'gl'), quad_x(L, 0.9, 1.9, Z0, 2.3, 'gl')]
for x in (3.5, 4.5):
    st.append(line(P(x, W, 0.4), P(x, W, 2.35), 'mul'))
vrstvy_svg['steny'] = ''.join(st)
vrstvy_svg['strecha'] = box(-0.08, -0.08, Z1, L + 0.08, W + 0.08, H + 0.06)

poradie = ['podlaha', 'kostra', 'priecky', 'steny', 'strecha']
top_y = P(0, 0, H + 0.06)[1]
bot_y = P(L, W, 0)[1]
vb_h = bot_y - top_y + E * 4 + 30
oy = -top_y + E * 4 + 15
vb_w = round((L + W) * C * S + 28 + 170)
nazvy = {v[0]: v[1] for v in VRSTVY}
g = []
for i, key in enumerate(poradie):
    lbl_y = P(L, W / 2, (Z0 if key == 'podlaha' else H if key == 'strecha' else 1.5))[1]
    lx = P(L, 0, 0)[0] + 18
    g.append(f'<g class="ly" data-l="{key}" style="--e:{i}"><g transform="translate(0 {round(oy,1)})">{vrstvy_svg[key]}'
             f'<g class="tag"><line x1="{lx - 10}" y1="{lbl_y}" x2="{lx + 16}" y2="{lbl_y}"/><text x="{lx + 22}" y="{lbl_y + 4}">{nazvy[key]}</text></g></g></g>')
anatomia = (f'<svg viewBox="0 0 {vb_w} {round(vb_h)}" role="img" aria-label="Rozložený modul: podlaha, konštrukcia, vnútorné steny, vonkajšie steny, strecha">'
            + ''.join(g) + '</svg>')

tabs = ''.join(f'<button role="tab" data-l="{k}" aria-selected="{"true" if i == 0 else "false"}"><span>{i + 1:02d}</span>{n}</button>'
               for i, (k, n, _) in enumerate(VRSTVY))
spec = ''.join(f'<ul class="spec{" is-on" if i == 0 else ""}" data-l="{k}">' + ''.join(f'<li>{x}</li>' for x in li) + '</ul>'
               for i, (k, n, li) in enumerate(VRSTVY))

# ---------- ostatné bloky ----------
X = '<svg class="xm" viewBox="0 0 20 20" aria-hidden="true"><path d="M0 0h7l7 10-7 10H0l7-10z" fill="#e31e25"/><path d="M13 0h7l-5 7.2-3.5-5z" fill="currentColor"/></svg>'
marquee = ''.join(f'<span>{u}</span>{X}' for u in UCELY) * 2
vyhody = ''.join(f'<li class="rv"><span class="ck" aria-hidden="true"></span>{v}</li>' for v in VYHODY)

kum, kroky, track = 0, [], []
for i, (n, d, p) in enumerate(KROKY, 1):
    od = kum + 1; kum += d
    kroky.append(f'<li class="krok" data-k="{i}" data-od="{od}" data-do="{kum}"><span class="krok__d">{d} {"deň" if d == 1 else "dní"}</span><h3>{n}</h3><p>{p}</p></li>')
    track.append(f'<div class="seg{" seg--long" if d > 1 else ""}" data-k="{i}"><i></i><span>{d} {"deň" if d == 1 else "dní"}</span></div>')
track.append('<div class="seg seg--sum" data-k="8"><i></i><span>Spolu 45 dní</span></div>')
kroky.append('<li class="krok" data-k="8" data-od="45" data-do="45"><span class="krok__d">Spolu</span><h3>Hotovo</h3><p>Stavba stojí a môžete ju začať používať.</p></li>')
zabery = ''.join(f'<img src="img/t{i}.jpg" alt="{a}" data-k="{i}" loading="lazy"{" class=\"is-on\"" if i == 1 else ""}>' for i, a in enumerate(ZABERY_ALT, 1))

filtre = ''.join(f'<button data-f="{k}" aria-pressed="{"true" if k == "vse" else "false"}">{n}</button>' for k, n in FILTRE)
gal = json.load(open(D / 'galeria.json'))
galeria = '\n'.join(
    f'<figure class="gi rv{" gi--tall" if x["wh"][1] > x["wh"][0] else ""}" data-k="{x["kat"]}" data-full="img/g-{x["n"]}.jpg">'
    f'<img src="img/t-{x["n"]}.jpg" alt="{x["nazov"]}{" – " + x["miesto"] if x["miesto"] else ""}" loading="lazy" width="{x["wh"][0]}" height="{x["wh"][1]}">'
    f'<figcaption><b>{x["nazov"]}</b>{"<span>" + x["miesto"] + "</span>" if x["miesto"] else ""}</figcaption></figure>'
    for x in gal)


def plan(r):
    # pôdorys v jednotnej mierke (12 m = 100 %)
    if isinstance(r, tuple):
        d, s = r; txt = f'{str(d).replace(".", ",")} × {str(s).replace(".", ",")} m'
    else:
        # plocha bez rozmerov – ilustračný obdĺžnik 12 m × plocha/12, prerušovaný
        d, s = 12, r / 12; txt = f'rozloha {r} m²'
    cls = '' if isinstance(r, tuple) else ' class="area"'
    return f'<div class="plan"><i{cls} style="--d:{d / 12:.3f};--s:{s / 12:.3f}"></i></div><p class="cena__r">{txt}</p>'


cennik = '\n'.join(
    f'<article class="cena rv">{plan(r)}<h3>{n}</h3>{f"<p class=cena__p>{pozn}</p>" if pozn else ""}'
    f'<p class="cena__c">{"<small>od</small> " if od else ""}{c} €</p><p class="cena__b">bez DPH</p></article>'
    for n, r, c, od, pozn in CENNIK)
krajiny = ''.join(f'<li{" class=sk" if k == "Slovensko" else ""}>{k}</li>' for k in KRAJINY)
typy = ''.join(f'<label class="chip"><input type="radio" name="typ" value="{t}"><span>{t}</span></label>' for t in TYPY)

css = (D / 'fonts/fonts.css').read_text() + '\n' + (D / 'style.src.css').read_text()
(D / 'style.css').write_text(css)
h = lambda b: hashlib.md5(b).hexdigest()[:8]
html = (D / 'src.html').read_text()
for k_, v in dict(marquee=marquee, vyhody=vyhody, kroky=''.join(kroky), track=''.join(track), zabery=zabery, filtre=filtre,
                  galeria=galeria, anatomia=anatomia, tabs=tabs, spec=spec, cennik=cennik, krajiny=krajiny,
                  pocet_krajin=str(len(KRAJINY)), typy=typy).items():
    html = html.replace('{{' + k_ + '}}', v)
html = html.replace('{{css}}', h(css.encode())).replace('{{js}}', h((D / 'main.js').read_bytes()))
assert '{{' not in html
(D / 'index.html').write_text(html)
(D / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
print('ok', len(gal), 'realizácií,', len(KRAJINY), 'krajín')
