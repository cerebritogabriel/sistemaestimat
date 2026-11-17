#!/usr/bin/env python3
"""Build de la landing de la app ESTIMAT (repo sistemaestimat).

Fuente en src/:
  src/paginas.json   qué plantilla genera qué archivo en cada idioma
  src/<pagina>.html  plantillas (en español) con marcas {{t:<pagina>.kNNNN}} e {{img:<id>}}
  src/i18n.json      diccionario de textos: {"index.k0001": {"es": ..., "pt": ..., "en": ...}}
  src/img/           capturas; se incrustan como data:image/...;base64

Genera: index.html, pt.html, en.html, estimat-afecto-{es,pt,en}.html,
        estimat-sistemas.html, estimat-sistemas-pt.html, estimat-sistemas-en.html

Uso:  python3 build.py                        # escribe junto a build.py
      python3 build.py --out DIR              # escribe en DIR
      python3 build.py --check [DIR]          # prueba de equivalencia contra los HTML de DIR
      python3 build.py --artefacto --out DIR  # solo artefacto.html (landing ES) para el artefacto de Claude
"""
import base64, json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')
MIME = {'jpg': 'jpeg', 'png': 'png', 'webp': 'webp', 'gif': 'gif', 'svg': 'svg+xml'}


def leer(nombre):
    with open(os.path.join(SRC, nombre), encoding='utf-8') as f:
        return f.read()


def imagen(ident, cache={}):
    if ident not in cache:
        carpeta = os.path.join(SRC, 'img')
        archivo = [a for a in os.listdir(carpeta) if a.split('.')[0] == ident]
        if len(archivo) != 1:
            raise SystemExit('Falta la imagen ' + ident + ' en src/img/')
        ext = archivo[0].split('.')[-1]
        with open(os.path.join(carpeta, archivo[0]), 'rb') as f:
            cache[ident] = 'data:image/%s;base64,%s' % (MIME[ext], base64.b64encode(f.read()).decode())
    return cache[ident]


def render(plantilla, i18n, idioma, nombre):
    faltan = []

    def tx(m):
        k = m.group(1)
        if k not in i18n:
            faltan.append(k)
            return m.group(0)
        return i18n[k][idioma]

    s = re.sub(r'\{\{t:([\w.]+)\}\}', tx, plantilla)
    if faltan:
        raise SystemExit('Claves sin traducción en i18n.json: ' + ', '.join(sorted(set(faltan))))
    s = re.sub(r'\{\{img:(\w+)\}\}', lambda m: imagen(m.group(1)), s)
    if re.search(r'\{\{(t|img):', s):
        raise SystemExit('Quedaron marcas sin reemplazar en ' + nombre)
    return s


def construir():
    i18n = json.loads(leer('i18n.json'))
    out = {}
    for p in json.loads(leer('paginas.json')):
        plantilla = leer(p['plantilla'])
        for idioma, archivo in p['salidas'].items():
            out[archivo] = render(plantilla, i18n, idioma, archivo)
    return out


def comparar(dir_ref):
    import difflib
    corte = lambda s: re.sub(r'(>)(?=<)|(;)|(")', lambda m: m.group(0) + '\n', s).split('\n')
    ok = True
    for nombre, html in construir().items():
        ruta = os.path.join(dir_ref, nombre)
        if not os.path.exists(ruta):
            print('falta', nombre); ok = False; continue
        with open(ruta, encoding='utf-8', newline='') as f:
            ref = f.read()
        if ref == html:
            print('igual  ', nombre); continue
        ok = False
        d = [l for l in difflib.unified_diff(corte(ref), corte(html), 'actual', 'generado', n=0, lineterm='')
             if l[:1] in '+-' and l[:3] not in ('+++', '---')]
        print('DISTINTO', nombre, '-', len(d), 'fragmentos cambiados; primeros:')
        for l in d[:12]:
            print('   ', l[:140])
    return ok


def main():
    out = ROOT
    if '--check' in sys.argv:
        i = sys.argv.index('--check')
        sys.exit(0 if comparar(sys.argv[i + 1] if len(sys.argv) > i + 1 else ROOT) else 1)
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]
    os.makedirs(out, exist_ok=True)
    paginas = construir()
    if '--artefacto' in sys.argv:
        paginas = {'artefacto.html': paginas['index.html']}
    for nombre, html in paginas.items():
        with open(os.path.join(out, nombre), 'w', encoding='utf-8', newline='') as f:
            f.write(html)
        print('ok', nombre, len(html.encode('utf-8')), 'bytes')


if __name__ == '__main__':
    main()
