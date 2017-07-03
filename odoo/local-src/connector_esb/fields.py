# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields


class AutoSetupMany2one(fields.Many2one):
    """Auto set comodel_name."""

    def _setup_attrs(self, model, name):
        super(AutoSetupMany2one, self)._setup_attrs(model, name)
        if model._abstract:
            return
        comodel_name = model._name
        # If your m2o field is used for `_inherits`
        # you want to use inherits' model as m2o relation
        # instead of the model itself.
        # Eg:
        #  class ESBProductBinding(models.Model):
        #     _name = 'esb.sale.order.binding'
        #     _inherit = 'esb.binding'
        #     _inherits = {'sale.order': 'odoo_id'}
        inherits_inv = {v: k for k, v in model._inherits.iteritems()}
        if model._inherits and self.name in inherits_inv:
            comodel_name = inherits_inv[self.name]
        self.comodel_name = comodel_name
