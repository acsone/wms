# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env
from odoo.addons.fastapi.schemas import Paging

from ..dependencies import AlcB2cClient, alc_b2c_client, ids_list, paging
from ..schemas.paged_collection import PagedCollection
from ..schemas.sale_order import (
    SaleOrderCreateRequest,
    SaleOrderResponse,
    SaleOrderUpdateRequest,
)

router = APIRouter(tags=["sales"])


@router.post("/sales/create")
def _create_sale_order(
    body: SaleOrderCreateRequest,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    client: Annotated[AlcB2cClient, Depends(alc_b2c_client)],
) -> SaleOrderResponse:
    """Create a sale order."""
    data = body._convert_to_write()
    sale_order = env["sale.order"]._create_from_b2c(data, client)
    return SaleOrderResponse.from_sale_order(sale_order)


@router.get(
    "/sales/search",
    response_model_exclude_unset=True,
)
@router.get(
    "/sales/",
    response_model_exclude_unset=True,
)
def get_sale_orders(
    paging_: Annotated[Paging, Depends(paging)],
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    client: Annotated[AlcB2cClient, Depends(alc_b2c_client)],
    ids: Annotated[list[int] | None, Depends(ids_list)] = None,
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
        data=[
            SaleOrderResponse.from_sale_order(sale_order) for sale_order in sale_orders
        ],
    )


@router.get("/sales/{id}")
@router.get("/sales/{id}/get")
def _get_sale_order(
    id: int,  # pylint: disable=redefined-builtin
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    client: Annotated[AlcB2cClient, Depends(alc_b2c_client)],
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
    return SaleOrderResponse.from_sale_order(sale_order)


@router.post("/sales/{id}/cancel")
def _cancel_sale_order(
    id: int,  # pylint: disable=redefined-builtin
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    client: Annotated[AlcB2cClient, Depends(alc_b2c_client)],
) -> SaleOrderResponse:
    """
    Cancel Sale Order.

    Cancelling a sale order is only possible until
    the preparation has started (i.e., the picking is printed)
    """
    sale_order = env["sale.order"]._get_order_from_b2c_ref(id, client)
    sale_order._cancel_from_b2c()
    return SaleOrderResponse.from_sale_order(sale_order)


@router.post("/sales/{id}")
@router.post("/sales/{id}/update")
@router.put("/sales/{id}")
def _update_sale_order(
    id: int,  # pylint: disable=redefined-builtin
    body: SaleOrderUpdateRequest,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    client: Annotated[AlcB2cClient, Depends(alc_b2c_client)],
) -> SaleOrderResponse:
    """Update sale order."""
    sale_order = env["sale.order"]._get_order_from_b2c_ref(id, client)
    data = body._convert_to_write()
    sale_order._update_from_b2c(data, client)
    return SaleOrderResponse.from_sale_order(sale_order)
