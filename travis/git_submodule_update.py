# -*- coding: utf-8 -*-
# Download submodules from Github zip archive url
# Keep standard update form private repositories
# listed in `travis/private_repo`
#
import os

from git import Repo

dl_dir = 'download'
os.system('mkdir %s' % dl_dir)

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
        wget_archive_url = "wget %s/archive/%s.zip" % (url, sub.hexsha)
        os.system(wget_archive_url)
        os.system('unzip -q %s -d %s' % (sub.hexsha, dl_dir))
        os.system('rm %s.zip' % sub.hexsha)
        os.system('rmdir %s' % sub.path)
        os.system('mv %s/* %s' % (dl_dir, sub.path))
    else:
        os.system('git submodule update %s' % sub.path)
