# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from dateutil.relativedelta import relativedelta
from psycopg2.extensions import AsIs

from odoo import _, api, fields
from odoo.exceptions import ValidationError
from odoo.models import Model

from odoo.addons.product.models.product_template import ProductTemplate


class ProductDiscountSpecial(Model):
    _name = "product.discount.special"
    _description = "Product Discount Special"
    _inherit = "mixin.past"

    sequence = fields.Integer("Sequence")
    date_start = fields.Date(
        "Start Date", required=True, default=lambda a: a.default_today()
    )
    date_end = fields.Date(
        "End Date", required=True, default=lambda a: a.default_in_one_month()
    )

    product_template_id = fields.Many2one[ProductTemplate](required=True)

    def name_get(self):
        result = []
        for rec in self:
            name = _("Discount special: {product}. {start} - {end}").format(
                product=rec.product_template_id.display_name,
                start=rec.date_start,
                end=rec.date_end,
            )
            result.append((rec.id, name))

        return result

    @api.model
    def default_today(self):
        date_str = self.env.context.get("date")
        if date_str:
            return fields.Date.from_string(date_str)
        return fields.Date.context_today(self)

    @api.model
    def default_in_one_month(self):
        today = self.default_today()
        return fields.Date.to_string(today + relativedelta(months=1))

    @api.constrains("product_template_id", "date_start", "date_end")
    def _check_dates_no_overlap(self):
        for record in self:
            if record.date_start > record.date_end:
                raise ValidationError(
                    _("{end} must be > {start}").format(
                        end=record.date_end, start=record.date_start
                    )
                )
            # OVERLAPS in postgresql allows to start range 2 the same day range 1 ends.
            # We check no overlaps at borders in addition
            sql_query = """
                SELECT
                    id
                FROM
                    %(table)s discount
                WHERE
                    ((discount.date_start, discount.date_end) OVERLAPS (%(start)s, %(end)s)
                    OR discount.date_end = %(start)s
                    OR discount.date_start = %(end)s)
                    AND discount.id != %(discount_id)s
                    AND discount.product_template_id = %(template_id)s
                    """
            self.env.cr.execute(
                sql_query,
                {
                    "table": AsIs(self._table),
                    "start": record.date_start,
                    "end": record.date_end,
                    "discount_id": record.id,
                    "template_id": record.product_template_id.id,
                },
            )
            res = self.env.cr.fetchall()
            if res:
                ids = [r[0] for r in res]
                others = self.browse(ids)
                others_date_start = others.mapped("date_start")
                others_date_end = others.mapped("date_end")
                raise ValidationError(
                    _(
                        "date start {start}, date end {end} for product {product} "
                        "overlaps already existing date start {others_date_start}, "
                        "date end {others_date_end}"
                    ).format(
                        start=record.date_start,
                        end=record.date_end,
                        product=record.product_template_id.name,
                        others_date_start=others_date_start,
                        others_date_end=others_date_end,
                    )
                )
