# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..models.alc_classified import AlcClassified


class AlcClassifiedWizardRejection(models.TransientModel):

    _name = "alc.classified.wizard.rejection"
    _description = "Wizard to Reject Classifieds."

    alc_classified_id = fields.Many2one[AlcClassified](
        string="Classified", required=True
    )
    name = fields.Char(related="alc_classified_id.name")
    reason = fields.Char(string="Rejection Reason")

    def execute(self):
        for wizard in self:
            wizard.alc_classified_id.reject(wizard.reason)
        return True
