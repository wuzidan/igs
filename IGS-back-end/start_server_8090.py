#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ITS_project.settings')
sys.path.insert(0, r'D:\IGS\IGS-back-end')

try:
    import django
    django.setup()
    print('Django setup successful')
    
    from django.core.management import call_command
    call_command('runserver', '0.0.0.0:8090', verbosity=2)
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
    input('Press Enter to exit...')
