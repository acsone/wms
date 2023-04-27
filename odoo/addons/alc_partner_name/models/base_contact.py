# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api

from odoo.addons.base.models.ir_qweb_fields import Contact as BaseContact


class Contact(BaseContact):
    @api.model
    def value_to_html(self, value, options):
        res = super().value_to_html(value.with_context(to_html=True), options)
        return res
