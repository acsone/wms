# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.tools import ormcache

from odoo.addons.account.models.account_payment_term import AccountPaymentTerm
from odoo.addons.account_payment_mode.models.account_payment_mode import (
    AccountPaymentMode,
)
from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.models.fastapi_endpoint import FastapiEndpoint
from odoo.addons.product.models.product_pricelist import Pricelist
from odoo.addons.product_assortment.models.ir_filters import IrFilters
from odoo.addons.sale_channel.models.sale_channel import SaleChannel
from odoo.addons.sales_team.models.crm_team import CrmTeam


class AlcB2cClient(models.Model):
    _name = "alc.b2c.client"
    _inherit = ["server.env.techname.mixin", "server.env.mixin"]  # nosemgrep
    _description = "Alc B2c Client"

    name = fields.Char(required=True)
    product_assortment_id = fields.Many2one[IrFilters](
        string="Product Assortment",
        help="Allows only products matching with the assortment domain",
        domain=[("is_assortment", "=", True)],
        context={"product_assortment": True},
    )
    sale_channel_id = fields.Many2one[SaleChannel](required=True)
    pricelist_id = fields.Many2one[Pricelist](string="Pricelist", required=True)
    sale_team_id = fields.Many2one[CrmTeam](string="Sale Team", required=True)
    payment_mode_id = fields.Many2one[AccountPaymentMode](
        string="Payment Mode", domain=[("payment_type", "=", "inbound")]
    )
    payment_term_id = fields.Many2one[AccountPaymentTerm](string="Payment Terms")
    sale_reason_backorder_strategy = fields.Selection(
        selection=[("create", "Create"), ("cancel", "Cancel")],
        default=lambda self: self._get_default_sale_reason_backorder_strategy(),
        required=True,
        help="Choose the strategy that will be applied on pickings that have "
        "backorder choice enabled and depending on partner sale strategy.",
    )
    picking_policy = fields.Selection(
        selection="_selection_picking_policy",
        string="Shipping Policy",
        required=True,
        default=lambda s: s._default_picking_policy(),
    )

    api_key = fields.Char(required=True)
    partner_id = fields.Many2one[Partner](required=True)
    allow_customer_modifications = fields.Boolean(
        default=False,
        help="If set to True, first name, last name and address can be modified for the customer without any check",
    )
    fastapi_endpoint_id = fields.Many2one[FastapiEndpoint](required=True)

    @property
    def _server_env_fields(self):
        return {"api_key": {}}

    @api.model
    def _selection_picking_policy(self):
        return self.env["sale.order"]._fields["picking_policy"].selection

    @api.model
    def _default_picking_policy(self):
        return self.env["sale.order"]._fields["picking_policy"].default("sale.order")

    @api.model
    def _get_default_sale_reason_backorder_strategy(self):
        return self.env.company.partner_sale_backorder_default_strategy

    @api.model
    @ormcache("endpoint_id", "api_key")
    def _get_id_by_endpoint_id_and_api_key(self, endpoint_id, api_key):
        res = self.search([("fastapi_endpoint_id", "=", endpoint_id)]).filtered(
            lambda r: r.api_key == api_key
        )
        if not res:
            raise SystemError(_("No b2c client found for this api key"))
        if len(res) > 1:
            raise SystemError(_("More than one b2c client found for this api key"))
        return res.id

    def write(self, vals):
        res = super().write(vals)
        self._get_id_by_endpoint_id_and_api_key.clear_cache(self)
        return res

    def unlink(self):
        res = super().unlink()
        self._get_id_by_endpoint_id_and_api_key.clear_cache(self)
        return res
