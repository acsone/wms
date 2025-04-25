from odoo import _, api, fields, models


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    rules_count = fields.Integer(
        compute="_compute_rule_count", string="Number of Rules"
    )

    @api.depends("rule_ids")
    def _compute_rule_count(self):
        for program in self:
            program.rules_count = len(program.rule_ids)

    def action_open_conditional_rules(self):
        self.ensure_one()

        return {
            "name": _("Loyalty Rules"),
            "type": "ir.actions.act_window",
            "res_model": "loyalty.rule",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [("program_id", "=", self.id)],
            "context": {"default_program_id": self.id},
            "target": "current",
        }
