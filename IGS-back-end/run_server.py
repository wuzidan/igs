#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ITS_project.settings')
sys.path.insert(0, r'D:\IGS\IGS-back-end')

import django
django.setup()
print('Django setup successful')

from django.core.management import call_command
call_command('runserver', '0.0.0.0:8080', verbosity=2)
