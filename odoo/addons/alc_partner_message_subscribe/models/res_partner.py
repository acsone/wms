# Copyright 2023 ASCONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.models.res_partner import Partner as BasePartner


class ResPartner(BasePartner):
    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        """Add subtype to note automatically for partner."""
        # Get the id from "Note"
        subtype_note_id = self.env.ref("mail.mt_note")
        # Get default subtype item for partner
        partner_default_subtype_ids = self.env["mail.message.subtype"].search(
            [
                "|",
                ("res_model", "=", False),
                "&",
                ("res_model", "=", "res.partner"),
                ("default", "=", True),
            ]
        )
        partner_default_subtype_ids |= subtype_note_id
        if subtype_ids:
            subtype_ids += partner_default_subtype_ids.ids
        else:
            subtype_ids = partner_default_subtype_ids.ids
        return super().message_subscribe(
            partner_ids=partner_ids,
            subtype_ids=subtype_ids,
        )
