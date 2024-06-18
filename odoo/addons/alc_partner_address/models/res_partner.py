# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields

from odoo.addons.base.models.res_partner import Partner as BasePartner


class ResPartner(BasePartner):
    type_delivery = fields.Boolean(
        "Is Also Delivery",
        copy=False,
        help="Allow to mark an invoice address and also delivery address",
    )
    type_name = fields.Char("Address Type Name", compute="_compute_type_name")

    @api.depends("type", "type_delivery")
    def _compute_type_name(self):
        for partner in self:
            name = False
            if partner.type == "invoice" and partner.type_delivery:
                name = _("Invoice and delivery")
            elif partner.type:
                name = dict(self.fields_get(["type"])["type"]["selection"])[
                    partner.type
                ]
            partner.type_name = name

    def address_get(self, adr_pref=None):
        """Copy of default method.

        Changes:
        * Do not use the 'contact' partner as a default address, return self
            In standard, if an address for a given type is not found, any
            contact is returned instead of current partner
        * Check field type_delivery
            Allow an address to be both invoice and delivery. As in standard,
            the search is performed on children and then on children of the
            commercial entity, we do not want to catch a delivery address of
            another child of the commercial entity
        """
        adr_pref = set(adr_pref or [])
        result = {}
        visited = set()
        for partner in self:
            current_partner = partner
            while current_partner:
                to_scan = [current_partner]
                # Scan descendants, DFS
                while to_scan:
                    record = to_scan.pop(0)
                    visited.add(record)
                    # jbaudoux: add 'invoice and delivery' in search
                    rtypes = [record.type]
                    if rtypes == ["invoice"] and record.type_delivery:
                        rtypes = ["invoice", "delivery"]
                    for rtype in rtypes:
                        if rtype in adr_pref and not result.get(rtype):
                            result[rtype] = record.id
                        if len(result) == len(adr_pref):
                            return result
                    # jbaudoux: end of change
                    to_scan = [
                        c
                        for c in record.child_ids
                        if c not in visited
                        if not c.is_company
                    ] + to_scan

                # Continue scanning at ancestor if current_partner is not a
                # commercial entity
                if current_partner.is_company or not current_partner.parent_id:
                    break
                current_partner = current_partner.parent_id

        # jbaudoux: remove partner of type 'contact' as default, use self
        for adr_type in adr_pref:
            result[adr_type] = result.get(adr_type) or self.id
        return result
