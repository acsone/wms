# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import csv
import os
import pyodbc
import sys
from collections import defaultdict, OrderedDict

from convertion import MAPPER_CLASSES


def flatten_dict(nested_dict, prefix=None):
    """ Transform a dict with nested dict like:
    {"a": 1, "b": {'c': 3, 'd': {'e': 5}}}

    to a flat dict like:
    {'a': 1, 'b/c': 3, 'b/d/e': 5}
    """
    #TODO: Does not work with one2many with multiple lines...
    result = OrderedDict()
    for k, v in nested_dict.items():
        if prefix:
            new_key = "%s/%s" % (prefix, k)
        else:
            new_key = k
        if v and isinstance(v, dict):
            result.update(flatten_dict(v, new_key))
        else:
            result[new_key] = v

    return result


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
            entities = [flatten_dict(d) for d in entities]
            headers = entities[0].keys()

            file_path = os.path.join(self.csv_path, '%s.csv' % name)
            with open(file_path, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, headers)
                writer.writeheader()
                writer.writerows(entities)

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
