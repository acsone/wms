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
        partner_identification_xpaths = party_node.xpath(
            "cac:PartyIdentification/cbc:ID", namespaces=ns
        )
        for identification_xpath in partner_identification_xpaths:
            is_vat = "VAT" in identification_xpath.attrib.get("schemeName").upper()
            if not is_vat:
                continue
            value = identification_xpath.text
            if value:
                res["vat"] = value
                break
        return res
