# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductPartnerType(models.AbstractModel):
    """These functions need to be exposed on product.product (for sale_exception).

    but also on product.template if we want to keep the abstraction consistent.
    """

    _name = "product.partner_type"
    _description = "Type of customer from Alcyon business point of vue"

    def get_allowed_partner_types(self):
        """Returns the set of all partner types allowed to interact with the product."""
        self.ensure_one()
        if not self.categ_id:
            return set()
        partner_types = self.get_all_partner_types()
        partner_types = self._filter_partner_types_food(partner_types)
        partner_types = self._filter_partner_types_equipement(partner_types)
        partner_types = self._filter_partner_types_meds(partner_types)
        partner_types = self._filter_partner_types_veterinary(partner_types)
        partner_types = self._filter_partner_types_belgium(partner_types)
        partner_types = self._filter_partner_types_human(partner_types)
        partner_types = self._filter_partner_types_import(partner_types)
        partner_types = self._filter_partner_types_vt_be(partner_types)
        partner_types = self._filter_partner_types_narcotic_reg(partner_types, True)
        partner_types = self._filter_partner_types_narcotic_vet(partner_types, True)
        partner_types = self._filter_partner_types_psychotropic(partner_types)
        return partner_types

    def _filter_partner_types_food(self, partner_types):
        if self.is_food:
            partner_types -= {"equipment_only", "guest"}
        return partner_types

    def _filter_partner_types_equipement(self, partner_types):
        if self.is_equipment:
            partner_types -= {"food_only"}
        return partner_types

    def _filter_partner_types_meds(self, partner_types, strict=False):
        if self.is_meds:
            partner_types -= {"equipment_only", "food_only", "guest"}
            if strict:
                partner_types -= {"misc"}
        return partner_types

    def _filter_partner_types_human(self, partner_types):
        if self.is_human:
            partner_types &= {"veterinary", "supplier", "shareholder"}
        return partner_types

    def _filter_partner_types_import(self, partner_types):
        if self.is_import:
            partner_types -= {"misc", "student_like", "export_customer", "export_meds"}
        return partner_types

    def _filter_partner_types_vt_be(self, partner_types):
        if self.is_vt_be:
            partner_types -= {"misc", "student_like", "export_customer"}
        return partner_types

    def _filter_partner_types_narcotic_reg(self, partner_types, strict=False):
        if self.is_narcotic_reg:
            allowed = {"supplier", "wholesaler_pharmacy", "wholesaler_veterinary"}
            partner_types = set() if strict else (partner_types & allowed)
        return partner_types

    def _filter_partner_types_narcotic_vet(self, partner_types, strict=False):
        if self.is_narcotic_vet:
            allowed = {"supplier", "wholesaler_pharmacy", "wholesaler_veterinary"}
            partner_types &= {"veterinary"} if strict else allowed
        return partner_types

    def _filter_partner_types_psychotropic(self, partner_types):
        if self.is_psychotropic:
            partner_types -= {"misc", "student_like", "export_customer", "export_meds"}
        return partner_types

    def _filter_partner_types_veterinary(self, partner_types):
        if self.veterinary_only:
            partner_types -= {
                "equipment_only",
                "export_customer",
                "student_like",
                "wholesaler_pharmacy",
                "misc",
                "food_only",
            }
        return partner_types

    def _filter_partner_types_belgium(self, partner_types):
        if self.belgium_only:
            partner_types -= {"export_customer", "export_meds"}
        return partner_types

    @api.model
    def get_all_partner_types(self):
        return set(self.env["res.partner"]._get_partner_types())

    @api.model
    def get_partner_type_domain(self, partner):
        """Domain restricting products to the given partner's type."""
        partner.ensure_one()
        if partner.partner_type == "supplier":
            domain = [("supplier_id", "=", partner.id)]
        else:
            domain = [("allowed_partner_types", "like", partner.partner_type)]
        return domain
