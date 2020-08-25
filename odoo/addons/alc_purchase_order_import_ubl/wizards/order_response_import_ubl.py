# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class OrderResponseImport(models.TransientModel):
    _inherit = "order.response.import"

    @api.model
    def ubl_parse_party(self, party_node, ns):
        """
        Uses the VAT number provided by the PartyIdentification defined in
        alc_purchase_order_ubl
        """
        res = super(OrderResponseImport, self).ubl_parse_party(party_node, ns)
        partner_identification_xpath = party_node.xpath(
            "cac:PartyIdentification/cbc:ID", namespaces=ns
        )
        if not partner_identification_xpath or not partner_identification_xpath[0].text:
            return res
        is_vat = "VAT" in partner_identification_xpath[0].attrib.get("schemeName")
        if not is_vat:
            return res
        res["vat"] = partner_identification_xpath[0].text
        return res
