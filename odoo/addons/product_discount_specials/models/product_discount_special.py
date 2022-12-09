# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from dateutil.relativedelta import relativedelta
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductDiscountSpecial(models.Model):
    _name = "product.discount.special"
    _inherit = "mixin.past"

    sequence = fields.Integer("Sequence")

    date_start = fields.Date(
        "Start Date", required=True, default=lambda a: a.default_today()
    )
    date_end = fields.Date(
        "End Date", required=True, default=lambda a: a.default_in_one_month()
    )

    product_template_id = fields.Many2one("product.template", required=True)

    @api.model
    def default_today(self):
        return self.env.context.get("date", fields.Date.context_today(self))

    @api.model
    def default_in_one_month(self):
        today_str = self.default_today()
        today = fields.Date.from_string(today_str)
        return fields.Date.to_string(today + relativedelta(months=1))

    @api.constrains("product_template_id", "date_start", "date_end")
    def _check_dates_no_overlap(self):
        for record in self:
            if record.date_start > record.date_end:
                raise ValidationError(
                    _("%s must be > %s") % (record.date_end, record.date_start,)
                )
            # OVERLAPS in postgresql allows to start range 2 the same day range 1 ends.
            # We check no overlaps at borders in addition
            SQL = """
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
                SQL,
                dict(
                    table=AsIs(self._table),
                    start=record.date_start,
                    end=record.date_end,
                    discount_id=record.id,
                    template_id=record.product_template_id.id,
                ),
            )
            res = self.env.cr.fetchall()
            if res:
                ids = [r[0] for r in res]
                others = self.browse(ids)
                others_date_start = others.mapped("date_start")
                others_date_end = others.mapped("date_end")
                raise ValidationError(
                    _(
                        "date start %s, date end %s for product %s overlaps already existing date start %s, date end %s"
                    )
                    % (
                        record.date_start,
                        record.date_end,
                        record.product_template_id.name,
                        others_date_start,
                        others_date_end,
                    )
                )
