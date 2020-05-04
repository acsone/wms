# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RoundItinerary(models.Model):
    _name = "round.itinerary"
    _order = "sequence"

    sequence = fields.Integer("Sequence")
    name = fields.Char("Name", required=True)
    code = fields.Char("Code", required=True)
    color = fields.Integer("Color Index")
    partner_position_ids = fields.One2many(
        "round.itinerary.position", "itinerary_id", "Partners"
    )
    template_ids = fields.Many2many("round.template", string="Vehicle")
    partner_ids = fields.Many2many(
        "res.partner",
        string="Partners",
        compute="_compute_partner_ids",
        search="_search_partner_ids",
        readonly=True,
    )

    @api.multi
    def _compute_partner_ids(self):
        for itinerary in self:
            partners = itinerary.mapped("partner_position_ids.partner_id")
            itinerary.partner_ids = [(6, 0, partners.ids)]

    def _search_partner_ids(self, operator, value):
        """
        Search for itinerary containing the customer name
        :param operator:
        :param value:
        :return:
        """

        positions = self.env["round.itinerary.position"].search(
            [("partner_id.name", operator, value)]
        )

        return [("partner_position_ids", "in", positions.ids)]


class RoundItineraryPosition(models.Model):
    _name = "round.itinerary.position"
    _order = "sequence"

    itinerary_id = fields.Many2one("round.itinerary", "Itinerary", ondelete="cascade")
    sequence = fields.Integer("Sequence")
    partner_id = fields.Many2one(
        "res.partner",
        "Partner",
        required=True,
        ondelete="restrict",
        domain=["|", ("customer", "=", True), ("type", "=", "delivery")],
        index=True,
    )
    partner_zip = fields.Char("Partner ZIP", related="partner_id.zip", readonly=True)
    partner_city = fields.Char("Partner city", related="partner_id.city", readonly=True)
    partner_street = fields.Char(
        "Partner street", related="partner_id.street", readonly=True
    )
    tag_ids = fields.Many2many("round.tag", string="Tags")

    @api.multi
    @api.depends("itinerary_id", "tag_ids")
    def name_get(self):
        result = []
        for rec in self:
            name = rec.itinerary_id.name
            tags = "/".join(
                rec.tag_ids.with_context(short_round_tag_name=True).mapped(
                    "display_name"
                )
            )
            if tags:
                name += " (%s)" % tags
            templates = rec.itinerary_id.template_ids.with_context(
                short_round_template_name=True, show_round_template_tags=True
            ).mapped("display_name")
            if templates:
                name += " [%s]" % ", ".join(templates)
            result.append((rec.id, name))
        return result

    @api.multi
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if name:
            name = name.split(" ", 1)[0]
        res = self.search(args + [("itinerary_id.name", operator, name)], limit=limit)
        return res.name_get()
