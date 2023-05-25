# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from fastapi import Depends, Query

from odoo.api import Environment

from odoo.addons.fastapi.depends import authenticated_partner_env, paging
from odoo.addons.fastapi.schemas import Paging

from ..models.fastapi_endpoint import b2c_api_router
from .depends import AlcB2cClient, alc_b2c_client
from .models.sale_order import (
    SaleOrderCreateRequest,
    SaleOrderResponse,
    SaleOrderUpdateRequest,
)
from .utils import PagedCollection


@b2c_api_router.post("/sales/create", response_model=SaleOrderResponse)
def _create_sale_order(
    body: SaleOrderCreateRequest,
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    client: AlcB2cClient = Depends(alc_b2c_client),  # noqa: B008,
) -> SaleOrderResponse:
    """Create a sale order."""
    data = body._convert_to_write()
    sale_order = env["sale.order"]._create_from_b2c(data, client)
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
    ids: list[int] | None = Query(None),
    paging_: Paging = Depends(paging),  # noqa: B008
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    client: AlcB2cClient = Depends(alc_b2c_client),  # noqa: B008,
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
        b2c_client=client,
    )
    count = len(sale_orders)
    return PagedCollection[SaleOrderResponse](
        size=count,
        data=[SaleOrderResponse.from_orm(sale_order) for sale_order in sale_orders],
    )


@b2c_api_router.get("/sales/{id}", response_model=SaleOrderResponse)
@b2c_api_router.get("/sales/{id}/get", response_model=SaleOrderResponse)
def _get_sale_order(
    id: int,  # pylint: disable=redefined-builtin
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    client: AlcB2cClient = Depends(alc_b2c_client),  # noqa: B008,
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
    sale_order = env["sale.order"]._get_order_from_b2c_ref(id, client)
    return SaleOrderResponse.from_orm(sale_order)


@b2c_api_router.post("/sales/{id}/cancel", response_model=SaleOrderResponse)
def _cancel_sale_order(
    id: int,  # pylint: disable=redefined-builtin
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    client: AlcB2cClient = Depends(alc_b2c_client),  # noqa: B008,
) -> SaleOrderResponse:
    """
    Cancel Sale Order.

    Cancelling a sale order is only possible until
    the preparation has started (i.e., the picking is printed)
    """
    sale_order = env["sale.order"]._get_order_from_b2c_ref(id, client)
    sale_order._cancel_from_b2c()
    return SaleOrderResponse.from_orm(sale_order)


@b2c_api_router.post("/sales/{id}", response_model=SaleOrderResponse)
@b2c_api_router.post("/sales/{id}/update", response_model=SaleOrderResponse)
@b2c_api_router.put("/sales/{id}", response_model=SaleOrderResponse)
def _update_sale_order(
    id: int,  # pylint: disable=redefined-builtin
    body: SaleOrderUpdateRequest,
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    client: AlcB2cClient = Depends(alc_b2c_client),  # noqa: B008,
) -> SaleOrderResponse:
    """Update sale order."""
    sale_order = env["sale.order"]._get_order_from_b2c_ref(id, client)
    data = body._convert_to_write()
    sale_order._update_from_b2c(data, client)
    return SaleOrderResponse.from_orm(sale_order)
