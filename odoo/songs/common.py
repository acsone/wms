# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import pickle

from pkg_resources import Requirement

req = Requirement.parse('alcyon-odoo')


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
