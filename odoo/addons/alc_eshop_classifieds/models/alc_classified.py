# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from slugify import slugify

from odoo import api, fields, models


class AlcClassified(models.Model):
    """Model for classified advertisement. The partner is the classified owner.
       He can create new classifieds, and submit them for publication.
       An Odoo user can then approve or reject them(with motivation).
       At any moment a user can unpublish his own classified, either by deletion
       or by resetting the state to draft, or to pending so that the new version
       can be approved.
    """

    _name = "alc.classified"
    _description = "Classified Advertising"
    _inherit = ["mixin.past", "mixin.file.id", "mail.thread"]
    _order = "sequence,id"

    sequence = fields.Integer("Sequence")
    date_start = fields.Date(
        "Start Date",
        required=True,
        default=lambda a: a.default_today(),
        track_visibility="onchange",
    )
    date_end = fields.Date(
        "End Date",
        required=True,
        default=lambda a: a.default_in_one_week(),
        track_visibility="onchange",
    )
    name = fields.Char(string="Title", required=True, track_visibility="onchange")
    body = fields.Text(string="Content", required=True, track_visibility="onchange")
    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True, index=True, ondelete="cascade",
    )
    rejection_reason = fields.Char(string="Rejection", track_visibility="onchange")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("cancel", "Rejected"),
            ("published", "Published"),
            ("pending", "Approval Pending"),
        ],
        string="Status",
        track_visibility="onchange",
        copy=False,
        default="draft",
        index=True,
        readonly=True,
        required=True,
    )
    category = fields.Selection(
        [
            ("animals", "Animals"),
            ("clientele", "Clientele"),
            ("employment", "Employment"),
            ("equipment", "Equipment"),
            ("misc", "Miscellaneous"),
        ],
        string="Category",
        track_visibility="onchange",
        index=True,
        required=True,
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        required=True,
        track_visibility="onchange",
        domain=lambda self: [("country_id", "=", self.env.ref("base.be").id)],
    )
    email = fields.Char("Email", required=True, track_visibility="onchange")
    phone = fields.Char("Phone", required=True, track_visibility="onchange")
    contact = fields.Char("Contact", required=True, track_visibility="onchange")

    @api.model
    def default_today(self):
        return self.env.context.get("date", fields.Date.context_today(self))

    @api.model
    def default_in_one_week(self):
        today_str = self.default_today()
        today = fields.Date.from_string(today_str)
        return fields.Date.to_string(today + relativedelta(days=7))

    @api.model
    def _get_filename(self, name):
        return slugify(name)[:26]  # limit to 30 with extension

    # user methods (i.e. the partner_id) ###

    def submit(self):
        return self.write({"state": "pending"})

    def update_set_to_draft(self, vals):
        vals["state"] = "draft"
        return self.write(vals)

    def update_set_to_pending(self, vals):
        vals["state"] = "pending"
        return self.write(vals)

    # manager methods ###

    def confirm(self):
        return self.write({"rejection_reason": False, "state": "published"})

    def reject(self, reason=False):
        return self.write({"rejection_reason": reason, "state": "cancel"})

    def action_reject(self):
        self.ensure_one()
        wizard_model = self.env["alc.classified.wizard.rejection"]
        action_ref = "alc_eshop_classifieds.alc_classified_wizard_rejection_act_window"
        window_action = self.env.ref(action_ref).read()[0]
        wizard = wizard_model.create({"alc_classified_id": self.id})
        window_action["res_id"] = wizard.id
        return window_action
