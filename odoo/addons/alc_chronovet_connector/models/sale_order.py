# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import dateutil

import pytz
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND

TITLE_XML_ID_BY_CHRONOVET_KEY = {
    "mr": "base.res_partner_title_mister",
    "ms": "base.res_partner_title_madam",
}


class SaleOrder(models.Model):

    _inherit = "sale.order"

    chronovet_ref = fields.Char(string="Reference Chronovet", copy=False, index=True)
    sale_channel = fields.Selection(selection_add=[("chronovet", "Chronovet")])

    _sql_constraints = [
        (
            "chronovet_ref_unique",
            "EXCLUDE (chronovet_ref WITH =) WHERE (chronovet_ref <> '' or chronovet_ref is not null)",
            _("This chronovet reference already exists"),
        )
    ]

    @api.model
    def _create_from_chonovet(self, data, chronovet_backend):
        """ Create a sale order with data coming from chronovet
        """
        order_data = self._parse_chronovet_order(data, chronovet_backend)
        order = (
            self.env["sale.order"]
            .with_context(mail_auto_subscribe_no_notify=True)
            .create(order_data)
        )
        return order

    @api.model
    def _parse_chronovet_order(self, data, chronovet_backend):
        order_data = {}
        # we create all the orders with the VET as final customer
        # At the end of the process and after the onchange call, the partner_id
        # will be replaced by the final customer
        partner_vet = self._get_partner_by_ref(data["customer_ref"])
        # get the parther and play onchange to get shipping,
        order_data["partner_id"] = partner_vet.id
        order_data["chronovet_ref"] = data["id"]
        order_data["sale_channel"] = "chronovet"
        order_data["date_order"] = self._parse_datetime_to_utc(data["date"])
        order_data["team_id"] = chronovet_backend.sale_team_id.id
        # invvoice, payment_term, pricelist, carrier_id, team
        updated_data = self.play_onchanges(order_data, order_data.keys())
        order_data.update(updated_data)

        # replace partner by the final customer
        order_data["partner_id"] = self._get_final_chonovet_recipient(data).id
        order_data["pricelist_id"] = chronovet_backend.pricelist_id.id
        order_data["order_line"] = [
            (0, 0, line_info)
            for line_info in self._parse_chronovet_order_line(data, chronovet_backend)
        ]
        # TODO PAYMENT MODE WITH SALE_AUTOMATIC_WORKFLOW
        return order_data

    @api.model
    def _parse_chronovet_order_line(self, data, chronovet_backend):
        lines_data = data["lines"]
        skus = [line["sku"] for line in lines_data]
        domain = chronovet_backend.product_assortment_id._get_eval_domain()
        domain = AND([domain, [("default_code", "in", skus)]])
        products = self.env["product.product"].search(domain)
        product_by_sku = {p.default_code: p for p in products}
        unknown_skus = set(skus).difference(set(product_by_sku.keys()))
        if unknown_skus:
            raise ValidationError(_("Unknowns SKU(s): %s " ", ".join(unknown_skus)))
        result = []
        for line_data in lines_data:
            sol = {}
            product = product_by_sku[line_data["sku"]]
            sol["product_id"] = product.id
            sol["name"] = product.name
            sol["product_uom"] = product.uom_id.id
            sol["product_uom_qty"] = line.pop("quantity")
            sol["chronovet_ref"] = line.pop("line_id")
            result.append(sol)
        return result

    @api.model
    def _get_final_chonovet_recipient(self, data):
        customer_info = data["recipient"]
        chronovet_ref = "CHRONOVET_%s" % customer_info["id"]
        partner = self._get_partner_by_ref(chronovet_ref, raise_if_notfound=False)
        if partner:
            # DO WE HAVE TO UPDATE ADDRESS INFO?
            return partner
        name = customer_info["first_name"]
        last_name = customer_info.get("last_name")
        if last_name:
            name = "%s %s" % (name, last_name)
        title = customer_info.get("title")
        if title:
            title = self.env.ref(TITLE_XML_ID_BY_CHRONOVET_KEY[title]).id
        return self.env["res.partner"].create(
            {
                "name": name,
                "title": title,
                "email": customer_info.get("email"),
                "street": customer_info.get("street"),
                "street2": customer_info.get("street2"),
                "zip": customer_info.get("zip"),
                "city": customer_info.get("city"),
                "phone": customer_info.get("phone"),
                "mobile": customer_info.get("mobile"),
                "category_id": [
                    (
                        4,
                        self.env.ref(
                            "alc_chronovet_connector.res_partner_category_chronovet_customer"
                        ).id,
                    )
                ],
                "alcyon_category_id": self.env.ref(
                    "specific_partner.partner_category_student"
                ).id,
                "ref": chronovet_ref,
            }
        )

    @api.model
    def _get_partner_by_ref(self, ref, raise_if_notfound=True):
        partner = self.env["res.partner"].search(
            [("ref", "=", ref)],
            # For main partner and contacts having the same ref, the sort
            # order forces for the main contact to be returned.
            # Which is the one with parent_id set at Null.
            order="parent_id desc",
            limit=1,
        )
        if not partner and raise_if_notfound:
            raise ValidationError(_("No match found for customer_id: %s") % ref)
        return partner

    @api.model
    def _parse_datetime_to_utc(self, dt):
        """Parse an iso8601-formatted date string and returns
        a DT into UTC without TZ info as string
        """
        dt = dateutil.parser.parse(dt)
        dt = dt.astimezone(pytz.timezone("UTC"))
        return fields.Datetime.to_string(dt)
