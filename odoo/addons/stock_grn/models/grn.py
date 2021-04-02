# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright (C) 2015-TODAY BCIM <http://www.bcim.be>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models


class GRNType(models.Model):
    """ GRN Type """

    _name = "stock.grn.type"

    name = fields.Char(string="Type", required=True)


class GRN(models.Model):
    """ Goods Received Note """

    _name = "stock.grn"
    _description = "Goods Received Note"
    _order = "id desc"

    name = fields.Char(
        string="Name", copy=False, index=True, required=True, default="/"
    )
    carrier_id = fields.Many2one("res.partner", string="Carrier", required=True)
    carrier_category_id = fields.Integer(compute="_compute_carrier_category_id")
    carrier_ref = fields.Char(string="Carrier Id")

    from_info = fields.Char(string="From")
    ref = fields.Char(string="Reference")

    date = fields.Datetime(
        "Date", required=True, default=lambda self: fields.Datetime.now()
    )
    description = fields.Text("Description")
    type_id = fields.Many2one("stock.grn.type", string="Type")
    qty_pallet = fields.Integer(string="Qty Pallets")
    qty_box = fields.Integer(string="Qty Boxes")

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        change_default=True,
        default=lambda self: self.env["res.company"]._company_default_get("stock.grn"),
        required=True,
        readonly=True,
    )

    picking_ids = fields.One2many(
        "stock.picking",
        "grn_id",
        string="Incoming Shipments",
        domain=[("picking_type_code", "=", "incoming")],
    )

    supplier_id = fields.Many2one(
        "res.partner", string="Supplier", related="picking_ids.partner_id", store=True
    )

    def _compute_carrier_category_id(self):
        carrier_category = self.env.ref(
            "alc_partner_carrier.res_partner_category_carrier"
        )
        for rec in self:
            rec.carrier_category_id = carrier_category.id

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            vals["name"] = self.env["ir.sequence"].next_by_code("stock.grn") or "/"
        return super(GRN, self).create(vals)
