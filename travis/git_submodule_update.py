# -*- coding: utf-8 -*-
# Download submodules from Github zip archive url
# Keep standard update form private repositories
# listed in `travis/private_repo`
#
import os
import shutil
from urllib import urlretrieve
import zipfile

from git import Repo

DL_DIR = 'download'
ZIP_PATH = '%s/submodule.zip' % DL_DIR

os.makedirs(DL_DIR)

with open('travis/private_repos') as f:
    private_repos = f.read()

os.system('git submodule init')

for sub in Repo('.').submodules:
    if sub.path not in private_repos:
        url = sub.url
        if url.startswith('git@github.com:'):
            url = url.replace('git@github.com:', 'https://github.com/')
        # remove .git
        if url.endswith('.git'):
            url = url[:-4]
        archive_url = "%s/archive/%s.zip" % (url, sub.hexsha)
        urlretrieve(archive_url, ZIP_PATH)
        with zipfile.ZipFile(ZIP_PATH) as zf:
            zf.extractall(DL_DIR)
        os.remove(ZIP_PATH)
        os.removedirs(sub.path)
        submodule_dir = os.listdir(DL_DIR)[0]
        shutil.move(os.path.join(DL_DIR ,submodule_dir), sub.path)
    else:
        os.system('git submodule update %s' % sub.path)
