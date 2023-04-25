# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.models.res_partner import Partner as BasePartner


class ResPartner(BasePartner):
    def _commercial_fields(self):
        """Cancel propagation of the field ref to children.

        This changes the default behavior of the module base_partner_sequence,
        """
        res = super()._commercial_fields()
        if "ref" in res:
            res.remove("ref")
        return res

    def _needs_ref(self, vals=None):
        """Generate a unique ref for addresses and contacts.

        This changes the default behavior of the module base_partner_sequence.
        """
        res = super()._needs_ref(vals)
        if vals and vals.get("parent_id"):
            return True
        return res
