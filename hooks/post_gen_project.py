#!/usr/bin/env python3
"""
Post-generation hook for cookiecutter template.
Renames .json.j2 files back to .json after templating.
"""

import os
import shutil

def rename_template_files():
    """Rename .j2 template files back to their original extensions"""
    template_files = [
        # JSON templates
        'frontend/package.json.j2',
        'backend/docker/pgadmin_servers.json.j2',
        # TypeScript templates
        'frontend/src/lib/api.ts.j2',
        'frontend/src/app/layout.tsx.j2',
        'frontend/src/app/page.tsx.j2',
        'frontend/src/components/chat/chat-container.tsx.j2',
        'frontend/src/components/chat/chat-header.tsx.j2',
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            # Remove .j2 extension to get original filename
            original_file = template_file.replace('.j2', '')
            shutil.move(template_file, original_file)
            print(f"Renamed {template_file} -> {original_file}")

if __name__ == '__main__':
    rename_template_files()
