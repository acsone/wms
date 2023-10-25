# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import OR

from odoo.addons.base.models.res_country import Country, CountryState
from odoo.addons.base.models.res_partner import Partner, PartnerTitle


class AlcRegistration(models.Model):

    _name = "alc.registration"
    _inherit = "format.address.mixin"  # nosemgrep: is-old-style-inheritance
    _description = "Partner Registration"

    active = fields.Boolean("Active", default=True)
    partner_id = fields.Many2one[Partner](string="Created Partner", readonly=True)

    # we want a multiselect with "Livestock", "Equine", "Pets", "Exotic Pets"
    # it might become a m2m if there's a real usage for it
    # if refactor is needed as a M2M we could directly use res.partner.category
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
    title = fields.Many2one[PartnerTitle]()
    company_name = fields.Char()
    opt_out = fields.Boolean(string="Opt-Out")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    zip = fields.Char("Zip", change_default=True)
    city = fields.Char("City")
    state_id = fields.Many2one[CountryState](string="State")
    country_id = fields.Many2one[Country](string="Country")
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

    similar_partner_ids = fields.One2many[Partner](
        compute="_compute_similar_partner_ids",
        string="Similar Partners",
        help="Restricted to 10 parnters, use the action to show all potential matches.",
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

    def _get_partner_categories_from_clientele(self):
        categories = []
        mapping = {
            "livestock": "alc_partner_category.grands_animaux",
            "pet": "alc_partner_category.petits_animaux",
            "equine": "alc_partner_category.equins",
            "exotic": "alc_partner_category.nac",
        }
        for key, xml_id in mapping.items():
            if key in self.clientele:
                categories.append(self.env.ref(xml_id).id)
        return categories

    def _get_partner_vals(self):
        self.ensure_one()
        fields_to_sync = self._creation_fields()

        def g(v, f):
            return v.id if self._fields[f].relational else v

        vals = {f: g(self[f], f) for f in fields_to_sync}
        if vals.get("company_name"):
            vals["suite"] = vals["name"]
            vals["name"] = vals.pop("company_name")
        categories = self._get_partner_categories_from_clientele()
        if categories:
            vals["category_id"] = [(6, 0, categories)]
        return vals

    def create_partners(self):
        partners = self.env["res.partner"]
        for contact in self.filtered(lambda c: not c.partner_id):
            contact.partner_id = partners.create(contact._get_partner_vals())
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

    @api.model
    def _get_similarity_fields(self):
        return ["email", "vat", "mobile", "phone", "fax", "company_name", "name"]

    def _get_similarity_domain(self):
        self.ensure_one()
        domains = []
        for field in self._get_similarity_fields():
            if self[field]:
                domains.append([(field, "ilike", self[field])])
        return OR(domains)

    def action_show_similar(self):
        self.ensure_one()
        tree_view = self.env.ref("alc_registration.res_partner_similar_tree_view")
        return {
            "type": "ir.actions.act_window",
            "name": _("Similar Partners"),
            "res_model": "res.partner",
            "domain": self._get_similarity_domain(),
            "view_type": "form",
            "view_mode": "tree,form",
            "context": self.env.context,
            "target": "current",
            "views": [(tree_view.id, "tree")],
        }

    @api.depends(lambda s: s._get_similarity_fields())
    def _compute_similar_partner_ids(self):
        for partner in self:
            partner_domain = partner._get_similarity_domain()
            partners = self.env["res.partner"].search(partner_domain, limit=10)
            partner.similar_partner_ids = partners
