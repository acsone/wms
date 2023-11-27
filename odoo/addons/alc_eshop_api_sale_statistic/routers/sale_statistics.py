# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime
from collections import OrderedDict
from typing import Annotated

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.tools import float_round

from odoo.addons.alc_cerberus_utils import utils
from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import (
    FiveYearsResponse,
    MonthlyOrderedResponse,
    ProductFamily,
    TopOrderedResponse,
)

sale_statistics_router = APIRouter(tags=["sale_statistics"])


@sale_statistics_router.get("/sale_statistics/five_years")
def get_five_years(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
) -> FiveYearsResponse:
    """Last five years sale statistics by product category, chronologically.

    e.g [y-4, ..., y] with y being the current year, of the form:
    {"is_food": 57, "is_equipment": 0, "is_meds": 1300}
    Five years, that's all we've got We've got five years, what a surprise
    """
    return (
        env["alc.eshop.sale_statistics_router.helper"]
        .new({"partner": partner})
        .get_five_years()
    )


@sale_statistics_router.get("/sale_statistics/monthly_ordered/{product_id}")
def get_monthly_ordered_product_id(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    product_id: int,
) -> MonthlyOrderedResponse:
    """Returns the monthly quantity ordered during the last 12 months for.

    the given product.

    (The current month is excluded)
    """
    product = env["product.product"].browse(product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=_(
                "Product not found for id %(product_id)s",
                product_id=product_id,
            ),
        )
    return (
        env["alc.eshop.sale_statistics_router.helper"]
        .new({"partner": partner})
        ._get_monthly_ordered(product)
    )


@sale_statistics_router.get("/sale_statistics/top_ordered")
def get_top_ordered(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    page: int | None = None,
    per_page: int | None = None,
    product_families: Annotated[
        list[ProductFamily] | None, Query(alias="product_families[]")
    ] = None,
    supplier_discount_only: bool | None = None,
) -> TopOrderedResponse:
    """Search the most ordered product along the last 12 months."""
    return (
        env["alc.eshop.sale_statistics_router.helper"]
        .new({"partner": partner})
        ._get_top_ordered(
            page=page,
            per_page=per_page,
            product_families=product_families,
            supplier_discount_only=supplier_discount_only,
        )
    )


class AlcEshopSaleStatisticsRouterHelper(models.AbstractModel):
    _name = "alc.eshop.sale_statistics_router.helper"
    _description = "Helper for the sale statistics router"

    partner = fields.Many2one[Partner]()

    def _get_monthly_ordered(self, product):
        today = datetime.date.today()
        periods = OrderedDict()
        date_start = datetime.date(today.year - 1, today.month, 1)
        date_end = datetime.date(today.year, today.month, 1)
        sql = """
            SELECT
                SUM(product_uom_qty - COALESCE(product_qty_canceled, 0) ),
                CAST(date_trunc('month', date_order) AS date)
            FROM
                sale_order_line sol
                join sale_order so on so.id =  sol.order_Id
            WHERE
                product_id=%(product_id)s
                AND partner_id=%(partner_id)s
                AND order_partner_id=%(partner_id)s
                AND date_order >= %(date_start)s
                AND date_order < %(date_end)s
                AND so.sale_channel_id IN %(channels)s
                AND so.state in ('done', 'sale')
            GROUP BY
                CAST(date_trunc('month', date_order) AS date);
        """
        self.env.cr.execute(
            sql,
            {
                "channels": tuple(self.env["sale.channel"]._get_internal_ids()),
                "product_id": product.id,
                "partner_id": self.partner.id,
                "date_start": date_start,
                "date_end": date_end,
            },
        )
        result = self.env.cr.fetchall()
        total = 0
        rounding = product.uom_id.rounding
        _date = date_start
        for _m in range(12):
            periods.setdefault(_date, 0)
            _date += relativedelta(months=1)
        for qty, date in result:
            periods[date] = float_round(qty, precision_rounding=rounding)
            total += qty
        monthly_average = total / 12.0
        monthly_average = float_round(monthly_average, precision_rounding=rounding)
        return {
            "average": monthly_average,
            "months": periods,
        }

    # flake8: noqa: C901
    def _get_top_ordered(
        self,
        page=None,
        per_page=None,
        product_families: list[ProductFamily] | None = None,
        supplier_discount_only=False,
    ):
        sql = """
    SELECT
        c.count,
        a.*
    FROM (
        (
            SELECT
                count(1)
            FROM
                %(table)s
            WHERE
                partner_id = %(partner_id)s
                %(where)s
        ) as c
    LEFT JOIN
        (
            SELECT
               *
            FROM
                %(table)s
            WHERE
                partner_id = %(partner_id)s
                %(where)s
            ORDER BY
                ordered_count DESC
            LIMIT %(limit)s
            OFFSET %(offset)s
        ) as a
    ON TRUE
    )
        """
        wheres = ["\n"]
        for product_family in product_families or []:
            if product_family == ProductFamily.meds:
                wheres.append("AND is_meds")
            elif product_family == ProductFamily.food:
                wheres.append("AND is_food")
            elif product_family == ProductFamily.equipment:
                wheres.append("AND is_equipment")
        if supplier_discount_only:
            wheres.append("AND in_supplier_promotion")
        self.env.cr.execute(
            sql,
            {
                "table": AsIs(self.env["alc.eshop.product.ordered.qty"]._table),
                "partner_id": self.partner.id,
                "where": AsIs("\n".join(wheres)),
                "limit": per_page,
                "offset": per_page * (page - 1) if (per_page and page) else None,
            },
        )
        data = []
        res = {"size": 0, "data": data}
        size = 0
        for row in self.env.cr.dictfetchall():
            size = row["count"]
            if size == 0:
                # always return a row for the size but with no data if 0...
                break
            product_family = ""
            if row["is_food"]:
                product_family = "food"
            if row["is_meds"]:
                product_family = "meds"
            if row["is_equipment"]:
                product_family = "equipment"
            data.append(
                {
                    "product_id": row["product_id"],
                    "ordered_count": row["ordered_count"],
                    "date_last_ordered": utils.odoo_dt_to_dt_utc(
                        row["date_last_ordered"]
                    ),
                    "product_family": product_family,
                }
            )
        res["size"] = size
        return res

    def get_five_years(self):
        """Last five years sale statistics by product category, chronologically.

        e.g [y-4, ..., y] with y being the current year, of the form:
        {"is_food": 57, "is_equipment": 0, "is_meds": 1300}
        Five years, that's all we've got We've got five years, what a surprise
        """
        query = """
            SELECT *
            FROM %(table)s
            WHERE partner_id = %(partner_id)s
        """
        args = {
            "table": AsIs(self.env["alc.eshop.product.ordered.yearly"]._table),
            "partner_id": self.partner.id,
        }
        self.env.cr.execute(query, args)
        current_year = datetime.date.today().year
        families = ["is_food", "is_equipment", "is_meds"]
        year_range = list(range(current_year - 4, current_year + 1))
        years = {year: {family[3:]: 0 for family in families} for year in year_range}
        for row in self.env.cr.dictfetchall():
            year = row["order_year"]
            family = next((family for family in families if row[family]), None)
            if family and year in years:
                years[year][family[3:]] = years[year][family[3:]] + row["total"]
        # round everything
        data = [years[k] for k in year_range]
        for year in data:
            for family in year:
                year[family] = int(round(year[family]))
        return {"size": 5, "data": data}
