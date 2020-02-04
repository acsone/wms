# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.model
    def _ubl_get_party_identification(self, commercial_partner):
        """
            Should return a dict with key=SchemeName, value=Identifier
        """
        if not commercial_partner.vat:
            raise ValidationError(
                _(
                    "No VAT defined on the supplier.\n"
                    "VAT is required to identy the partner into the UBL"
                    "document"
                )
            )
        return {"BE:VAT": commercial_partner.vat}

    @api.model
    def _ubl_add_tax_category(
        self, tax, parent_node, ns, node_name='TaxCategory', version='2.1'
    ):
        """
        We don't provides tax info...
        """

    @api.multi
    def _ubl_add_order_line(
        self, parent_node, oline, line_number, ns, version='2.1'
    ):
        """
        Overrides to use the po line id as identifier
        """
        return super(PurchaseOrder, self)._ubl_add_order_line(
            parent_node, oline, oline.id, ns, version=version
        )

    @api.multi
    def _generate_ubl_order_document(self):
        self.ensure_one()
        return self.generate_ubl_xml_string("order", version="2.2")
