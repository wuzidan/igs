#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ITS_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8080'])
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
