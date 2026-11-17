# Fuente de la landing de la app ESTIMAT

- `paginas.json`: qué plantilla genera qué archivo en cada idioma (es, pt, en).
- `index.html`, `afecto.html`, `sistemas.html`: plantillas en español con marcas `{{t:…}}` e `{{img:…}}`.
- `i18n.json`: diccionario ES/PT/EN de esas marcas.
- `img/`: capturas que el build incrusta en base64.

Construir: `python3 build.py`. Comparar con lo publicado: `python3 build.py --check`.
Versión para el artefacto (landing ES): `python3 build.py --artefacto --out DIR`.
