# Copyright 2019 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.alc_sale_exception.models import sale_order_line


class SaleOrderLine(sale_order_line.SaleOrderLine):
    def validate_no_food(self):
        all_types = self.product_id.get_all_partner_types()
        allowed_types = self.product_id._filter_partner_types_food(all_types)
        return self.order_id.partner_id.partner_type not in allowed_types

    def validate_no_medoc(self):
        all_types = self.product_id.get_all_partner_types()
        allowed_types = self.product_id._filter_partner_types_meds(all_types, True)
        return self.order_id.partner_id.partner_type not in allowed_types

    def validate_no_medoc_cascade_import(self):
        all_types = self.product_id.get_all_partner_types()
        allowed_types = self.product_id._filter_partner_types_import(all_types)
        return self.order_id.partner_id.partner_type not in allowed_types

    def validate_no_medoc_veterinary_belge(self):
        all_types = self.product_id.get_all_partner_types()
        allowed_types = self.product_id._filter_partner_types_vt_be(all_types)
        return self.order_id.partner_id.partner_type not in allowed_types

    def validate_no_medoc_human(self):
        all_types = self.product_id.get_all_partner_types()
        allowed_types = self.product_id._filter_partner_types_human(all_types)
        return self.order_id.partner_id.partner_type not in allowed_types

    def validate_no_medoc_vet_stupefiant(self):
        all_types = self.product_id.get_all_partner_types()
        allowed_types = self.product_id._filter_partner_types_narcotic_reg(all_types)
        return self.order_id.partner_id.partner_type not in allowed_types

    def validate_no_medoc_vet_psychoIII(self):
        all_types = self.product_id.get_all_partner_types()
        allowed_types = self.product_id._filter_partner_types_psychotropic(all_types)
        return self.order_id.partner_id.partner_type not in allowed_types

    def validate_no_medoc_belgium_only(self):
        all_types = self.product_id.get_all_partner_types()
        allowed_types = self.product_id._filter_partner_types_belgium(all_types)
        return self.order_id.partner_id.partner_type not in allowed_types

    def validate_no_veterinary_product(self):
        """Disallow products which are only for veterinary."""
        all_types = self.product_id.get_all_partner_types()
        allowed_types = self.product_id._filter_partner_types_veterinary(all_types)
        return self.order_id.partner_id.partner_type not in allowed_types

    def validate_no_psychotropic_ordered_by_phone(self):
        """No psychotropic ordered on the phone."""
        return (
            self.product_id.is_psychotropic
            and self.order_id.sale_channel_id.code == "phone"
        )

    def validate_no_stupefiant_vet_by_phone(self):
        return (
            self.product_id.is_narcotic_vet
            and self.order_id.sale_channel_id.code == "phone"
        )

    # Warnings
    def warning_psychotropic(self):
        """Add warning for psychotropic product on sale order line."""
        return self.product_id.is_psychotropic

    def warning_stupefiant_vet(self):
        """Add warning for psychotropic product on sale order line."""
        return self.product_id.is_narcotic_vet

    def warning_cascade_importation(self):
        """Add a warning for cascade importation product."""
        return self.product_id.is_import

    def warning_human_medicine(self):
        """Add a warning for human medicine product."""
        return self.product_id.is_human
