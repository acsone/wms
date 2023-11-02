# Copyright 2023 ACSONE SA/NV
# License Other proprietary
from odoo import api

from odoo.addons.account_intrastat.models.account_intrastat_report import (
    IntrastatReportCustomHandler as IntrastatBase,
)


class IntrastatReportCustomHandler(IntrastatBase):
    @api.model
    def _fill_missing_values(self, vals_list):
        """
        Fill in the weight if it is <= 0.

        This was the code in v10.

        # TODO: Maybe something more clever that fill it in on category level.
        """
        res = super()._fill_missing_values(vals_list)
        for vals in res:
            if "weight" in vals and vals.get("weight") <= 0:
                vals["weight"] = 0.01
        return res
