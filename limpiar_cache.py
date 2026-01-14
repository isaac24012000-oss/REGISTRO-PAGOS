#!/usr/bin/env python3
"""
Script para limpiar caché de Streamlit
Ejecutar antes de hacer push a Streamlit Cloud
"""

import os
import shutil

cache_dirs = [
    '.streamlit/cache',
    '__pycache__',
    '.pytest_cache',
]

for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print(f"✓ Eliminado: {cache_dir}")

print("\n✓ Caché limpiado. Ya puedes hacer push a GitHub")
