# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Contact(models.AbstractModel):
    _inherit = "ir.qweb.field.contact"

    @api.model
    def value_to_html(self, value, options):
        res = super(Contact, self).value_to_html(
            value.with_context(to_html=True), options
        )
        return res
