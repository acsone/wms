# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from odoo import api

from odoo.addons.shopinvader_schema_sale.schemas import sale


class Sale(sale.Sale, extends=True):
    channel: str | None = None

    @classmethod
    def from_sale_order(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        res = super().from_sale_order(odoo_rec)
        res.channel = odoo_rec.sale_channel_id.code or None
        return res


class SaleSearch(sale.SaleSearch, extends=True):
    def to_odoo_domain(self, env: api.Environment) -> list:
        domain = super().to_odoo_domain(env)
        domain.append(
            ("sale_channel_id", "in", env["sale.channel"].sudo()._get_internal_ids())
        )
        return domain
