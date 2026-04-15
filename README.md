# Limícoles de Catalunya — Guia d'Identificació

Lloc web amb guia d'identificació de limícoles: taula general, fitxes per grup i il·lustracions.

## Com desplegar a GitHub Pages

### 1. Crea el repositori
```bash
gh repo create limicoles --public
# o bé crea'l manualment a github.com
```

### 2. Configura `_config.yml`
Edita les dues primeres línies:
```yaml
baseurl: "/limicoles"   # nom del teu repositori
url: "https://EL-TEU-USUARI.github.io"
```

### 3. Puja el projecte
```bash
cd limicoles-jekyll
git init
git add .
git commit -m "Primer commit: guia de limícoles"
git remote add origin https://github.com/EL-TEU-USUARI/limicoles.git
git push -u origin main
```

### 4. Activa GitHub Pages
A GitHub: **Settings → Pages → Source → Deploy from branch → main / root**

El lloc estarà disponible a:
`https://EL-TEU-USUARI.github.io/limicoles`

---

## Desenvolupament local (opcional)

```bash
bundle install
bundle exec jekyll serve
# Obre http://localhost:4000/limicoles
```

---

## Estructura del projecte

```
├── _config.yml          # Configuració Jekyll
├── _data/
│   └── species.yml      # Totes les dades d'espècies i grups
├── _groups/             # Una pàgina per grup (fitxer .md)
├── _layouts/
│   ├── default.html     # Layout principal
│   └── group.html       # Layout de pàgina de grup
├── assets/
│   ├── css/main.css
│   └── images/groups/   # Il·lustracions extretes dels PDFs
└── index.html           # Pàgina principal amb taula general
```

## Com afegir o editar espècies

Tota la informació és a `_data/species.yml`. Pots editar-lo directament:
- Afegir una espècie nova dins la llista `especies` del seu grup
- Modificar característiques existents
- Afegir noves il·lustracions a `assets/images/groups/` i referenciar-les

## Nota sobre il·lustracions

Les il·lustracions provenen d'una guia d'ocells publicada. Per a ús estrictament educatiu o privat.
