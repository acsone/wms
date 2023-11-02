# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from extendable_pydantic.models import StrictExtendableBaseModel
from pydantic import Field

from odoo.addons.shopinvader_api_cart import schemas


class CartResponse(schemas.CartResponse, extends=True):
    customer_ref: str | None = None

    @classmethod
    def from_cart(cls, odoo_rec):
        res = super().from_cart(odoo_rec)
        res.customer_ref = odoo_rec.client_order_ref
        return res


class CartUpdateRequest(StrictExtendableBaseModel):
    uuid: Annotated[
        str | None,
        Field(
            description="Prefer the use of the uuid into the query path",
            json_schema_extra={"deprecated": True},
        ),
    ] = None
    customer_ref: str | None = None
    note: str | None = None
