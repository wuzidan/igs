#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

url = 'http://localhost:8000/api/graphs/4/'
headers = {
    'Content-Type': 'application/json',
}

try:
    response = requests.get(url, headers=headers)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Keys: {list(data.keys())}')
        print(f'Nodes count: {len(data.get("nodes", []))}')
        print(f'Relationships count: {len(data.get("relationships", []))}')
        if data.get('nodes'):
            print(f'First node: {data["nodes"][0]}')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Error: {e}')
