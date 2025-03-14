# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.osv import expression


class LoyaltyProgram(models.Model):

    _inherit = "loyalty.program"

    def _get_partners_for_rfa(self):
        partner_domains = []
        rfa_programs = self.env["loyalty.program"].search(
            [("program_type", "=", "year_end_rebate")]
        )
        if rfa_programs.partner_ids:
            partner_domains.append([("id", "in", rfa_programs.partner_ids.ids)])
        for program in rfa_programs:
            if program.partner_domain and program.partner_domain != "[]":
                partner_domains.append(program._get_eval_partner_domain())
        if not partner_domains:
            return self.env["res.partner"].search([])
        domain = expression.OR(partner_domains)
        return self.env["res.partner"].search(domain)

    def _update_loyalty_points(self, touched_products, retroactive_date):
        for program in self:
            partners = program._get_partners_for_rfa()
            sql = """
                SELECT
                    so.id
                FROM
                    sale_order so,
                    sale_order_line sol
                WHERE
                    so.state in ('sale', 'done')
                    AND so.partner_id IN %s
                    AND sol.order_id = so.id
                    AND sol.product_id IN %s
                    AND so.date_order >= %s
            """
            params = [
                tuple(partners.ids),
                tuple(touched_products.ids),
                retroactive_date,
            ]
            if program.date_from:
                sql += " AND so.date_order >= %s"
                params.append(program.date_from)
            if program.date_to:
                sql += " AND so.date_order <= %s"
                params.append(program.date_to)
            self.env.cr.execute(sql, params)
            orders = self.env["sale.order"].browse(
                [r[0] for r in self.env.cr.fetchall()]
            )
            orders._delay_recompute_rfa(self)

    def action_launch_rfa_updater(self):
        updater_wizard = self.env["alc.loyalty.rule.updater"].create(
            {"loyalty_program_id": self.id}
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "alc.loyalty.rule.updater",
            "res_id": updater_wizard.id,
            "view_mode": "form",
            "target": "new",
            "name": _("Update Loyalty Rule %(name)s", name=self.name),
            "context": dict(self.env.context, default_retroactive=True),
        }
