from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CronDeliveryPlan(models.Model):
    _name = "cron.delivery.plan"
    _order = "next_execution"

    week_day = fields.Selection(
        [
            (1, "Monday"),
            (2, "Tuesday"),
            (3, "Wednesday"),
            (4, "Thursday"),
            (5, "Friday"),
            (6, "Saturday"),
            (7, "Sunday"),
        ],
        string="Week day",
        help="Set the day to execute the plan " "each week",
    )
    date_overwrite = fields.Date(
        "Date overwrite", help="Set a date to execute the plan " "only once time"
    )
    next_execution = fields.Date(
        "Next execution", compute="_compute_next_execution", store=True, readonly=True
    )
    active = fields.Boolean("Active", default=True)
    version_id = fields.Many2one(
        "round.template.version", string="Version", required=True
    )
    tag_ids = fields.Many2many("round.tag", string="Tags")

    @api.depends("week_day", "date_overwrite")
    def _compute_next_execution(self):
        for line in self:
            if not line.active:
                continue

            if line.date_overwrite:
                line.next_execution = line.date_overwrite
            elif line.week_day:
                today = datetime.now() + relativedelta(days=1)
                while today.isoweekday() != line.week_day:
                    today += relativedelta(days=1)
                line.next_execution = fields.Date.to_string(today)

    @api.constrains("week_day", "date_overwrite")
    def constrains_date(self):
        for line in self:
            if not line.week_day and not line.date_overwrite:
                raise UserError(
                    _("You have to set the week day " "or the date overwrite")
                )
            if line.week_day and line.date_overwrite:
                raise UserError(
                    _(
                        "You cannot set a week day and a date "
                        "overwrite in the same time."
                    )
                )

    @api.model
    def create_daily_plan(self, today_overwrite=None):
        today_str = today_overwrite or fields.Date.today()
        daily_plans = self.search([("next_execution", "=", today_str)])

        make_plan_wizard = self.env["round.wizard.makeplan"]

        for daily_plan in daily_plans:
            wizard = make_plan_wizard.create(
                {
                    "version_id": daily_plan.version_id.id,
                    "tag_ids": [(6, 0, daily_plan.tag_ids.ids)],
                    "execution_date": today_str,
                    "assign_moves": self.env.context.get("assign_moves", True),
                }
            )
            wizard.confirm()

            if daily_plan.date_overwrite:
                daily_plan.active = False
            else:
                execution_date = fields.Date.from_string(today_str)
                next_execution = execution_date + relativedelta(days=7)
                next_execution_str = fields.Date.to_string(next_execution)

                daily_plan.next_execution = next_execution_str
