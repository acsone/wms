# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from odoo import api

from odoo.addons.alc_product_flattened_data.models.alc_product_flattened_data import (
    AlcProductFlattenedData,
)
from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import Lang, Product, ProductList

catalog_router = APIRouter(tags=["catalog"])


def product_flattened_data_model(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)]
) -> AlcProductFlattenedData:
    return env["alc.product.flattened.data"].sudo()


@catalog_router.get("/catalog/", status_code=200)
def search(
    model: Annotated[AlcProductFlattenedData, Depends(product_flattened_data_model)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    code_amm: str | None = None,
    code_amm__ilike: str | None = None,
    lang: Lang | None = None,
    name: str | None = None,
    name__ilike: str | None = None,
    reference: str | None = None,
    reference__ilike: str | None = None,
    limit: int | None = 10,
    page: int = 1,
) -> ProductList:
    """Search products available for the partner."""
    domain = partner._get_product_domain()
    if code_amm:
        domain.append(("code_amm", "=", code_amm))
    if code_amm__ilike:
        domain.append(("code_amm", "ilike", code_amm__ilike))
    if name:
        domain.append(("name", "=", name))
    if name__ilike:
        domain.append(("name", "ilike", name__ilike))
    if reference:
        domain.append(("reference", "=", reference))
    if reference__ilike:
        domain.append(("reference", "ilike", reference__ilike))
    if lang:
        lang = LANG_BY_LANG_PREFIX[lang.value]
    domain = model._product_domain_to_model_domain(domain)
    model = model.with_context(lang=lang).sudo()
    offset = limit * (page - 1) if limit and page else 0
    count = model.search_count(domain)
    records_iterator = model._get_partner_products_iterator(
        partner, domain_extend=domain, limit=limit, offset=offset
    )
    return ProductList(
        data=[
            Product.from_product_flattened_data(record) for record in records_iterator
        ],
        size=count,
    )


@catalog_router.get("/catalog/{reference}", status_code=200)
def get_by_reference(
    model: Annotated[AlcProductFlattenedData, Depends(product_flattened_data_model)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    reference: str,
) -> Product:
    """Get a product by reference."""
    domain = partner._get_product_domain()
    domain.append(("default_code", "=", reference))
    record = model._get_partner_products_iterator(partner, domain_extend=domain)
    # safe iterate over iterator to get the first record
    record = next(record, None)
    if not record:
        raise HTTPException(
            status_code=404, detail=f"No product found with reference {reference}"
        )
    return Product.from_product_flattened_data(record)


LANG_BY_LANG_PREFIX = {
    "en": "en_US",
    "fr": "fr_BE",
    "nl": "nl_BE",
}
