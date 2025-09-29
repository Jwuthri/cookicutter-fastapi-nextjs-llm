#!/usr/bin/env python3
"""
Post-generation hook for cookiecutter template.
Renames .json.j2 files back to .json after templating.
"""

import os
import shutil

def rename_json_templates():
    """Rename .json.j2 files back to .json"""
    json_templates = [
        'frontend/package.json.j2',
        'backend/docker/pgadmin_servers.json.j2'
    ]
    
    for template_file in json_templates:
        if os.path.exists(template_file):
            json_file = template_file.replace('.json.j2', '.json')
            shutil.move(template_file, json_file)
            print(f"Renamed {template_file} -> {json_file}")

if __name__ == '__main__':
    rename_json_templates()
