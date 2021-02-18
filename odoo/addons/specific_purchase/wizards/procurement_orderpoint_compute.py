# -*- coding: utf-8 -*-
import logging
import threading
from datetime import datetime

import odoo
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

MANAGE_DAY_PREFIX = "is_manage_day_"


class ProcurementOrderpointCompute(models.TransientModel):
    _inherit = "procurement.orderpoint.compute"

    is_manage_day_1 = fields.Boolean("Monday")
    is_manage_day_2 = fields.Boolean("Tuesday")
    is_manage_day_3 = fields.Boolean("Wednesday")
    is_manage_day_4 = fields.Boolean("Thursday")
    is_manage_day_5 = fields.Boolean("Friday")
    is_manage_day_6 = fields.Boolean("Saturday")
    is_manage_day_7 = fields.Boolean("Sunday")

    type = fields.Selection(
        [("by_suppliers", "By suppliers"), ("by_days", "By days")],
        string="Type",
        default="by_suppliers",
        required=True,
    )
    supplier_ids = fields.Many2many(
        "res.partner", string="Suppliers", domain=[("supplier", "=", True)]
    )

    @api.model
    def default_get(self, fields_list):
        result = super(ProcurementOrderpointCompute, self).default_get(fields_list)

        field_name = MANAGE_DAY_PREFIX + str(datetime.now().isoweekday())
        result[field_name] = True

        return result

    @api.multi
    def procure_calculation(self):
        self.ensure_one()

        kwargs = {}
        if self.type == "by_days":
            kwargs["type"] = self.type
            is_day_selected = False
            for day in range(1, 8):
                field_name = MANAGE_DAY_PREFIX + str(day)
                if self[field_name]:
                    is_day_selected = True
                    kwargs[field_name] = True
            if not is_day_selected:
                raise UserError(_("Please select at least one day"))
        else:
            supplier_ids = self.supplier_ids.ids
            kwargs["type"] = self.type
            kwargs["supplier_ids"] = supplier_ids
            if not supplier_ids:
                raise UserError(_("Please select at least one supplier"))

        threaded_calculation = threading.Thread(
            target=self._specific_procure_calculation_orderpoint, kwargs=kwargs
        )
        threaded_calculation.start()
        return {"type": "ir.actions.act_window_close"}

    def _specific_procure_calculation_orderpoint(self, **kwargs):
        """
        Specific method to execute the procurement.
        This method is not called by the scheduler !
        :param kwargs:
        :return:
        """
        context = self._context.copy()
        context.update(kwargs)

        with api.Environment.manage():
            # As this function is in a new thread, I need to open a new cursor,
            # because the old one may be closed
            with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                self_in_new_cr = self.with_env(self.env(cr=new_cr, context=context))
                scheduler_cron = self_in_new_cr.sudo().env.ref(
                    "procurement.ir_cron_scheduler_action"
                )
                # Avoid to run the scheduler multiple times in the same time
                # Alcyon doesn't use this cron. It's why I can use it.
                try:
                    with tools.mute_logger("odoo.sql_db"):
                        self_in_new_cr._cr.execute(
                            "SELECT id FROM ir_cron WHERE id = %s " "FOR UPDATE NOWAIT",
                            (scheduler_cron.id,),
                        )
                except Exception:
                    _logger.info(
                        "Attempt to run procurement scheduler aborted,"
                        " as already running"
                    )
                    self_in_new_cr._cr.rollback()
                    return {}

                self_in_new_cr.env["procurement.order"]._procure_orderpoint_confirm(
                    use_new_cursor=True, company_id=self.env.user.company_id.id
                )
                return {}
