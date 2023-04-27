# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List, Optional

from fastapi import Depends, Query

from odoo.api import Environment

from odoo.addons.fastapi.depends import authenticated_partner_env, paging
from odoo.addons.fastapi.schemas import Paging

from ..models.fastapi_endpoint import b2c_api_router
from ..models.fastapi_endpoint_settings import (
    FastapiEndpointSettings,
    fastapi_endpoint_setting,
)
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
    skus: Optional[List[str]] = Query(None),
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    endpoint_setting: FastapiEndpointSettings = Depends(  # noqa: B008
        fastapi_endpoint_setting
    ),
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
        skus, paging_.limit, paging_.offset, endpoint_setting
    )
    return PagedCollection[Product](
        size=len(products),
        data=[Product.from_orm(product) for product in products],
    )
