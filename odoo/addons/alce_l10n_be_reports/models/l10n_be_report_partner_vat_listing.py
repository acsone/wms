# Copyright 2021 ACSONE SA/NV

from odoo import api, models


class ReportL10nBePartnerVatListing(models.AbstractModel):

    _inherit = "l10n.be.report.partner.vat.listing"

    @api.model
    def get_lines(self, context_id, line_id=None):
        return super(
            ReportL10nBePartnerVatListing, self.with_context(active_test=False)
        ).get_lines(context_id=context_id, line_id=line_id)
