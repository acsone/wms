# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from odoo import api

from odoo.addons.fastapi.dependencies import authenticated_partner_env

from ..schemas import ProductBrand, ProductBrandList

brands_router = APIRouter(tags=["brands"])


@brands_router.get("/brands/", status_code=200)
def _list(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    name: str | None = None,
    name__ilike: str | None = None,
) -> ProductBrandList:
    """Search brands.

    This endpoint is used to search brands. The response is a list of brands.
    """
    model = env["product.brand"].sudo()
    domain = []
    if name:
        domain.append(("name", "=", name))
    if name__ilike:
        domain.append(("name", "ilike", name__ilike))
    count = model.sudo().search_count(domain)
    brands = model.sudo().search(domain)
    brands_data = brands.read(["id", "name"])
    return ProductBrandList(data=brands_data, size=count)


@brands_router.get("/brands/{_id}", status_code=200)
def get(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    _id: int,
) -> ProductBrand:
    """Get a brand.

    This endpoint is used to get brand information for a given id.
    """
    model = env["product.brand"].sudo()
    brand = model.sudo().browse(_id)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand with id {_id} not found")
    return ProductBrand(id=brand.id, name=brand.name)
