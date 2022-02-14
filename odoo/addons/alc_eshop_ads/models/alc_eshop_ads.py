# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AlcEshopAds(models.Model):

    _name = "alc.eshop.ads"
    _description = "Eshop Ads"

    name = fields.Char(required=True)

    image_ids = fields.One2many(
        string="Images", comodel_name="alc.eshop.ads.image", inverse_name="ads_id",
    )
    image_small_url = fields.Char(
        related="image_ids.image_id.image_small_url", store=True
    )
    file_id = fields.Many2one(
        string="storage dile",
        comodel_name="storage.file",
        help="If specified, the file will be downloaded by the customer on "
        "click on the ads banner into the website.",
        ondelete="cascade",
    )

    file = fields.Binary(compute="_compute_file", inverse="_inverse_file")
    filename = fields.Char(related="file_id.name")

    site_url = fields.Char(
        string="Site url",
        help="If specified, the customer will be redirected to this url click "
        "on the ads banner into the website.",
    )
    images_display_rotation = fields.Selection(
        selection=[("based_on_sequence", "Based on sequence"), ("random", "Random")],
        required=True,
        default="based_on_sequence",
    )
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    display_slot = fields.Selection(
        selection=[
            ("top_left", "Top left"),
            ("top_right", "Top right"),
            ("bottom_left", "Bottom left"),
            ("bottom_right", "Bottom right"),
        ],
        required=True,
    )
    lang_id = fields.Many2one(
        "res.lang",
        string="Lang",
        help="If set, the ads will be only visible into the specified "
        "lang on the website",
    )

    @api.constrains("site_url", "file_id")
    def _check_site_url_or_file_id(self):
        for rec in self:
            if rec.site_url and rec.file_id:
                raise ValidationError(
                    _(
                        "You must choose between the download of a file OR the "
                        "redirect to a website on click on the banner"
                    )
                )

    @api.constrains("date_start", "date_end", "display_slot", "lang_id")
    def _validate_slot(self):
        for this in self:
            start = fields.Date.from_string(this.date_start)
            end = fields.Date.from_string(this.date_end)
            if start > end:
                raise ValidationError(
                    _("The defined period on %s is not a valid (%s > %s)")
                    % (this.name, this.date_start, this.date_end)
                )
            # here we use a plain SQL query to benefit of the daterange
            # function available in PostgresSQL
            # (http://www.postgresql.org/docs/current/static/rangetypes.html)
            SQL = """
                    SELECT
                        id
                    FROM
                        %(table)s dt
                    WHERE
                        DATERANGE(dt.date_start, dt.date_end, '[]') &&
                            DATERANGE(%(date_start)s::date, %(date_end)s::date, '[]')
                        AND dt.display_slot=%(display_slot)s
                        AND id != %(id)s"""
            if this.lang_id:
                SQL += " AND (dt.lang_id = %(lang_id)s OR dt.lang_id is null)"
            self.env.cr.execute(
                SQL,
                dict(
                    table=AsIs(self._table),
                    date_start=this.date_start,
                    date_end=this.date_end,
                    lang_id=this.lang_id.id,
                    display_slot=this.display_slot,
                    id=this.id,
                ),
            )
            res = self.env.cr.fetchall()
            if res:
                dt = self.browse(res[0][0])
                raise ValidationError(
                    _("%s overlaps %s on slot %s")
                    % (this.name, dt.name, this.get_display_slot_label())
                )

    def get_display_slot_label(self):
        return self._fields.get("display_slot").convert_to_export(
            self.display_slot, self
        )

    @api.depends("file_id")
    def _compute_file(self):
        for rec in self:
            rec.file = rec.file_id.data

    def _inverse_file(self):
        for rec in self:
            if not rec.file and rec.file_id:
                rec.file_id.unlink()
                continue
            if rec.file:
                if rec.file_id:
                    rec.file_id.data = rec.file
                    continue
                rec.file_id = rec.file_id.create(
                    {
                        "backend_id": rec._get_default_backend_id(),
                        "name": rec.filename,
                        "data": rec.file,
                    }
                )

    def _get_or_create_file_id(self):
        self.ensure_one()
        if not self.file_id:
            self.file_id = self.file_id.create(
                {"backend_id": self._get_default_backend_id(), "name": self.name}
            )
        return self.file_id

    def _get_default_backend_id(self):
        return self.env["storage.backend"]._get_backend_id_from_param(
            self.env, "storage.image.backend_id"
        )

    @api.depends("name", "date_start", "date_end", "display_slot")
    def _compute_display_name(self):
        qweb_date = self.env["ir.qweb.field.date"]
        for rec in self:
            rec.display_name = u"{} - {} ({} -> {})".format(
                rec.name,
                rec.get_display_slot_label(),
                qweb_date.value_to_html(rec.date_start, rec),
                qweb_date.value_to_html(rec.date_end, rec),
            )
