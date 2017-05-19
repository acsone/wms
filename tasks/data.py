# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from distutils.version import StrictVersion
import csvdiff
import csv
import os

from invoke import task, exceptions

from .common import (
    MIGRATION_FILE,
    current_version,
    exit_msg,
)


@task(name="make-csv-diff")
def make_csv_diff(ctx, filename=None):
    """ This task compare 2 csv files and create multiple csv files
    to be loaded in the next version """

    if not (filename):
        exit_msg("You must provide a filename like: --filename product.csv")

    old_version = current_version()
    if not old_version:
        exit_msg("the version file is empty")
    try:
        version = StrictVersion(old_version)
    except ValueError:
        exit_msg("'{}' is not a valid version".format(version))

    version = (version.version[0],
               version.version[1] + 1,
               0)
    next_version = '.'.join([str(v) for v in version])

    target_dir = os.path.join('odoo', 'data', 'update', next_version)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    old_csv = os.path.join('odoo', 'data', 'install', filename + '.former')
    new_csv = os.path.join('odoo', 'data', 'install', filename)
    json = csvdiff.diff_files(old_csv, new_csv, ['id'])

    added = json['added']
    changed = json['changed']

    if not added and not changed:
        return

    load_method = ''
    with open(MIGRATION_FILE, 'r') as fd:
        for line in fd.read().split('\n'):
            if filename in line and '/opt/odoo/data/install' in line:
                load_method = line.split('::')[1].split()[0]
                break

    try:
        ctx.run(r'grep --quiet --regexp "- version:.*{}" {}'.format(
            next_version,
            MIGRATION_FILE
        ))
    except exceptions.Failure:
        with open(MIGRATION_FILE, 'a') as fd:
            fd.write('    - version: {}\n'.format(next_version))

    with open(MIGRATION_FILE, 'a') as fd:
        fd.write('      modes:\n')
        fd.write('        full:\n')
        fd.write('          operations:\n')
        fd.write('            post:\n')

    def create_csv_new(added):
        added_filename = filename[:-4] + '.new.csv'
        file_path = os.path.join(target_dir, added_filename)
        with open(file_path, 'wb') as csvfile:
            fieldnames = added[0].keys()
            # Put id as first column
            del fieldnames[fieldnames.index('id')]
            fieldnames.insert(0, 'id')
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(added)

        with open(MIGRATION_FILE, 'a') as fd:
            fd.write('              - bin/importer.sh songs.install.data_full::{} /opt/{}\n'.format(load_method, file_path))

    def create_csv_changes(changed):
        # get unique type of changes
        change_types = []
        for c in changed:
            fields_changed = c['fields'].keys()
            if fields_changed not in change_types:
                change_types.append(fields_changed)

        files_to_load = []
        for ct in change_types:
            changes_str = '-'.join([i.replace('/id', '') for i in ct])
            changed_filename = filename[:-4] + '.change-' + changes_str + '.csv'
            file_path = os.path.join(target_dir, changed_filename)
            files_to_load.append(file_path)
            change_batch = [c for c in changed if c['fields'].keys() == ct]
            with open(file_path, 'wb') as csvfile:
                fieldnames = ['id'] + ct
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                # For each line change get the id column and all new values
                for c in change_batch:
                    row = {'id': c['key'][0]}
                    row.update({k: v['to'] for (k, v) in c['fields'].iteritems()})
                    writer.writerow(row)

        with open(MIGRATION_FILE, 'a') as fd:
            for f in files_to_load:
                fd.write('              - bin/importer.sh songs.install.data_full::{} /opt/{}\n'.format(load_method,f))

    create_csv_new(added)
    create_csv_changes(changed)
