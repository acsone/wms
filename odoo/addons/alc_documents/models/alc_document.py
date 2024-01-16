# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base.models.ir_attachment import IrAttachment
from odoo.addons.base.models.res_partner import Partner
from odoo.addons.sale_channel.models.sale_channel import SaleChannel


class AlcDocument(models.Model):
    """A document is a facade for an attachment, that can be computed 'on the fly'.

    So the idea is to have two types: one where we generate the attachment based on the
    document, and one where we have an attachment, and create the document to access it.
    """

    _name = "alc.document"
    _description = "Alcyon Document"
    _order = "is_null_document_date_start desc, document_date desc, type, name"

    attachment_id = fields.Many2one[IrAttachment](
        readonly=True, ondelete="cascade", index=True
    )
    compute = fields.Selection([], readonly=True)  # to extend
    res_model = fields.Char(related="attachment_id.res_model", readonly=True)
    document_date = fields.Datetime(
        compute="_compute_document_date", store=True, readonly=True
    )
    is_null_document_date_start = fields.Boolean(
        "The document date is null",
        compute="_compute_is_null_document_date_start",
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one[Partner](readonly=True, ondelete="cascade", index=True)
    sale_channel_id = fields.Many2one[SaleChannel](readonly=True)
    allowed_partner_types = fields.Char(
        string="Allowed Partner Types", readonly=True, index="trigram"
    )
    type = fields.Selection(
        selection=[
            ("order", "Order"),
            ("delivery_note", "Delivery Note"),
            ("invoice", "Invoice"),
            ("credit_note", "Credit Note"),
        ],
        readonly=True,
    )

    name = fields.Char(required=True, readonly=True)
    format = fields.Char(readonly=True)

    _sql_constraints = [
        (
            "attachment_uniq",
            "unique(attachment_id)",
            "There can be only one document per attachment.",
        ),
    ]

    def _ensure_data(self):
        self.ensure_one()
        if self.compute:
            getattr(self, f"_compute_data_{self.compute}")()

    def _get_data(self) -> bytes:
        """Get data in raw format.

        IOW the data is not  b64 encoded...
        """
        self._ensure_data()
        return self.attachment_id.raw or b""

    def _get_attachment(self):
        self.ensure_one()
        self._ensure_data()
        return self.attachment_id

    def compute_data(self):
        for document in self:
            if document.compute:
                getattr(document, f"_compute_data_{document.compute}")()

    @api.model
    def _get_watched_models(self):
        # each one should be in a separate module extending this function
        return ["sale.order", "account.move", "stock.picking"]

    @api.model
    def _get_prefixes(self):
        # each model should register its own prefixes in the corresponding module
        return ["cf", "CM", "fc", "nc", "NE"]

    @api.constrains("partner_id", "allowed_partner_types")
    def _partner_type_constraint(self):
        partner_types = self.env["res.partner"]._get_partner_types()
        for document in self:
            if document.partner_id:
                if document.allowed_partner_types:
                    raise ValidationError(
                        _("You cannot have a public document with a partner.")
                    )
            else:  # public document: should be accessible to some partner_types
                document_partner_types = document.allowed_partner_types.split(",")
                if not document_partner_types:
                    raise ValidationError(_("A public document should be accessible."))
                if not all(pt in partner_types for pt in document_partner_types):
                    raise ValidationError(_("All partner_types should be valid."))

    @api.constrains("compute", "attachment_id")
    def _constraint_compute_attachment(self):
        for document in self:
            if not document.compute and not document.attachment_id:
                msg = _("A document without an attachment needs a compute method.")
                raise ValidationError(msg)

    @api.model
    def _get_format(self, attachment):
        split = (attachment.name or "").rsplit(".", 1)
        return split[1] if len(split) > 1 else ""

    @api.model
    def _record(self, attachment):
        return self.env[attachment.res_model].browse(attachment.res_id)

    @api.model
    def _get_partner(self, attachment):
        partner = self.env["res.partner"]
        if attachment.res_model == "res.partner":
            partner = partner.browse(attachment.res_id)
        elif attachment.res_model in self._get_watched_models():
            partner = self._record(attachment).partner_id
        return partner

    @api.model
    def _get_sale_channel(self, attachment) -> SaleChannel:
        sale_channel = self.env["sale.channel"].browse()
        if attachment.res_model == "sale.order":
            sale_channel = self._record(attachment).sale_channel_id
        return sale_channel

    @api.model
    def _get_type(self, attachment):
        document_type = False
        if attachment.res_model == "sale.order":
            document_type = "order"
        elif attachment.res_model == "stock.picking":
            document_type = "delivery_note"
        elif attachment.res_model == "account.move":
            if self._record(attachment).move_type == "out_invoice":
                document_type = "invoice"
            elif self._record(attachment).move_type == "out_refund":
                document_type = "credit_note"
        return document_type

    @api.model
    def _partner_needs_dossier(self, attachment):
        partner = self._get_partner(attachment)
        return not partner or partner.needs_dossier

    @api.model
    def is_dossier_attachment(self, attachment):
        attachment.ensure_one()
        return (
            attachment.res_model in self._get_watched_models()
            or any(attachment.name.startswith(f"{s}_") for s in self._get_prefixes())
        ) and self._partner_needs_dossier(attachment)

    @api.model
    def _get_vals_from_attachment(self, attachment):
        return {
            "name": attachment.name,
            "attachment_id": attachment.id,
            "partner_id": self._get_partner(attachment).id,
            "format": self._get_format(attachment),
            "sale_channel_id": self._get_sale_channel(attachment).id,
            "type": self._get_type(attachment),
        }

    @api.model
    def jobify_process_dossier(self, attachment):
        description = _("Process dossier for attachment %(name)s", name=attachment.name)
        return self.with_delay(description=description).process_dossier(attachment)

    @api.model
    def process_dossier(self, attachment):
        document = None
        if attachment.exists() and self.is_dossier_attachment(attachment):
            vals = self._get_vals_from_attachment(attachment)
            if vals.get("type"):
                document = self.create(vals)
        return document

    @api.model
    def get_partner_domain(self, partner):
        partner.ensure_one()
        # allowed_partner_types is unused as to now.
        # however we distinguish between compute type that might appear once per partner
        # and other types that might be linked to the address book,
        # e.g. delivery notes to the shipping partner
        return [
            "|",
            "&",
            ("partner_id", "child_of", partner.id),
            ("compute", "=", False),
            "&",
            ("partner_id", "=", partner.id),
            ("compute", "!=", False),
        ]

    @api.depends("document_date")
    def _compute_is_null_document_date_start(self):
        """
        By default we cannot order DESC and put all nulls at the end with Odoo.

        (ORDER BY document_date DESC NULLS FIRST)
        Change the code of Odoo to allows ordering nulls first is really touchy.
        To avoid that I create a simply boolean to say if the field document_date
        is null and I order on this field.
        """
        for rec in self:
            rec.is_null_document_date_start = bool(not rec.document_date)

    @api.depends("attachment_id")
    def _compute_document_date(self):
        for document in self:
            document.document_date = document._get_document_date()

    def _get_document_date(self):
        self.ensure_one()
        return self.attachment_id.create_date
