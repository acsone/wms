# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import csv
import os
from collections import OrderedDict


class FieldMapper:
    def __init__(self, odoo_name, db2_name=None, strip=True,
                 constant=None, mapping=None, default=None, check=None):
        self.odoo_name = odoo_name
        self.db2_name = db2_name
        self.strip = strip
        self.constant = constant
        self.mapping = mapping
        self.default = default
        self.check = check


class EntityMapper:

    DB2_NAME = None
    DB2_SCHEMA = 'sbdata'

    DB2_REF_NAME = None

    XMLID_IMPORT_NAME = '__import__'
    XMLID_FIELD = None

    FIELDS_MAPPING = []

    def __init__(self, importer):
        assert self.DB2_NAME
        assert self.XMLID_FIELD

        self.name = self.__class__.__name__.lower().replace('mapper', '')
        self.importer = importer

        self.file_cache_path = os.path.join(
            '/var/tmp', 'db2_caches', '%s.csv' % self.DB2_NAME
        )

    @property
    def cursor(self):
        return self.importer.cursor

    def get_xml_id(self, entity_name, code, prefix=None):
        assert entity_name and code

        if prefix is None:
            prefix = self.XMLID_IMPORT_NAME

        return "%s.%s_%s" % (
            prefix, entity_name, code
        )

    @staticmethod
    def convert_coding(value):
        if isinstance(value, str):
            value = value.decode('latin1').encode('utf8')
        return value

    def fetchall_dict(self, query, params=tuple()):
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        if rows:
            rows = [
                {c.lower(): self.convert_coding(row[idx])
                 for idx, c in enumerate(
                    [d[0] for d in row.cursor_description]
                )}
                for row in rows
            ]
        return rows

    def convert_entities(self, db2_entities):
        odoo_entities = []
        for db2_entity in db2_entities:
            odoo_entity = OrderedDict(id=None)
            for field in self.FIELDS_MAPPING:
                if isinstance(field, str):
                    field = FieldMapper(field)

                if field.db2_name:
                    value = db2_entity[field.db2_name]

                    if value and field.strip and isinstance(value, str):
                        value = value.strip()

                    if field.mapping:
                        value = field.mapping.get(value)

                    elif field.check and not field.check(value):
                        value = None

                    if value is None and field.default:
                        value = field.default

                    odoo_entity[field.odoo_name] = value

                elif field.constant is not None:
                    odoo_entity[field.odoo_name] = field.constant

                else:
                    try:
                        convert_method = getattr(
                            self, 'convert_%s' % field.odoo_name
                        )
                    except AttributeError:
                        raise ValueError(
                            "Le champ '%s' n'a ni nom DB2 "
                            "ni méthode de conversion définie."
                            % field.odoo_name
                        )
                    convert_method(odoo_entity, db2_entity)

            odoo_entity['id'] = self.get_xml_id(
                self.name, odoo_entity[self.XMLID_FIELD]
            )
            odoo_entities.append(odoo_entity)

        return odoo_entities

    def get_sql_joins(self):
        return None

    def get_sql_where(self):
        return None

    def get_sql_query(self):
        needed_refs = self.importer.get_foreign_refs(self.DB2_NAME)

        query = "SELECT * FROM %s.%s "
        placeholders = (self.DB2_SCHEMA, self.DB2_NAME)
        params = []

        joins = self.get_sql_joins()
        if joins:
            query += joins

        if not self.importer.full and needed_refs:
            assert self.DB2_REF_NAME, \
                "DB2_REF_NAME is needed for fetching specific references!"

            query += "WHERE %s IN (%s)"

            placeholders += (
                self.DB2_REF_NAME,
                ', '.join('?' for idx in range(len(needed_refs)))
            )
            params += tuple(needed_refs)

        else:
            where_cond = self.get_sql_where()
            if not where_cond:
                where_cond = '1=1'

            query += "WHERE %s ORDER BY 1 asc "
            placeholders += (where_cond,)

            if not self.importer.full:
                query += "FETCH FIRST 300 ROWS ONLY"

        return query % placeholders, params

    def get_db2_entities(self):

        entities = self.fetchall_dict(*self.get_sql_query())

        caches_path = os.path.dirname(self.file_cache_path)
        if not os.path.exists(caches_path):
            os.makedirs(caches_path)

        with open(self.file_cache_path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, entities[0].keys())
            writer.writeheader()
            writer.writerows(entities)

        return entities

    def get_db2_entities_from_cache(self):
        if not os.path.exists(self.file_cache_path):
            raise ValueError(
                "Impossible de trouver le fichier de cache %s"
                % self.file_cache_path
            )

        with open(self.file_cache_path) as csv_file:
            return list(csv.DictReader(csv_file))

    def process(self):
        if self.cursor:
            db2_entities = self.get_db2_entities()
        else:
            db2_entities = self.get_db2_entities_from_cache()

        self.importer.add_entities(
            self.name, self.convert_entities(db2_entities)
        )
