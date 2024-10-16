# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from odoo import api, models
from odoo.osv import expression
from odoo.tools.query import Query as SQLQuery
from odoo.tools.query import _generate_table_alias

from odoo.addons.alc_supplier_promotion.models.product_supplierinfo import (
    ProductSupplierInfo,
)
from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import Discount, DiscountList

discounts_router = APIRouter(tags=["discounts"])


@discounts_router.get("/discounts", status_code=200)
def get(
    partner: Annotated[Partner, Depends(authenticated_partner)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    limit: int | None = 10,
    page: int = 1,
    reference: Annotated[
        str | None,
        Query(descripton="The product reference you search the discount for"),
    ] = None,
    reference__ilike: Annotated[
        str | None,
        Query(descripton="Part of the product reference you search the discount for"),
    ] = None,
) -> DiscountList:
    """Get the discounts for a partner."""
    count, records = (
        env["alc.eshop.discounts_router.helper"]
        .sudo()
        ._search_supplierinfo_discounts(
            partner=partner,
            limit=limit,
            page=page,
            reference=reference,
            reference__ilike=reference__ilike,
        )
    )
    return DiscountList(
        data=[Discount.from_product_supplierinfo(record) for record in records],
        size=count,
    )


class AlcEshopDiscountsRouterHelper(models.AbstractModel):
    _name = "alc.eshop.discounts_router.helper"
    _description = "Helper for the discounts router"

    def _search_supplierinfo_discounts(
        self,
        partner: Partner,
        limit: int | None = 10,
        page: int = 1,
        reference: str | None = None,
        reference__ilike: str | None = None,
    ) -> tuple[int, ProductSupplierInfo]:
        supplierinfo_model = self.env["product.supplierinfo"]
        offset = limit * (page - 1) if limit and page else 0
        if not partner.supplier_promotion_sale_allowed:
            return 0, supplierinfo_model
        product_domain = partner._get_product_domain()
        if reference:
            product_domain.append(("default_code", "=", reference))
        if reference__ilike:
            product_domain.append(("default_code", "ilike", reference__ilike))
        supplierinfo_domain = [("is_past", "=", False)]
        if partner.partner_type != "veterinary":
            supplierinfo_domain.append(["only_for_veterinaries", "=", False])
        return self._do_search_supplierinfo_discounts(
            product_domain=product_domain,
            supplierinfo_domain=supplierinfo_domain,
            limit=limit,
            offset=offset,
        )

    def _do_search_supplierinfo_discounts(
        self, product_domain, supplierinfo_domain, limit, offset
    ) -> tuple[int, ProductSupplierInfo]:
        supplierinfo_model = self.env["product.supplierinfo"]
        prodduct_model = self.env["product.product"]
        supplierinfo_query = supplierinfo_model._where_calc(supplierinfo_domain)
        supplierinfo_model._apply_ir_rules(supplierinfo_query, "read")
        product_alias = _generate_table_alias("product_product", link="product_tmpl_id")
        product_query = SQLQuery(self.env.cr, product_alias, prodduct_model._table)
        product_query = expression.expression(
            product_domain,
            prodduct_model,
            alias=product_alias,
            query=product_query,
        ).query
        prodduct_model._apply_ir_rules(product_query, "read")

        product_query.add_where(
            f"{product_alias}.product_tmpl_id = product_supplierinfo.product_tmpl_id"
        )
        subquery, subparams = product_query.subselect("1")
        supplierinfo_query.add_where(f"EXISTS({subquery})", subparams)
        query, params = supplierinfo_query.select("count(1)")
        self.env.cr.execute(query, params)
        count = self.env.cr.fetchone()[0]
        records = supplierinfo_model
        if count:
            supplierinfo_query.limit = limit
            supplierinfo_query.offset = offset
            records = supplierinfo_model.browse(supplierinfo_query)
        return count, records
