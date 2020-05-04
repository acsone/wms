# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import date, timedelta

import odoo.addons.decimal_precision as dp
import pytz
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    total_weight = fields.Float(
        "Total weight",
        compute="_compute_total_weight",
        readonly=True,
        help="Total weight in Kg",
    )
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", track_visibility="onchange"
    )
    nbr_lines = fields.Integer("Nbr lines", compute="_compute_nbr_lines", readonly=True)
    nbr_lines_bo = fields.Integer(
        "Nbr lines BO",
        compute="_compute_nbr_lines_bo",
        search="_search_nbr_lines_bo",
        readonly=True,
    )

    @api.model
    def convert_time(self, pl_day, pl_time=14.00):
        """
        mock float field to respect user timezone
        pl_day - date in string format
        pl_time - time in float format
        """
        tz_utc = pytz.timezone("UTC")
        tz_context = pytz.timezone(self.env.context.get("tz", "UTC"))

        new_planned_date = fields.Datetime.from_string(pl_day)
        hour = int(pl_time)
        minute = int(round(pl_time - hour) * 60)
        new_planned_date = new_planned_date.replace(hour=hour, minute=minute, second=0)
        return tz_context.localize(new_planned_date).astimezone(tz_utc)

    @api.multi
    def action_set_date_planned(self):
        # disabled default method
        for order in self:
            renew_date = self.convert_time(order.date_planned)
            order.order_line.update({"date_planned": renew_date})

    @api.multi
    def _compute_nbr_lines(self):
        """
        Compute the number of lines by purchase order.
        :return:
        """
        for po in self:
            po.nbr_lines = len(po.order_line)

    @api.multi
    def _compute_nbr_lines_bo(self):
        """
        Compute the number of lines with back order by purchase order.
        :return:
        """
        for po in self:
            # NOTE: computing 'immediately_usable_qty' field is very slow,
            # especially when the field is displayed on PO tree view
            po.nbr_lines_bo = len(
                po.order_line.filtered(
                    lambda line: line.product_id.immediately_usable_qty < 0
                )
            )

    def _search_nbr_lines_bo(self, operator, value):
        orders = self.browse()
        draft_orders = self.search([("state", "=", "draft")])
        for order in draft_orders:
            # NOTE: actual operator is ignored here for the sake of simplicity.
            # To implement if it's really needed.
            if order.nbr_lines_bo:
                orders |= order
        return [("id", "in", orders.ids)]

    @api.model
    def create(self, vals):
        """
        Set the default responsible on a purchase order
        :param vals:
        :return:
        """
        if not vals.get("responsible_id") and vals.get("partner_id"):
            partner = self.env["res.partner"].browse(vals["partner_id"])
            if partner.purchase_manager_id:
                vals["responsible_id"] = partner.purchase_manager_id.id

        return super(PurchaseOrder, self).create(vals)

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        for rec in self:
            if rec.state == "draft" and vals.get("date_planned"):
                rec.action_set_date_planned()
        return res

    @api.multi
    def _compute_total_weight(self):
        for po in self:
            total_weight = 0
            for line in po.order_line:
                total_weight += line.product_id.weight * line.product_qty

            po.total_weight = total_weight

    @api.multi
    def button_confirm(self):
        self.responsible_id = self.env.user.id

        return super(PurchaseOrder, self).button_confirm()

    @api.multi
    def _add_supplier_to_product(self):
        """
        Disable this feature
        :return:
        """
        return

    last_date_done = fields.Datetime(
        string="Last date of Transfer", compute="_compute_last_date_done", store=True
    )

    @api.depends("order_line.qty_received")
    def _compute_last_date_done(self):
        for order in self:
            if order.is_shipped:
                order.last_date_done = max(order.picking_ids.mapped("date_done"))
            else:
                order.last_date_done = False


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    price_unit_base = fields.Float(
        "Unit Price", required=True, digits=dp.get_precision("Product Price")
    )
    price_unit = fields.Float(string="Unit Price (discounted)")
    discount_global = fields.Float(
        default=lambda line: line.order_id.partner_id.supplier_discount
    )
    promotion_supplier = fields.Float(default=0.0)
    product_ref = fields.Char("Product ref", related="product_id.default_code")
    is_bo_line = fields.Boolean("BO Line", compute="_compute_is_bo_line", readonly=True)

    @api.multi
    def _compute_is_bo_line(self):
        """
        Compute if the PO line is contains a product in BO.
        :return:
        """
        for line in self:
            line.is_bo_line = line.product_id.immediately_usable_qty < 0

    # By default there is no way to add a discounts in Purchase Lines.
    # To do that I added a new field "price_unit_base".
    # This field will replace the field "price_unit" in the view form and the
    # field price_unit will contains the price of the product with discount.
    #
    # When the user create a Purchase Order Line he will set the price
    # on price_unit_base and recompute the price with discount.
    @api.model
    def create(self, vals):
        """
        To keep a good compatibility we set the price_unit_base if
        the user create a purchase_order_line without price_unit_base
        (and vice versa)
        :param vals:
        :return:
        """
        if "price_unit" in vals and "price_unit_base" not in vals:
            vals["price_unit_base"] = vals["price_unit"]

        if "price_unit_base" in vals and "price_unit" not in vals:
            vals["price_unit"] = vals["price_unit_base"]

        return super(PurchaseOrderLine, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        To keep a good compatibility we set the price_unit_base if the user
        change the price_unit we need to recompute the price_unit_base.

        The view will always give both fields.

        :param vals:
        :return:
        """
        # discount_incl = self.env.context.get('discount_incl')
        # if 'price_unit' in vals and not discount_incl:
        #     vals['price_unit_base'] = vals['price_unit']

        return super(PurchaseOrderLine, self).write(vals)

    @api.onchange("price_unit_base", "discount_global", "promotion_supplier")
    def _onchange_price_unit(self):
        """
        This method defines when price unit must be recomputed from the view
        """
        self._set_price_unit()

    @api.model
    def _compute_discount(self, base_price, discount1, discount2):
        return base_price * (1 - (discount1 / 100)) * (1 - (discount2 / 100))

    def _set_price_unit(self):
        """
        This method will compute the price unit according
        the price_unit_base with discounts.

        This method must be called to upon changes on
        price_unit_base, discount_global or promotion_supplier

        """
        for line in self:
            price_unit = self._compute_discount(
                line.price_unit_base, line.discount_global, line.promotion_supplier
            )
            # set context only out of onchange context
            # as it would loose cached values otherwise
            if line.id:
                line = line.with_context(discount_incl=True)
            line.price_unit = price_unit

    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        result = super(PurchaseOrderLine, self)._onchange_quantity()
        self.price_unit_base = self.price_unit
        self._set_promotion_supplier()
        self._set_price_unit()

        return result

    def _get_seller(self):
        """Get supplier info for purchase line"""
        self.ensure_one()
        seller = self.env["res.partner"]
        if self.product_id:
            po = self.order_id
            seller = self.product_id._select_seller(
                partner_id=self.partner_id,
                quantity=self.product_qty,
                date=po.date_order and po.date_order[:10],
                uom_id=self.product_uom,
            )
        return seller

    def _set_promotion_supplier(self):
        if self.product_id:
            seller = self._get_seller()
            self.promotion_supplier = seller.discount_purchase or 0.0
        else:
            self.promotion_supplier = 0.0

    @api.onchange("product_id")
    def onchange_product_id(self):
        """
        Force discount recomputation, handle scheduled date
        priority to initialize planned date:
            if day_planned set - all new lines initialized with this date,
            otherwise date computed based on seller
        """
        result = super(PurchaseOrderLine, self).onchange_product_id()
        self.recompute_discount_values()

        return result

    @api.multi
    def recompute_discount_values(self):
        """ Recompute discount values
        (global discount, supplier promotion and scheduled date).

        This method can be use to recompute PO in draft to keep a valid
        scheduled date and update promotions.
        """
        for line in self:
            line._set_promotion_supplier()

            if line.product_id:
                seller = line._get_seller()
                line.date_planned = line._get_date_planned(seller)

            if not line.discount_global:
                line.discount_global = line.order_id.partner_id.supplier_discount
            line._set_price_unit()

    @api.multi
    def get_next_scheduled_date(self, seller, date_order_str=None):
        """
        Return the scheduled date
        :return: datetime - the scheduled date
        """

        # By default, take the delivery lead time on the supplier info
        if seller:
            lead_time = seller.delay
        # If there is no supplier info for this product, we take
        # the delivery lead time on the supplier
        elif len(self) == 1:
            lead_time = self.order_id.partner_id.delivery_lead_time
        else:
            lead_time = 0

        if date_order_str:
            date_planned = fields.Datetime.from_string(date_order_str)
        else:
            date_planned = date.today()

        holiday_obj = self.env["bank.holiday"]
        index = 0
        while index < lead_time:
            date_planned += timedelta(days=1)

            # Check if there is a bank holiday for the current date planned
            date_order_str = fields.Date.to_string(date_planned)
            holiday = holiday_obj.search([("date", "=", date_order_str)])
            if holiday:
                continue

            # Check if the date planned is Saturday or Sunday
            if date_planned.isoweekday() in [6, 7]:
                continue

            index += 1
        return fields.Datetime.to_string(date_planned)

    @api.model
    def _get_date_planned(self, seller, po=False):
        """
        Inherit the method "_get_date_planned" in the module purchase
        The original method has the decorator "api.model" but
        it should be the decorator api.multi or api.one.
        The parameter po is priority on self (see below)
        purchase.py:
        date_order = po.date_order if po else self.order_id.date_order
        :param seller:
        :param po:
        :return:
        """
        date_planned_str = False
        if not po:
            po = self.order_id
        if po.date_planned:
            # if there is planned date propagate it all lines
            date_planned_str = po.convert_time(po.date_planned).strftime(
                DEFAULT_SERVER_DATETIME_FORMAT
            )
        if not date_planned_str:
            date_order_str = po.date_order if po else self.order_id.date_order
            date_planned_str = self.get_next_scheduled_date(seller, date_order_str)

        return fields.Datetime.from_string(date_planned_str)

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        if not res:
            # If no stock move is created, then the procurement will never be
            # checked (this is done when the move state changes to done or
            # cancel)
            self.ensure_one()
            self.procurement_ids.check()
        return res
