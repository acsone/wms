# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import csv
import uuid as uuid_lib
from typing import Annotated, Any, Protocol

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.shopinvader_api_cart.routers.cart import (
    ShopinvaderApiCartRouterHelper as ShopinvaderApiCartRouterHelperBase,
)
from odoo.addons.shopinvader_api_cart.schemas import CartTransaction
from odoo.addons.shopinvader_schema_sale.schemas import Sale

from ..schemas import CartSuiteNameValue, CartUpdateRequest

carts_router = APIRouter(tags=["carts"])


@carts_router.post("/carts/info")
@carts_router.post("/carts/{uuid}/info")
def update_cart_info(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    cart_info: CartUpdateRequest,
    uuid: str | None = None,
) -> Sale:
    """Update cart info."""
    cart = (
        env["shopinvader_api_cart.cart_router.helper"]
        .new({"partner": partner})
        ._update_cart_info(uuid, cart_info)
    )
    return Sale.from_sale_order(cart)


@carts_router.post("/carts/confirm")
@carts_router.post("/carts/{uuid}/confirm")
def confirm(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    cart_info: CartUpdateRequest,
    uuid: str | None = None,
) -> Sale:
    params = cart_info.model_dump(exclude_unset=True)
    uuid = uuid or params.get("uuid")
    cart = env["sale.order"]._find_open_cart(partner.id, uuid)
    if not cart:
        raise HTTPException(status_code=404, detail="No cart found")
    if uuid and cart.uuid != uuid:
        raise HTTPException(status_code=404, detail="No cart found")
    if not cart.partner_id.eshop_ordering_allowed:
        raise ValidationError(_("You are no allowed to pass an order on the EShop"))
    upd_vals = cart_info.to_sale_order_vals()
    upd_vals["date_order"] = fields.Datetime.now()
    upd_vals.update(cart.play_onchanges(upd_vals, upd_vals.keys()))
    if upd_vals:
        cart.write(upd_vals)
    cart.action_confirm_cart()
    cart._notify_note()
    cart.action_confirm()
    return Sale.from_sale_order(cart)


@carts_router.post("/carts/csv")
@carts_router.post("/carts/{uuid}/csv")
def import_csv(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    file: UploadFile,
    uuid: str | None = None,
):
    """Import a CSV file to create / update a cart.

    The content of the file must follow the following rules:

    Columns are separated by a semicolon (;)

    The first line must contain the following columns:
    - suite_name: the name of the suite
    - customer_ref: the customer reference
    - email: the email of the customer
    - note: the note of the cart

    The following lines must contain the following columns:
    - sku: the sku of the product
    - qty: the quantity of the product

    The csv file therefore contains at least 2 lines.
    """
    _no_found, cart = (
        env["shopinvader_api_cart.cart_router.helper"]
        .new({"partner": partner})
        ._import_csv(file.file, uuid=uuid)
    )
    return Sale.from_sale_order(cart)


@carts_router.get("/carts/next_suite_name")
@carts_router.get("/carts/{uuid}/next_suite_name")
def get_next_suite_name(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    uuid: str | None = None,
) -> CartSuiteNameValue:
    """This service return the next suite name to apply to the cart.

    if the cart contains meds products
    """
    cart = env["sale.order"]._find_open_cart(partner.id, uuid)
    value = None
    if cart:
        value = cart.suite_name or cart.get_next_suite_name(cart)
    return CartSuiteNameValue(value=value)


class ByteReader(Protocol):
    """Protocol for a file-like object that can be read as bytes."""

    # pylint: disable=method-required-super
    def read(self, n: int | None = None) -> bytes:
        ...

    def seek(self, n: int) -> None:
        ...


