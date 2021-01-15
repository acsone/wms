# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import math
from collections import OrderedDict

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RoundInstance(models.Model):
    _inherit = "round.instance"

    @api.multi
    def print_cash_on_delivery_invoices(self):
        self.ensure_one()
        invoices = self.instance_customer_ids.mapped("cash_on_delivery_invoice_ids")
        if not invoices:
            raise UserError(_("No invoice to print"))
        invoices.filtered(lambda i: not i.sent).write({"sent": True})
        return self.env["report"].get_action(invoices, "account.report_invoice")

    @api.multi
    def print_delivery_round(self):
        self.ensure_one()

        return self.env["report"].get_action(
            self, "delivery_rounds.delivery_round_report"
        )

    @api.multi
    def get_time_leave_planned(self):
        self.ensure_one()

        if self.time_leave_planned <= 0:
            return ""

        pattern = "%02d:%02d"
        hour = math.floor(self.time_leave_planned)
        min_ = round((self.time_leave_planned % 1) * 60)
        if min_ == 60:
            min_ = 0
            hour += 1

        return pattern % (hour, min_)

    @api.multi
    def get_merged_shippings(self):
        self.ensure_one()

        shippings = self._get_sorted_shipping_ids()

        shipping_values = OrderedDict()
        for shipping in shippings:
            partner_value = shipping_values.get(shipping.partner_id, {})

            number_of_drug = partner_value.get("number_of_drug", 0)
            number_of_drug += shipping.number_of_drug
            item_number_of_drug = partner_value.get("item_number_of_drug", 0)
            item_number_of_drug += shipping.item_number_of_drug

            number_of_cold = partner_value.get("number_of_cold", 0)
            number_of_cold += shipping.number_of_cold
            item_number_of_cold = partner_value.get("item_number_of_cold", 0)
            item_number_of_cold += shipping.item_number_of_cold

            number_of_food = partner_value.get("number_of_food", 0)
            number_of_food += shipping.number_of_food
            item_number_of_food = partner_value.get("item_number_of_food", 0)
            item_number_of_food += shipping.item_number_of_food

            number_of_equipment = partner_value.get("number_of_equipment", 0)
            number_of_equipment += shipping.number_of_equipment
            item_number_of_equipment = partner_value.get("item_number_of_equipment", 0)
            item_number_of_equipment += shipping.item_number_of_equipment

            number_of_human_drug = partner_value.get("number_of_human_drug", 0)
            number_of_human_drug += shipping.number_of_human_drug
            item_number_of_human_drug = partner_value.get(
                "item_number_of_human_drug", 0
            )
            item_number_of_human_drug += shipping.item_number_of_human_drug

            number_total = partner_value.get("number_total", 0)
            number_total += shipping.number_total
            item_number_total = partner_value.get("item_number_total", 0)
            item_number_total += shipping.item_number_total

            note = partner_value.get("note", "")
            if shipping.partner_id.comment:
                note = shipping.partner_id.comment

            partner_value.update(
                {
                    "number_of_drug": number_of_drug,
                    "item_number_of_drug": item_number_of_drug,
                    "number_of_cold": number_of_cold,
                    "item_number_of_cold": item_number_of_cold,
                    "number_of_food": number_of_food,
                    "item_number_of_food": item_number_of_food,
                    "number_of_equipment": number_of_equipment,
                    "item_number_of_equipment": item_number_of_equipment,
                    "number_of_human_drug": number_of_human_drug,
                    "item_number_of_human_drug": item_number_of_human_drug,
                    "number_total": number_total,
                    "item_number_total": item_number_total,
                    "note": note,
                    "rank": shipping.rank,
                    "shipping": shipping,
                }
            )
            shipping_values[shipping.partner_id] = partner_value

        result = []
        for partner, values in shipping_values.iteritems():
            shipping_value = shipping_values.get(partner)
            if not shipping_value:
                continue

            # There is something very stupid in Odoo. If you want to display
            # the address of a partner with the tag <address t-field=.... />
            # you HAVE TO have at least one dot in the t-field
            # (eg: t-field="shipping.partner_id" and not t-field="partner")
            # It's why I append a shipping
            result.append((partner, shipping_value["shipping"], shipping_value))

        return result


class RoundInstanceCustomer(models.Model):
    _inherit = "round.instance.customer"

    cash_on_delivery_invoice_ids = fields.Many2many(
        "account.invoice",
        string="Invoices",
        compute="_compute_cash_on_delivery_invoice_ids",
        readonly=True,
    )
    has_cash_on_delivery_invoice = fields.Boolean(
        string="Has Invoices",
        compute="_compute_cash_on_delivery_invoice_ids",
        readonly=True,
    )

    @api.depends("picking_ids.cash_on_delivery_invoice_ids")
    def _compute_cash_on_delivery_invoice_ids(self):
        for rec in self:
            shippings = rec.picking_ids.filtered(
                lambda p: p.picking_type_code == "outgoing"
            )
            shippings_done = shippings.filtered(
                lambda shipping: shipping.state == "done"
            )
            rec.cash_on_delivery_invoice_ids = shippings_done.mapped(
                "cash_on_delivery_invoice_ids"
            )
            if rec.cash_on_delivery_invoice_ids:
                rec.has_cash_on_delivery_invoice = True

    def print_cash_on_delivery_invoices(self):
        self.ensure_one()
        invoices = self.cash_on_delivery_invoice_ids
        if not invoices:
            raise UserError(_("No invoice to print"))
        invoices.filtered(lambda i: not i.sent).write({"sent": True})
        return self.env["report"].get_action(invoices, "account.report_invoice")
