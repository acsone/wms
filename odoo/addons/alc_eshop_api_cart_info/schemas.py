# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from extendable_pydantic.models import StrictExtendableBaseModel
from pydantic import Field

from odoo.addons.shopinvader_schema_sale import schemas


class Sale(schemas.Sale, extends=True):
    customer_ref: Annotated[
        str | None,
        Field(
            description="Prefer the use of the client_order_ref field",
            json_schema_extra={"deprecated": True},
        ),
    ] = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.customer_ref = odoo_rec.client_order_ref or None
        return res


class CartUpdateRequest(StrictExtendableBaseModel, extra="ignore"):
    uuid: Annotated[
        str | None,
        Field(
            description="Prefer the use of the uuid into the query path",
            json_schema_extra={"deprecated": True},
        ),
    ] = None
    customer_ref: str | None = None
    note: str | None = None
