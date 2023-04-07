# Copyright ACSONE SA/NV n
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.stock.models.res_partner import Partner
from odoo.addons.stock.wizard.stock_scheduler_compute import (
    StockSchedulerCompute as StockSchedulerComputeBase,
)

MANAGE_DAY_PREFIX = "is_manage_day_"


class StockSchedulerCompute(StockSchedulerComputeBase):
    is_manage_day_1 = fields.Boolean("Monday")
    is_manage_day_2 = fields.Boolean("Tuesday")
    is_manage_day_3 = fields.Boolean("Wednesday")
    is_manage_day_4 = fields.Boolean("Thursday")
    is_manage_day_5 = fields.Boolean("Friday")
    is_manage_day_6 = fields.Boolean("Saturday")
    is_manage_day_7 = fields.Boolean("Sunday")

    procure_type = fields.Selection(
        [("by_suppliers", "By suppliers"), ("by_days", "By days")],
        string="Type",
        default="by_suppliers",
        required=True,
    )
    supplier_ids = fields.Many2many[Partner](
        string="Suppliers", domain=[("is_supplier", "=", True)]
    )

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        field_name = MANAGE_DAY_PREFIX + str(datetime.now().isoweekday())
        result[field_name] = True
        return result

    def procure_calculation(self):
        self.ensure_one()
        context = {}
        if self.procure_type == "by_days":
            context["procure_type"] = self.procure_type
            is_day_selected = False
            for day in range(1, 8):
                field_name = MANAGE_DAY_PREFIX + str(day)
                if self[field_name]:
                    is_day_selected = True
                    context[field_name] = True
            if not is_day_selected:
                raise UserError(_("Please select at least one day"))
        else:
            supplier_ids = self.supplier_ids.ids
            context["procure_type"] = self.procure_type
            context["supplier_ids"] = supplier_ids
            if not supplier_ids:
                raise UserError(_("Please select at least one supplier"))
        return super(
            StockSchedulerCompute, self.with_context(**context)
        ).procure_calculation()
