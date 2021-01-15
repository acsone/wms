# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models

from .utils import create_index, install_trgm_extension


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model_cr
    def init(self):
        trgm_installed = install_trgm_extension(self.env)

        if trgm_installed:
            for field in ("name", "email", "display_name", "ref"):
                index_name = "res_partner_%s_trgm_index" % field
                create_index(
                    self.env.cr,
                    index_name,
                    self._table,
                    "USING gin (%s gin_trgm_ops)" % field,
                )

        # this query is issued every time the list view of partners
        # is displayed
        index_name = "res_partner_customer_count_index"
        create_index(
            self.env.cr,
            index_name,
            self._table,
            "(active, customer, parent_id) "
            "WHERE active AND customer "
            "AND parent_id is null ",
        )

        # equivalent for the suppliers
        index_name = "res_partner_supplier_count_index"
        create_index(
            self.env.cr,
            index_name,
            self._table,
            "(active, customer, parent_id) "
            "WHERE active AND supplier "
            "AND parent_id is null ",
        )
