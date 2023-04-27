# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import Depends

from odoo import _, api, fields, models
from odoo.api import Environment

from odoo.addons.account.models.account_payment_term import AccountPaymentTerm
from odoo.addons.account_payment_mode.models.account_payment_mode import (
    AccountPaymentMode,
)
from odoo.addons.auth_api_key.models.auth_api_key import AuthApiKey
from odoo.addons.fastapi.depends import fastapi_endpoint, odoo_env
from odoo.addons.fastapi.models.fastapi_endpoint import FastapiEndpoint
from odoo.addons.product.models.product_pricelist import Pricelist
from odoo.addons.product_assortment.models.ir_filters import IrFilters
from odoo.addons.sale_channel.models.sale_channel import SaleChannel
from odoo.addons.sales_team.models.crm_team import CrmTeam

from ..services.utils import api_key_header


class FastapiEndpointSettings(models.Model):

    _name = "fastapi.endpoint.settings"
    _description = "Fastapi Endpoint Settings"

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

    auth_api_key_id = fields.Many2one[AuthApiKey](required=True)
    allow_customer_modifications = fields.Boolean(
        default=False,
        help="If set to True, first name, last name and address can be modified for the customer without any check",
    )
    fastapi_endpoint_id = fields.Many2one[FastapiEndpoint](required=True)

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", _("Name must be unique")),
        (
            "auth_api_key_uniq",
            "UNIQUE(auth_api_key_id)",
            _("Auth api key can only be used by 1 backend at same time"),
        ),
    ]

    @api.model
    def _selection_picking_policy(self):
        return self.env["sale.order"]._fields["picking_policy"].selection

    @api.model
    def _default_picking_policy(self):
        return self.env["sale.order"]._fields["picking_policy"].default("sale.order")

    @api.model
    def _get_default_sale_reason_backorder_strategy(self):
        return self.env.company.partner_sale_backorder_default_strategy


def fastapi_endpoint_setting(
    api_key: str = Depends(api_key_header),  # noqa: B008
    env: Environment = Depends(odoo_env),  # noqa: B008
    endpoint: FastapiEndpoint = Depends(fastapi_endpoint),  # noqa: B008
) -> FastapiEndpointSettings:
    """Return the fastapi.endpoint record."""
    return (
        env["fastapi.endpoint.settings"]
        .sudo()
        .search(
            [
                ("fastapi_endpoint_id", "=", endpoint.id),
                ("auth_api_key_id.key", "=", api_key),
            ]
        )
    )
