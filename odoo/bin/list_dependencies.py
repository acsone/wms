#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

BASE_DIR = os.getcwd()
LOCAL_SRC_DIR = os.path.join(BASE_DIR, 'odoo', 'local-src')

dependencies = set()
modules = os.listdir(LOCAL_SRC_DIR)
for mod in modules:
    # read __manifest__
    manifest_path = os.path.join(LOCAL_SRC_DIR, mod, '__manifest__.py')
    if not os.path.isfile(manifest_path):
        continue
    with open(manifest_path) as manifest:
        # TODO only read dict
        data = eval(manifest.read())
    dependencies.update(data['depends'])

# remove local-src from list of dependencies
dependencies = dependencies.difference(modules)
print(','.join(dependencies))
