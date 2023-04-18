# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi.depends import authenticated_partner_env, paging
from odoo.addons.fastapi.schemas import PagedCollection, Paging

from ..models.fastapi_endpoint import b2c_api_router
from .models.product import Product


@b2c_api_router.get(
    "/products/search",
    response_model=PagedCollection[Product],
    response_model_exclude_unset=True,
)
def get_products(
    paging_: Paging = Depends(paging),  # noqa: B008
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
) -> PagedCollection[Product]:
    """
    Return the list of available products.

    For each product, the taxes to applied are provided. The type of amount
    to apply can be one of the following values:
        * fixed: Fixed amount
        * percent, Percentage of Price
        * division, Percentage of Price Tax Included
    """
    count = env["product.product"].search_count([])
    products = env["product.product"].search(
        [], limit=paging_.limit, offset=paging_.offset
    )
    return PagedCollection[Product](
        total=count,
        items=[Product.from_orm(product) for product in products],
    )
