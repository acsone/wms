# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List, Optional

from fastapi import Depends, Query

from odoo.api import Environment

from odoo.addons.fastapi.depends import authenticated_partner_env, paging
from odoo.addons.fastapi.schemas import PagedCollection, Paging

from ..models.fastapi_endpoint import b2c_api_router
from ..models.fastapi_endpoint_settings import (
    FastapiEndpointSettings,
    fastapi_endpoint_setting,
)
from .models.sale_order import (
    SaleOrderCreateRequest,
    SaleOrderResponse,
    SaleOrderUpdateRequest,
)


@b2c_api_router.post("/sales/create", response_model=SaleOrderResponse)
def _create_sale_order(
    body: SaleOrderCreateRequest,
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    endpoint_setting: FastapiEndpointSettings = Depends(  # noqa: B008
        fastapi_endpoint_setting
    ),
) -> SaleOrderResponse:
    """Create a sale order."""
    data = body._convert_to_write()
    sale_order = env["sale.order"]._create_from_b2c(data, endpoint_setting)
    return SaleOrderResponse.from_orm(sale_order)


@b2c_api_router.get(
    "/sales/search",
    response_model=PagedCollection[SaleOrderResponse],
    response_model_exclude_unset=True,
)
@b2c_api_router.get(
    "/sales/",
    response_model=PagedCollection[SaleOrderResponse],
    response_model_exclude_unset=True,
)
def get_sale_orders(
    ids: Optional[List[int]] = Query(None),
    paging_: Paging = Depends(paging),  # noqa: B008
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    endpoint_setting: FastapiEndpointSettings = Depends(  # noqa: B008
        fastapi_endpoint_setting
    ),
) -> PagedCollection[SaleOrderResponse]:
    """
    Get orders info.

    More information on the response content is available
    on the 'get' method
    """
    sale_orders = env["sale.order"]._search_orders_from_b2c(
        b2c_refs=ids,
        limit=paging_.limit,
        offset=paging_.offset,
        endpoint_setting=endpoint_setting,
    )
    count = len(sale_orders)
    return PagedCollection[SaleOrderResponse](
        total=count,
        items=[SaleOrderResponse.from_orm(sale_order) for sale_order in sale_orders],
    )


@b2c_api_router.get("/sales/{id}", response_model=SaleOrderResponse)
@b2c_api_router.get("/sales/{id}/get", response_model=SaleOrderResponse)
def _get_sale_order(
    id: int,  # pylint: disable=redefined-builtin
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    endpoint_setting: FastapiEndpointSettings = Depends(  # noqa: B008
        fastapi_endpoint_setting
    ),
) -> SaleOrderResponse:
    """
    Get order info:

    Into the response:
     * the field state can have one of the following value:
       * draft: Quote received and created into our system
       * sale: Sale Order confirmed
       * cancel: Sale Order cancelled
       * delivery: Sale Order sent to the vet
    * When state is "delivery" delivery info are provided by the
    deliveries field
    """
    sale_order = env["sale.order"]._get_order_from_b2c_ref(id, endpoint_setting)
    return SaleOrderResponse.from_orm(sale_order)


@b2c_api_router.post("/sales/{id}/cancel", response_model=SaleOrderResponse)
def _cancel_sale_order(
    id: int,  # pylint: disable=redefined-builtin
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    endpoint_setting: FastapiEndpointSettings = Depends(  # noqa: B008
        fastapi_endpoint_setting
    ),
) -> SaleOrderResponse:
    """
    Cancel Sale Order.

    Cancelling a sale order is only possible until
    the preparation has started (i.e., the picking is printed)
    """
    sale_order = env["sale.order"]._get_order_from_b2c_ref(id, endpoint_setting)
    sale_order._cancel_from_b2c()
    return SaleOrderResponse.from_orm(sale_order)


@b2c_api_router.post("/sales/{id}", response_model=SaleOrderResponse)
@b2c_api_router.post("/sales/{id}/update", response_model=SaleOrderResponse)
@b2c_api_router.put("/sales/{id}", response_model=SaleOrderResponse)
def _update_sale_order(
    id: int,  # pylint: disable=redefined-builtin
    body: SaleOrderUpdateRequest,
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    endpoint_setting: FastapiEndpointSettings = Depends(  # noqa: B008
        fastapi_endpoint_setting
    ),
) -> SaleOrderResponse:
    """Update sale order."""
    sale_order = env["sale.order"]._get_order_from_b2c_ref(id, endpoint_setting)
    data = body._convert_to_write()
    sale_order._update_from_b2c(data, endpoint_setting)
    return SaleOrderResponse.from_orm(sale_order)
