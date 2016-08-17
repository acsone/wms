# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import csv
import pickle

from anthem.output import safe_print


# TODO: move in anthem

def load_csv(ctx, model_name, path, dialect='excel', **fmtparams):
    """ Load a CSV from a filename

    Usage example::

      from pkg_resources import Requirement, resource_string

      req = Requirement.parse('my-project')
      load_csv(ctx, 'res.users',
               resource_string(req, 'data/users.csv'),
               delimiter=',')

    """
    with open(path, 'rb') as data:
        load_csv_stream(ctx, model_name, data, dialect=dialect, **fmtparams)


def load_csv_stream(ctx, model_name, data, dialect='excel', **fmtparams):
    """ Load a CSV from a stream

    Usage example::

      from pkg_resources import Requirement, resource_stream

      req = Requirement.parse('my-project')
      load_csv_stream(ctx, 'res.users',
                      resource_stream(req, 'data/users.csv'),
                      delimiter=',')

    """
    data = csv.reader(data, dialect=dialect, **fmtparams)
    head = data.next()
    values = list(data)
    if values:
        result = ctx.env[model_name].load(head, values)
        ids = result['ids']
        if not ids:
            messages = u'\n'.join(
                u'- %s' % msg for msg in result['messages']
            )
            safe_print(u"Failed to load CSV "
                       u"in '%s'. Details:\n%s" %
                       (model_name, messages))
            raise Exception('Load failure, see the logs')
        else:
            safe_print(u"Imported %d records in '%s'" %
                       (len(ids), model_name))


def create_default_value(ctx, model, field, value, company_id):
    ctx.env.cr.execute("""
    INSERT INTO ir_values
        (name, model, value, key, key2, company_id, user_id)
    SELECT %(field)s, %(model)s, %(pickled)s, 'default', NULL,
           %(company_id)s, NULL
    WHERE NOT EXISTS (
      SELECT id FROM ir_values
      WHERE name = %(field)s
            AND model = %(model)s
            AND company_id = %(company_id)s
            AND user_id is NULL
            AND key = 'default' and key2 is NULL
    )
    """, {'field': field,
          'model': model,
          'company_id': company_id,
          'pickled': pickle.dumps(value),
          })
