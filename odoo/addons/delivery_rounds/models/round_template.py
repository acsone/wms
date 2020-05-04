# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError

re_name = re.compile(r"(\w+) ?- ?(\w+)( .*)?")


class RoundTemplateVersion(models.Model):
    _name = "round.template.version"

    name = fields.Char("Name", required=True)
    template_ids = fields.Many2many("round.template", string="Templates")
    is_default_version = fields.Boolean("Default version")

    @api.constrains("is_default_version")
    def constrains_is_default_version(self):
        for version in self:
            if not version.is_default_version:
                continue

            default_version = self.search(
                [("is_default_version", "=", True), ("id", "!=", version.id)]
            )
            if default_version:
                raise UserError(
                    _("You cannot have more " "than one default version at once.")
                )


class RoundTemplate(models.Model):
    _name = "round.template"
    _order = "time_leave_planned"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", required=True, default="0")
    itinerary_ids = fields.Many2many("round.itinerary", string="Itineraries")
    color = fields.Integer("Color Index")
    time_picking_planned = fields.Float("Planned Picking Start Time")
    time_leave_planned = fields.Float("Planned Vehicle Start Time")
    version_ids = fields.Many2many("round.template.version", string="Versions")
    partner_ids = fields.Many2many(
        "res.partner",
        string="Partners",
        readonly=True,
        compute="_compute_partner_ids",
        search="_search_partner_ids",
    )
    tag_ids = fields.Many2many("round.tag", string="Tags")

    @api.multi
    def _compute_partner_ids(self):
        for template in self:
            partners = template.mapped("itinerary_ids.partner_position_ids.partner_id")

            template.partner_ids = [(6, 0, partners.ids)]

    def _search_partner_ids(self, operator, value):
        """
        Search for template containing the customer name
        :param operator:
        :param value:
        :return:
        """

        positions = self.env["round.itinerary.position"].search(
            [("partner_id.name", operator, value)]
        )
        itineraries = self.env["round.itinerary"].search(
            [("partner_position_ids", "in", positions.ids)]
        )

        return [("itinerary_ids", "in", itineraries.ids)]

    @api.multi
    @api.depends("name", "code", "tag_ids")
    def name_get(self):
        result = []
        for rec in self:
            name = rec.code
            if not self.env.context.get("short_round_template_name"):
                name += " - %s" % rec.name
            if self.env.context.get("show_round_template_tags"):
                tags = "/".join(
                    rec.tag_ids.with_context(short_round_tag_name=True).mapped(
                        "display_name"
                    )
                )
                if tags:
                    name += " (%s)" % tags
            result.append((rec.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            vals = re_name.match(name)
            if vals:
                vals = vals.groups()
                code = vals[0]
                text = vals[1]
                comb = operator.startswith("not ") and "|" or "&"
            else:
                code = text = name.strip()
                comb = operator.startswith("not ") and "&" or "|"
            domain = [comb, ("code", operator, code), ("name", operator, text)]
        records = self.search(domain + args, limit=limit)
        return records.name_get()
