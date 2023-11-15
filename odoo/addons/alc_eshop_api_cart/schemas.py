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

    import_warning_msg: str | None = None
    suite_name: str | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.customer_ref = odoo_rec.client_order_ref or None
        res.import_warning_msg = odoo_rec.import_warning_msg or None
        res.suite_name = odoo_rec.suite_name or None
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
    suite_name: str | None = None

    def to_sale_order_vals(self):
        values = self.model_dump(exclude_unset=True)
        vals = {}
        if "customer_ref" in values:
            vals["client_order_ref"] = self.customer_ref
        if "note" in values:
            vals["note"] = self.note
        if "suite_name" in values:
            vals["suite_name"] = self.suite_name
        return vals


class CartConfirmRequest(CartUpdateRequest):
    ...


class CartSuiteNameValue(StrictExtendableBaseModel):
    value: str | None
