#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ITS_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from graphs.models import KnowledgeGraph

g = KnowledgeGraph.objects.first()
if g:
    print(f'ID: {g.id}, Name: {g.name}')
    print(f'Content keys: {list(g.content.keys()) if g.content else "No content"}')
    if g.content:
        nodes = g.content.get('nodes', [])
        relationships = g.content.get('relationships', [])
        print(f'Nodes count: {len(nodes)}')
        print(f'Relationships count: {len(relationships)}')
        if nodes:
            print(f'First node: {nodes[0]}')
else:
    print('No knowledge graph found')
