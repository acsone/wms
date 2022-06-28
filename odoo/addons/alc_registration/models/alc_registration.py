# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base.res.res_partner import FormatAddress


class AlcRegistration(FormatAddress, models.Model):

    _name = "alc.registration"
    _description = "Partner Registration"

    active = fields.Boolean("Active", default=True)
    partner_id = fields.Many2one("res.partner", string="Created Partner", readonly=True)

    # we want a multiselect with "Livestock", "Equine", "Pets", "Exotic Pets"
    # it might become a m2m if there's a real usage for it
    clientele = fields.Char(string="Clientele", required=True)
    occupation = fields.Selection(
        string="Occupation",
        required=True,
        selection=[
            ("veterinary", "Veterinary"),
            ("assistant", "Veterinary Assistant"),
            ("student", "Student"),
            ("pharmacist", "Pharmacist"),
            ("wholesaler", "Wholesaler"),
            ("supplier", "Supplier"),
        ],
    )

    name = fields.Char()
    title = fields.Many2one("res.partner.title")
    company_name = fields.Char()
    opt_out = fields.Boolean(string="Opt-Out")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    zip = fields.Char("Zip", change_default=True)
    city = fields.Char("City")
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    country_name = fields.Char(string="Country Name")
    phone = fields.Char("Phone")
    fax = fields.Char("Fax")
    mobile = fields.Char("Mobile")
    email = fields.Char("Email")

    comment = fields.Text()

    vat = fields.Char(string="TIN", help="Tax Identification Number.")

    # might be moved into an override? -> pharmacy
    apb_authorization = fields.Char(string="Authorization/APB")
    # might be moved into an override? -> veterinary
    vet_depot_number = fields.Char(string="Depot number")
    vet_subscription_number = fields.Char(string="Subscription number")
    # might be moved into an override? -> partner_type
    partner_type = fields.Selection(  # replaces alcyon_category_id
        string="Alcyon Partner Category",
        required=True,
        selection=[
            ("guest", "Guest"),  # lowest access rights
            ("misc", "Miscellaneous"),
            ("student_like", "Student and similar"),
            ("shareholder", "Shareholder"),
            ("veterinary", "Veterinary"),
            ("wholesaler_pharmacy", "Pharmacy Wholesaler"),
            ("wholesaler_veterinary", "Veterinary Wholesaler"),
            ("equipment_only", "Equipment Only"),
            ("food_only", "Food Only"),
            ("export_customer", "Export Customer"),
            ("export_meds", "Export Medicine"),
            ("supplier", "Suppliers"),
        ],
        default="misc",
    )

    state = fields.Selection(
        string="Status",
        selection=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        compute="_compute_state",
    )

    @api.depends("partner_id", "active")
    def _compute_state(self):
        for registration in self:
            state = registration.partner_id and "accepted"
            state = state or ("pending" if registration.active else "rejected")
            registration.state = state

    @api.model
    def _creation_fields(self):
        return [
            "name",
            "title",
            "partner_type",
            "company_name",
            "street",
            "street2",
            "zip",
            "city",
            "country_id",
            "fax",
            "phone",
            "mobile",
            "email",
            "vat",
            "vet_depot_number",
            "vet_subscription_number",
            "apb_authorization",
            "opt_out",
            "comment",
        ]

    def create_partners(self):
        fields_to_sync = self._creation_fields()
        partners = self.env["res.partner"]
        for contact in self.filtered(lambda c: not c.partner_id):
            g = lambda v, f: v.id if self._fields[f].relational else v
            vals = {f: g(contact[f], f) for f in fields_to_sync}
            contact.partner_id = partners.create(vals)
            partners |= contact.partner_id
        return partners

    def action_create_partners(self):
        partners = self.create_partners()
        if not partners:
            raise ValidationError(_("No new partners."))
        window_action = self.env.ref("contacts.action_contacts").read()[0]
        window_action["target"] = "current"
        window_action["view_mode"] = "form" if len(partners) == 1 else "tree"
        if len(partners) == 1:
            window_action["res_id"] = partners.id
            window_action["views"] = [(False, "form")]
        else:
            window_action["views"] = [(False, "tree"), (False, "form")]
            window_action["domain"] = [("id", "in", partners.ids)]
        return window_action

    def action_archive(self):
        rejected = self.filtered(lambda c: not c.partner_id)
        if not rejected:
            raise ValidationError(_("Registration has already been accepted."))
        rejected.write({"active": False})
        # redirect to standard view to continue the work
        window_action = self.env.ref("alc_registration.alc_registration_act_window")
        return window_action.read()[0]

    def action_reset_to_pending(self):
        to_reset = self.filtered(lambda c: not c.partner_id and not c.active)
        if not to_reset:
            raise ValidationError(_("No Registration to reset."))
        to_reset.write({"active": True})
        window_action = self.env.ref("alc_registration.alc_registration_act_window")
        window_action = window_action.read()[0]
        window_action["target"] = "current"
        window_action["view_mode"] = "form" if len(to_reset) == 1 else "tree"
        if len(to_reset) == 1:
            window_action["res_id"] = to_reset.id
            window_action["views"] = [(False, "form")]
        else:
            window_action["views"] = [(False, "tree"), (False, "form")]
            window_action["domain"] = [("id", "in", to_reset.ids)]
        return window_action
