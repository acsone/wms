#!/usr/bin/python
# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import csv
import os
import pyodbc
import sys
from shutil import copyfile
from collections import defaultdict, OrderedDict

from convertion import MAPPER_CLASSES


def flatten_dict(nested_dict, prefix=None):
    """ Transform a dict with nested dict like:
    {"a": 1, "b": {'c': 3, 'd': {'e': 5}}, "f": [{"g": 6}, {"g": 7}]}

    to a list of flat dict like:
    [
        {'a': 1, 'b/c': 3, 'b/d/e': 5, "f/g": 6},
        {"f/g": 7}
    ]
    """
    rows = []

    result = OrderedDict()
    rows.append(result)

    for k, v in nested_dict.items():
        if prefix:
            new_key = "%s/%s" % (prefix, k)
        else:
            new_key = k
        if v and isinstance(v, dict):
            result.update(flatten_dict(v, new_key)[0])

        elif isinstance(v, list) and v and isinstance(v[0], dict):
            # One2many or many2many case
            if prefix:
                raise NotImplementedError(
                    "List of dict in sub dict is not implemented yet."
                )
            result.update(flatten_dict(v.pop(0), new_key)[0])
            for other in v:
                rows.append(flatten_dict(other, new_key)[0])

        else:
            result[new_key] = v

    return rows


class Importer:

    def __init__(self, cursor, full=False):
        self.odoo_entities = OrderedDict()
        self.foreign_refs = defaultdict(list)
        self.cursor = cursor
        self.full = full
        self.csv_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..', 'odoo', 'data',
            'install' if self.full else 'demo'
        )

    def add_entity(self, name, entity):
        try:
            self.odoo_entities[name].append(entity)
        except KeyError:
            self.odoo_entities[name] = [entity]

    def add_entities(self, name, entities):
        for entity in entities:
            self.add_entity(name, entity)

    def add_foreign_ref(self, name, ref):
        self.foreign_refs[name].append(ref)

    def get_foreign_refs(self, name):
        return self.foreign_refs[name]

    def write_csv_files(self):
        for name, entities in self.odoo_entities.items():
            rows = []
            for entity in entities:
                rows.extend(flatten_dict(entity))
            headers = rows[0].keys()

            file_path = os.path.join(self.csv_path, '%s.csv' % name)

            # backup the file before overwriting it to make diff csv files
            if os.path.isfile(file_path):
                copyfile(file_path, file_path + '.former')
            with open(file_path, 'wb') as csvfile:
                writer = csv.DictWriter(csvfile, headers, lineterminator='\n')
                writer.writeheader()
                writer.writerows(rows)

    def process(self):
        for class_ in MAPPER_CLASSES:
            mapper = class_(self)
            mapper.process()

        self.write_csv_files()


if __name__ == "__main__":

    cache = '--cache' in sys.argv
    full = '--full' in sys.argv

    if not cache:
        conn = pyodbc.connect('DSN=Alcyon')
        cursor = conn.cursor()
    else:
        cursor = None

    importer = Importer(cursor, full=full)
    importer.process()
