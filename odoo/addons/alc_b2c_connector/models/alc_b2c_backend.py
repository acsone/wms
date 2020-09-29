# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models, tools
from odoo.addons.server_environment import serv_config
from odoo.http import request


class AlcB2CBackend(models.Model):

    _name = "alc.b2c.backend"
    _description = "B2C Config"
    _inherit = "connector.backend"

    name = fields.Char(required=True, readonly=True)
    product_assortment_id = fields.Many2one(
        string="Product Assortment",
        comodel_name="ir.filters",
        help="Allows only products matching with the assortment domain",
        domain=[("is_assortment", "=", True)],
        context={"product_assortment": True},
    )
    sale_channel = fields.Selection(
        selection=lambda a: a.get_sale_channel_selection(), required=True
    )
    pricelist_id = fields.Many2one(
        "product.pricelist", string="Pricelist", required=True
    )
    sale_team_id = fields.Many2one("crm.team", string="Sale Team", required=True)
    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string="Payment Mode",
        domain=[("payment_type", "=", "inbound")],
    )
    payment_term_id = fields.Many2one("account.payment.term", string="Payment Terms")

    _sql_constraints = [("name_uniq", "UNIQUE(name)", _("Name must be unique"))]

    @api.model
    def get_sale_channel_selection(self):
        return self.env["sale.order"]._fields["sale_channel"].selection

    @classmethod
    def _get_api_key_section_name(cls, auth_api_key):
        for section in serv_config.sections():
            if section.startswith("api_key_") and serv_config.has_option(
                section, "key"
            ):
                if tools.consteq(auth_api_key, serv_config.get(section, "key")):
                    return section
        return None

    @api.model
    @tools.ormcache("self._uid", "auth_api_key")
    def _get_id_from_auth_api_key(self, auth_api_key):
        auth_api_key_section_name = self._get_api_key_section_name(auth_api_key)
        if auth_api_key_section_name:
            # filtered, not search because auth_api_key_name is
            # not a searchable field
            return (
                self.suspend_security()
                .search(
                    [
                        (
                            "name",
                            "=",
                            serv_config.get(auth_api_key_section_name, "backend_name"),
                        )
                    ]
                )
                .id
            )
        return False

    @api.model
    def _get_from_http_request(self):
        auth_api_key = getattr(request, "auth_api_key", None)
        return self.browse(self._get_id_from_auth_api_key(auth_api_key))
