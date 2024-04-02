# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.stock_release_channel_plan.wizards.launch_plan import (
    StockReleaseChannelPlanWizardLaunch as StockReleaseChannelPlanWizardLaunchBase,
)


class StockReleaseChannelPlanWizardLaunch(StockReleaseChannelPlanWizardLaunchBase):
    def action_launch(self):
        self.ensure_one()
        action = super().action_launch()
        action["context"] = {
            "search_default_filter_open": True,
            "search_default_filter_locked": True,
            "search_default_filter_delivering": True,
        }
        return action
