# Copyright 2018 Okia SPRL
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api
from odoo.exceptions import UserError

from odoo.addons.sale_cancel_remaining.wizards.cancel_remaining_wizard import (
    CancelRemainingWizard as CancelRemainingWizardBase,
)


class CancelRemainingWizard(CancelRemainingWizardBase):
    @api.model
    def _check_pickings_to_cancel(self, line):
        res = super()._check_pickings_to_cancel(line)
        pickings_to_cancel = self._get_pickings_to_cancel(line)
        if any(pickings_to_cancel.mapped("printed")):
            raise UserError(
                _("You cannot cancel a quantity that is part " "of a started picking")
            )
        return res
