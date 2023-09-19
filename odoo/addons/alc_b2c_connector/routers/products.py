# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env, paging
from odoo.addons.fastapi.schemas import Paging

from ..dependencies import AlcB2cClient, alc_b2c_client
from ..schemas.paged_collection import PagedCollection
from ..schemas.product import Product

router = APIRouter(tags=["products"])


@router.get(
    "/products/search",
    response_model_exclude_unset=True,
)
def get_products(
    paging_: Annotated[Paging, Depends(paging)],
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    client: Annotated[AlcB2cClient, Depends(alc_b2c_client)],
    skus: Annotated[list[str] | None, Query()] = None,
) -> PagedCollection[Product]:
    """
    Return the list of available products.

    For each product, the taxes to applied are provided. The type of amount
    to apply can be one of the following values:
        * fixed: Fixed amount
        * percent, Percentage of Price
        * division, Percentage of Price Tax Included
    """
    products = env["product.product"]._search_products_from_b2c(
        skus, paging_.limit, paging_.offset, client
    )
    return PagedCollection[Product](
        size=len(products),
        data=[Product.from_product_product(product) for product in products],
    )
