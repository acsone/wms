# Copyright 2024 ACSONE SA/NV
# License Other proprietary
from odoo import _

from odoo.addons.account_followup.models.account_followup_report import (
    AccountFollowupReport as AccountFollowupReportBase,
)


class AccountFollowupReport(AccountFollowupReportBase):
    def _get_followup_report_lines(self, options):
        lines = super()._get_followup_report_lines(options=options)

        for line in lines:
            if "columns" in line:
                line["columns"].pop(2)
                if "class" not in line or line["class"] != "total":
                    line["columns"][2]["name"] = ""
        return lines

    def _get_followup_report_columns_name(self):
        """Return the name of the columns of the follow-ups report."""
        names = super()._get_followup_report_columns_name()
        result_names = names.copy()
        # TODO: This should be removed as 16.0 current branch includes this
        result_names[0] = {
            "name": _("Reference"),
            "style": "text-align:center; white-space:nowrap;",
        }
        result_names.pop(3)
        result_names[3]["name"] = ""
        # result_names.pop(3)
        return result_names
