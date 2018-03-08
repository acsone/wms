# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import pickle

from pkg_resources import Requirement, resource_stream
from anthem.lyrics.loaders import load_csv_stream

req = Requirement.parse('alcyon-odoo')


def load_csv(ctx, path, model, delimiter=',',
             header=None, header_exclude=None):
    content = resource_stream(req, path)
    load_csv_stream(ctx, model, content, delimiter=delimiter,
                    header=header, header_exclude=header_exclude)


def load_users_csv(ctx, path, delimiter=','):
    # make sure we don't send any email
    model = ctx.env['res.users'].with_context({
        'no_reset_password': True,
        'tracking_disable': True,
    })
    load_csv(ctx, path, model, delimiter=delimiter)


def define_settings(ctx, model, values):
    """ Define settings like being in the interface
     Example :
      - model = 'sale.config.settings'
      - values = {'default_invoice_policy': 'delivery'}
    """
    ctx.env[model].create(values).execute()


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
