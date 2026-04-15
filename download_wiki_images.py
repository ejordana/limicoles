#!/usr/bin/env python3
# Descarrega les imatges de Wikipedia per a cada espècie i actualitza species.yml

import urllib.request
import urllib.parse
import json
import os
import re
import time

DATA_FILE  = '_data/species.yml'
IMAGES_DIR = 'assets/images/groups'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, */*',
    'Accept-Language': 'ca,es;q=0.9,en;q=0.8',
}

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))

def fetch_binary(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def wiki_image_url(nom_cientific):
    title = nom_cientific.replace(' ', '_')
    encoded = urllib.parse.quote(title)
    data = fetch_json(f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}')
    return (data.get('originalimage') or data.get('thumbnail') or {}).get('source')

def ext_from_url(url):
    path = urllib.parse.urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    return ext if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp') else '.jpg'

def slugify(text):
    return re.sub(r'[^a-z0-9\-]', '', text.lower().replace(' ', '-'))

# Llegir YAML manualment (sense llibreries externes)
def parse_yaml_simple(path):
    """Parser mínim per extreure grup id i espècies del species.yml."""
    grups = []
    grup  = None
    esp   = None

    with open(path, encoding='utf-8') as f:
        for line in f:
            # grup id
            m = re.match(r'  - id:\s+"?([^"]+)"?', line)
            if m:
                grup = {'id': m.group(1).strip(), 'especies': []}
                grups.append(grup)
                esp = None
                continue
            # espècie nom_cientific
            m = re.match(r'        nom_cientific:\s+"?([^"]+)"?', line)
            if m and grup:
                esp = {'nom_cientific': m.group(1).strip()}
                grup['especies'].append(esp)
                continue
            # espècie imatge
            m = re.match(r'        imatge:\s+"?([^"]+)"?', line)
            if m and esp:
                esp['imatge'] = m.group(1).strip()
                continue
            # espècie nom
            m = re.match(r'      - nom:\s+"?([^"]+)"?', line)
            if m and grup:
                esp = {'nom': m.group(1).strip()}
                grup['especies'].append(esp)
                continue
            # nom dins espècie (línia després de "- nom:")
            if esp and 'nom' not in esp:
                m = re.match(r'\s+nom:\s+"?([^"]+)"?', line)
                if m:
                    esp['nom'] = m.group(1)

    return grups

def update_imatge_in_yaml(path, nom_cientific, new_filename):
    """Substitueix el camp imatge de l'espècie al fitxer YAML."""
    with open(path, encoding='utf-8') as f:
        content = f.read()

    # Cerca el bloc de l'espècie pel nom científic i actualitza imatge
    escaped = re.escape(nom_cientific)
    pattern = rf'(nom_cientific:\s+"?{escaped}"?\n(?:.*\n)*?        imatge:\s+)"?[^\n"]*"?'
    replacement = rf'\g<1>"{new_filename}"'
    new_content, n = re.subn(pattern, replacement, content)

    if n:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# --- Principal ---
grups = parse_yaml_simple(DATA_FILE)

for grup in grups:
    grup_id = grup['id']
    dir_path = os.path.join(IMAGES_DIR, grup_id)
    os.makedirs(dir_path, exist_ok=True)

    for esp in grup['especies']:
        sci  = esp.get('nom_cientific')
        nom  = esp.get('nom', sci)
        if not sci:
            continue

        print(f'\n{nom} ({sci})')

        filename_check = slugify(sci)
        # Si ja existeix amb qualsevol extensió, saltar sense cridar Wikipedia
        existing = next((f for f in os.listdir(dir_path) if f.startswith(filename_check + '.')), None)
        if existing:
            print(f'  -> Ja existeix: {os.path.join(dir_path, existing)}')
            if esp.get('imatge') != existing:
                if update_imatge_in_yaml(DATA_FILE, sci, existing):
                    print(f'  -> species.yml actualitzat: {existing}')
            continue

        try:
            img_url = wiki_image_url(sci)
        except Exception as e:
            if '429' in str(e):
                print(f'  -> 429 Too Many Requests. Aturant.')
                exit(1)
            print(f'  -> Error Wikipedia: {e}')
            continue

        if not img_url:
            print('  -> Sense imatge a Wikipedia')
            continue

        ext      = ext_from_url(img_url)
        filename = f'{slugify(sci)}{ext}'
        dest     = os.path.join(dir_path, filename)

        if os.path.exists(dest):
            print(f'  -> Ja existeix: {dest}')
            continue
        print(f'  -> Descarregant: {img_url}')
        try:
            data = fetch_binary(img_url)
            with open(dest, 'wb') as f:
                f.write(data)
            print(f'  -> Guardat: {dest}')
        except Exception as e:
            if '429' in str(e):
                print(f'  -> 429 Too Many Requests. Aturant.')
                exit(1)
            print(f'  -> Error descarregant: {e}')
            continue

        if esp.get('imatge') != filename:
            if update_imatge_in_yaml(DATA_FILE, sci, filename):
                print(f'  -> species.yml actualitzat: {filename}')

        print('\nImatge descarregada. Torna a executar per continuar amb la següent.')
        exit(0)

print('\nTotes les imatges ja estan descarregades!')
