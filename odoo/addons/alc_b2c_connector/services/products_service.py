# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from fastapi import Depends, Query

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env, paging
from odoo.addons.fastapi.schemas import Paging

from ..models.fastapi_endpoint import b2c_api_router
from .dependencies import AlcB2cClient, alc_b2c_client
from .models.product import Product
from .utils import PagedCollection


@b2c_api_router.get(
    "/products/search",
    response_model=PagedCollection[Product],
    response_model_exclude_unset=True,
)
@b2c_api_router.get(
    "/stocks/search",
    response_model=PagedCollection[Product],
    response_model_exclude_unset=True,
)
def get_products(
    paging_: Paging = Depends(paging),  # noqa: B008
    skus: list[str] | None = Query(None),  # noqa: B008
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    client: AlcB2cClient = Depends(alc_b2c_client),  # noqa: B008,
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
        data=[Product.from_orm(product) for product in products],
    )
