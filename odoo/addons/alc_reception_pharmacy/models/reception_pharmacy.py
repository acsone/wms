# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.queue_job.job import identity_exact

from .reception_pharmacy_line import ReceptionPharmacyLine


class ReceptionPharmacy(models.Model):
    _name = "reception.pharmacy"
    _rec_name = "date"
    _description = "Reception pharmacy"

    date = fields.Datetime(default=lambda self: fields.Datetime.now(), copy=False)
    product_id = fields.Many2one[ProductProduct](
        string="Product",
        default=lambda self: self.env.ref(
            "alc_reception_pharmacy.product_colis_souverain"
        ),
        required=True,
        domain=lambda s: s._domain_product_id(),
    )
    line_ids = fields.One2many[ReceptionPharmacyLine](
        inverse_name="wizard_id",
        string="Lines",
        states={"done": [("readonly", True)]},
    )
    state = fields.Selection(
        [("draft", "New"), ("done", "Done")],
        compute="_compute_state",
        store=True,
        copy=False,
        readonly=True,
        default="draft",
    )

    @api.depends("line_ids.state")
    def _compute_state(self):
        for reception in self:
            # If no lines have been added yet or if one of them is 'draft'
            if not (reception.line_ids) or any(
                line.state == "draft" for line in reception.line_ids
            ):
                reception.state = "draft"
            else:
                reception.state = "done"

    @api.model
    def _domain_product_id(self):
        return [
            (
                "categ_id",
                "=",
                self.env.ref(
                    "alc_product_category_data.product_categ_colis_souverain"
                ).id,
            )
        ]

    def validate(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Please insert at least one line"))
        line_by_partner = self.line_ids.filtered(
            lambda s: s.state == "draft"
        ).partition("partner_shipping_id")
        for partner, lines in line_by_partner.items():
            # we delay the validation of the lines to minimize the risk of
            # deadlocks. The validation is done by partner to try to group
            # the lines that should go to the same picking.
            job_description = _("Reception pharmacy for %(name)s", name=partner.name)
            lines.with_delay(
                description=job_description, identity_key=identity_exact
            ).validate()
        self.env.user.notify_info(
            _("Reception pharmacy : lines are validated in background")
        )