class ShopinvaderApiCartRouterHelper(ShopinvaderApiCartRouterHelperBase):

    partner = fields.Many2one[Partner]()

    def _update_cart_info(self, uuid: str | None, cart_info: CartUpdateRequest):
        """Update cart info."""
        params = cart_info.model_dump(exclude_unset=True)
        uuid = uuid or params.get("uuid")
        cart = self.env["sale.order"]._find_open_cart(self.partner.id, uuid)
        if not cart:
            cart = self.env["sale.order"]._create_empty_cart(self.partner.id)
        if not uuid or cart.uuid == uuid:
            # update only if the cart is the one requested
            upd_vals = cart_info.to_sale_order_vals()
            if upd_vals:
                cart.write(upd_vals)
        return cart

    def _import_csv(
        self, csv_file: ByteReader, uuid: str | None = None
    ) -> tuple[list[str], SaleOrder]:
        """Import a CSV file to create / update a cart.

        The content of the file must follow the following rules:

        Columns are separated by a semicolon (;)

        The first line must contain the following columns:
        - suite_name: the name of the suite
        - customer_ref: the customer reference
        - email: the email of the customer
        - note: the note of the cart

        The following lines must contain the following columns:
        - sku: the sku of the product
        - qty: the quantity of the product

        The csv file therefore contains at least 2 lines.
        """
        (
            _not_found_skus,
            cart_info,
            transactions,
        ) = self._get_cart_info_and_transactions(csv_file)
        cart = self.env["sale.order"]._find_open_cart(self.partner.id, uuid)
        cart = self._sync_cart(self.partner, cart, uuid, transactions)
        if cart and cart_info:
            cart.write(cart_info)
        return _not_found_skus, cart

    def _get_cart_info_and_transactions(
        self, csv_file: ByteReader
    ) -> tuple[list[str], dict[str, Any], list[CartTransaction]]:
        """Return a tuple (unknown skus, cart_info, list of transactions to apply).

        from the csv file
        """
        # the file object is in binary mode
        # we need to decode it to get a string
        csv_file.seek(0)
        csv_file = csv_file.read().decode("utf-8").splitlines()
        csv_lines = list(csv.reader(csv_file, delimiter=";"))
        if not len(csv_lines) > 1:
            raise ValueError("Not enough lines.")
        info = {}
        if len(csv_lines[0]) < 4:
            raise ValueError("Missing columns in contact line.")
        info["suite_name"] = csv_lines[0][0] or False
        info["client_order_ref"] = csv_lines[0][1] or False
        info["note"] = csv_lines[0][3] or False
        not_found_skus, transactions = self._csv_lines_to_transactions(csv_lines[1:])
        if not_found_skus:
            msg = _(
                "The following sku are unknown: %(skus)s\n"
                "The corresponding lines have been ignored by the import process.",
                skus=", ".join(not_found_skus),
            )
            info["import_warning_msg"] = msg
        else:
            # reset warning message if no more unknown SKU
            info["import_warning_msg"] = None
        return not_found_skus, info, transactions

    def _csv_lines_to_transactions(
        self, csv_lines
    ) -> tuple[list[str], list[CartTransaction]]:
        """Return a tuple (list of sku not found, list of transactions to apply).

        from the csv lnes
        """
        lines = []
        not_found_skus = []
        skus = []
        for values in csv_lines:
            if len(values) < 2:
                raise ValueError("Missing column in product line.")
            skus.append(values[0])

        product_by_sku = self._get_product_by_sku(skus=skus)
        for values in csv_lines:
            sku = values[0]
            qty = values[1]
            product = product_by_sku.get(sku)
            if product:
                line_id = str(uuid_lib.uuid4())
                line = CartTransaction(
                    product_id=product.id,
                    qty=int(qty),
                    uuid=line_id,
                )
                lines.append(line)
            else:
                not_found_skus.append(sku)
        return not_found_skus, lines

    def _get_product_by_sku(self, skus) -> dict[str, ProductProduct]:
        domain = self.partner._get_product_domain()
        domain.append(("default_code", "in", skus))
        return {p.default_code: p for p in self.env["product.product"].search(domain)}
