#!/usr/bin/env python3
"""docs/ 폴더를 스캔해서 nav.json을 생성합니다."""
import os
import json

def scan_dir(path):
    items = []
    try:
        entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
    except FileNotFoundError:
        return items

    for entry in entries:
        if entry.name.startswith('.') or entry.name.startswith('_'):
            continue
        if entry.is_dir():
            children = scan_dir(entry.path)
            if children:
                items.append({
                    "type": "folder",
                    "name": entry.name,
                    "children": children
                })
        else:
            ext = os.path.splitext(entry.name.lower())[1]
            supported = {'.md', '.html', '.htm', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
            if ext in supported:
                rel_path = os.path.relpath(entry.path, '.').replace('\\', '/')
                display_name = os.path.splitext(entry.name)[0] if ext == '.md' else entry.name
                items.append({
                    "type": "file",
                    "name": display_name,
                    "path": rel_path
                })
    return items

nav = {"items": scan_dir('docs')}

with open('nav.json', 'w', encoding='utf-8') as f:
    json.dump(nav, f, ensure_ascii=False, indent=2)

print(f"nav.json generated: {len(nav['items'])} top-level items")
