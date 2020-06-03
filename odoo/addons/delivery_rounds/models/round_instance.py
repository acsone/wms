# -*- coding: utf-8 -*-
# Copyright 2016-2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2017-2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import math
from ast import literal_eval
from contextlib import closing, contextmanager
from datetime import datetime
from itertools import groupby

import odoo
from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import config

_logger = logging.getLogger(__name__)


def float2time(value):
    hour = math.floor(value)
    minute = round((value % 1) * 60)
    if minute == 60:
        minute = 0
        hour = hour + 1
    return "%d:%02d" % (hour, minute)


def time2float(value):
    return value.hour + value.minute / 60.0


def time_now(record):
    tz_name = record.env.context.get("tz") or record.env.user.tz
    if not tz_name:
        raise UserError("Please configure your timezone in your user preferences")
    return time2float(fields.Datetime.context_timestamp(record, datetime.now()))


class RoundInstance(models.Model):
    _name = "round.instance"
    _order = "date asc, time_picking_planned asc"
    _rec_name = "complete_name"

    date = fields.Date(
        "Date",
        required=True,
        states={"done": [("readonly", True)], "delivering": [("readonly", True)]},
        default=fields.Date.context_today,
    )

    time_picking_planned = fields.Float(
        "Planned Picking Start Time",
        states={"done": [("readonly", True)], "delivering": [("readonly", True)]},
    )
    time_leave_planned = fields.Float(
        "Planned Vehicle Start Time",
        states={"done": [("readonly", True)], "delivering": [("readonly", True)]},
    )

    stat_time_closed = fields.Float("Closed Time", readonly=True)
    stat_time_picking = fields.Float("Picking Start Time", readonly=True)
    stat_time_loading = fields.Float("Vehicle Loading Time", oldname="stat_time_leave")
    can_edit_stat_time_loading = fields.Boolean(
        compute="_compute_can_edit_stat_time_loading"
    )

    template_id = fields.Many2one(
        "round.template",
        "Template",
        states={"done": [("readonly", True)]},
        required=True,
        ondelete="restrict",
    )
    template_code = fields.Char(
        "Code", related="template_id.code", store=True, readonly=True
    )
    template_name = fields.Char(
        "Name", related="template_id.name", store=True, readonly=True
    )
    color = fields.Integer(related="template_id.color")
    state = fields.Selection(
        [
            ("pending", "Anticipated"),
            ("draft", "Open"),
            ("close", "Closed"),
            ("delivering", "Delivering"),
            ("done", "Done"),
        ],
        "State",
        readonly=True,
        default="pending",
    )
    picking_launched = fields.Boolean("Pickings Launched", readonly=True)

    itinerary_ids = fields.Many2many("round.itinerary", string="Itineraries")

    picking_ids = fields.One2many(
        "stock.picking",
        "delivery_round_id",
        "Pickings",
        domain=[("picking_type_subcode", "=", "PICK")],
        readonly=True,
    )
    shipping_ids = fields.One2many(
        "stock.picking",
        "delivery_round_id",
        "Deliveries",
        domain=[("picking_type_code", "=", "outgoing")],
        readonly=True,
    )

    complete_name = fields.Char(
        "Display Name", readonly=True, compute="_get_complete_name", store=True
    )
    tag_ids = fields.Many2many("round.tag", string="Tags")
    partner_ids = fields.Many2many(
        "res.partner",
        string="Partners",
        readonly=True,
        compute="_compute_partner_ids",
        search="_search_partner_ids",
    )
    instance_customer_ids = fields.One2many(
        comodel_name="round.instance.customer",
        inverse_name="delivery_round_id",
        string="Customers",
        states={"done": [("readonly", True)], "delivering": [("readonly", True)]},
    )
    delivery_failure = fields.Boolean(compute="_compute_delivery_failure")
    report_delivery = fields.Html(compute="_compute_report_delivery", readonly=True)

    @api.depends("instance_customer_ids.delivery_error")
    @api.multi
    def _compute_delivery_failure(self):
        for record in self:
            record.delivery_failure = any(
                icust.delivery_error for icust in record.instance_customer_ids
            )

    @api.depends("instance_customer_ids.delivery_error")
    @api.multi
    def _compute_report_delivery(self):
        for record in self:
            record.report_delivery = self.env.ref(
                "delivery_rounds.round_report_delivery"
            ).render({"customers": record.instance_customer_ids})

    @api.multi
    def _compute_partner_ids(self):
        for instance in self:
            partners = instance.mapped("itinerary_ids.partner_position_ids.partner_id")
            instance.partner_ids = [(6, 0, partners.ids)]

    @api.multi
    def _compute_can_edit_stat_time_loading(self):
        can_edit = self.env.user.has_group("base.group_system")
        for record in self:
            record.can_edit_stat_time_loading = can_edit

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
    @api.depends("template_id", "date", "time_leave_planned")
    def _get_complete_name(self):
        for rec in self:
            rec.complete_name = u"{} {} - {}".format(
                rec.date,
                float2time(rec.time_leave_planned),
                rec.template_id.display_name,
            )

    @api.onchange("template_id")
    def onchange_template_id(self):
        self.ensure_one()
        if not self.template_id:
            return
        template = self.template_id
        self.itinerary_ids = [(6, 0, template.itinerary_ids.ids)]
        self.tag_ids = [(6, 0, template.tag_ids.ids)]
        self.time_picking_planned = template.time_picking_planned
        self.time_leave_planned = template.time_leave_planned

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            vals = name.split("-", 1)
            if len(vals) > 1:
                code = vals[0].strip()
                text = vals[1].strip()
                comb = operator.startswith("not ") and "|" or "&"
            else:
                code = text = name.strip()
                comb = operator.startswith("not ") and "&" or "|"
            domain = [
                comb,
                ("template_code", operator, code),
                ("template_name", operator, text),
            ]
        records = self.search(domain + args, limit=limit)
        return records.name_get()

    @api.multi
    def button_itinerary_import(self):
        return dict(
            self.env.ref("delivery_rounds.action_round_itinerary_import").read()[0]
        )

    @api.multi
    def button_update(self):
        for record in self:
            record._include_itinerary(self.itinerary_ids)

    def _include_itinerary(self, itineraries):
        self.ensure_one()

        self.itinerary_ids |= itineraries

        partners = (
            itineraries.mapped("partner_position_ids")
            .filtered(
                lambda p: not self.tag_ids  # See find_bypartner tag rules
                or not p.tag_ids
                or p.tag_ids & self.tag_ids
            )  # & is intersect
            .mapped("partner_id")
        )

        # Itineraries can contain partners of any type. So extract
        # corresponding delivery address
        partners_delivery_ids = [
            partner.address_get(["delivery"])["delivery"] for partner in partners
        ]

        picking_confirmed = self.env["stock.picking"].search(
            [
                ("delivery_round_id", "=", False),
                ("partner_id", "in", partners_delivery_ids),
                ("state", "not in", ("done", "cancel")),
                ("picking_type_subcode", "=", "PICK"),
            ]
        )
        self._assign_pickings(picking_confirmed)

    def _check_printed_pickings(self, pickings):
        errors = []
        for pick in pickings:
            if (
                pick.printed
                and pick.delivery_round_id
                and pick.pack_operation_product_ids
            ):
                errors.append(
                    _(
                        "You cannot reassign the started picking %s "
                        "on the delivery round %s to the delivery round %s"
                    )
                    % (
                        pick.name,
                        pick.delivery_round_id.complete_name,
                        self.complete_name,
                    )
                )
        if errors:
            raise UserError("\n".join(errors))

    def _check_allowed_holidays_pickings(self, pickings):
        errors = {}
        for pick in pickings:
            partner = pick.partner_id
            if (
                pick.picking_type_code != "incoming"
                and not partner.is_shipping_date_allowed(self.date)
            ):
                if partner.id not in errors.keys():
                    errors[partner.id] = _(u"{} is not working day for {}").format(
                        self.date, partner.name
                    )
        if errors:
            raise UserError("\n".join(errors.values()))

    def _assign_pickings(self, pickings, no_prepare=False):
        self.ensure_one()

        _logger.info(
            "Assign to round instance %s the pickings %s (%s)",
            self.id,
            pickings.mapped("name"),
            pickings.ids,
        )
        pickings._lock()
        self._check_printed_pickings(pickings)
        if self.env.context.get("manual_change_delivery_round"):
            self._check_allowed_holidays_pickings(pickings)

        pickings.filtered(lambda picking: picking.state == "draft").action_confirm()
        # Note: MTO moves in waiting state are updated in standard by a call to
        # action_assign, so we need to propagate it
        self._assign_picking_moves_to_assign(pickings, no_prepare=no_prepare)
        # Retrieve all pickings (partially) available
        # Do not look at the state of the picking as assigned state has the
        # lowest priority
        moves_assigned = pickings.mapped("move_lines").filtered(
            lambda move: move.state == "assigned"
            or (move.state == "confirmed" and move.partially_available)
        )
        pickings_assigned = moves_assigned.mapped("picking_id")
        if pickings_assigned:
            # Get and assign linked picking to be sure that they are all into
            # the same delivery round
            linked_pickings = self._get_linked_pickings(pickings_assigned)
            self._assign_picking_moves_to_assign(linked_pickings, no_prepare=no_prepare)

            # Use | to let it work in tests with one step delivery
            pickings_assigned |= linked_pickings

            def key(r):
                partner = r.partner_id
                # If delivery address is a contact, take parent
                if partner.type == "contact" and partner.parent_id:
                    partner = partner.parent_id
                return partner

            for partner, pickings_bypartner_iter in groupby(
                pickings_assigned.sorted(key=key), key=key
            ):
                ric = self._add_customer(partner)
                pickings_bypartner = reduce(lambda x, y: x | y, pickings_bypartner_iter)
                # As we filtered on assigned, we typically excluded the waiting
                # shippings. So include them back
                pickings_bypartner |= pickings_bypartner._get_all_dest_pickings()
                ric._link_pickings(pickings_bypartner)
        return pickings_assigned

    @api.model
    def _assign_picking_moves_to_assign(self, pickings, no_prepare=False):
        moves_to_assign = pickings.mapped("move_lines").filtered(
            lambda move: move.state not in ("done", "cancel")
            and move.product_uom_qty > 0.0
        )
        moves_to_assign = moves_to_assign.filtered(
            lambda move: not move.linked_move_operation_ids
        )
        return moves_to_assign.with_context(round_autoset=False).action_assign(
            no_prepare=no_prepare
        )

    @api.model
    def _get_linked_pickings(self, pickings):
        """
        Return all the pickings chained to the same outgoing pickings of those
        of the given pickings.

        This method id usefull to be sure that if a picking is manually added
        to a delivery round, all the pickings linked to the same outgoing
        picking are also included into the same delivery_round instance
        """
        shippings = pickings._get_all_dest_pickings().filtered(
            lambda r: r.picking_type_code == "outgoing"
        )
        return shippings._get_all_src_pickings()

    @api.multi
    def _add_customer(self, customer):
        self.ensure_one()
        customer.ensure_one()
        ric = self.env["round.instance.customer"].search(
            [
                ("delivery_round_id", "=", self.id),
                ("partner_id", "=", customer.id),
                ("delivered", "!=", True),
            ],
            limit=1,
        )
        rank = 0
        if not ric:
            pos = self.env["round.itinerary.position"].search(
                [
                    ("itinerary_id", "in", self.itinerary_ids.ids),
                    ("partner_id", "=", customer.id),
                ],
                limit=1,
            )
            if pos:
                rank = (pos.sequence + pos.itinerary_id.sequence * 1000) * 1000
            _logger.warn("Partner added on delivery %s", self.id)
            ric = (
                self.env["round.instance.customer"]
                .sudo()
                .create(
                    {
                        "delivery_round_id": self.id,
                        "partner_id": customer.id,
                        "rank": rank,
                    }
                )
            )
        return ric

    @api.model
    def find_bytemplate(self, template):
        """
        Find a delivery_round for having a specified template. This is used for
        deliveries linked to a specific carrier
        """
        return self.search(
            [
                ("template_id", "=", template.id),
                ("state", "not in", ("delivering", "done")),
            ],
            order="date asc, time_leave_planned asc",
            limit=1,
        )

    @api.model
    def find_bypartner(self, partner):
        """
        Find a delivery_round for this partner according to tags defined
        on customer position or round instance.
        Round instances are sorted according to the date and the time of
        the picking.

        Here is the rule for taking or not a round instance:
        - If you define one (or more) tag on the instance, only customer
        containing this tag will be taken
        - A customer without tag will be taken in any case

        :param partner:
        :return:
        """
        if not partner:
            # This should not happen unless a picking without partner has been
            # manually created
            return False

        _logger.debug("Search a round instance for partner %s", partner.id)

        # The following query will search for the best itinerary instance.
        # First, the query will search for all open instance (state = draft)
        # The itinerary linked to this instance must contains the partner
        # (round_instance_round_itinerary_rel).
        # In this case, we will check tags on the customer (customer_tag)
        # and the instance tag (instance_tag).
        # Info: A customer and/or instance can have several tags.
        # In this case the query will return several lines.
        #
        # Tags rules:
        # - The customer tag must be equal to the instance tag
        # - The customer tag is empty
        # - The instance tag is empty

        # If delivery address is a contact, take parent
        if partner.type == "contact" and partner.parent_id:
            partner = partner.parent_id

        best_instance_query = """
        SELECT instance.id
        FROM round_instance_round_itinerary_rel AS rel
          INNER JOIN round_instance AS instance
            ON rel.round_instance_id = instance.id
          INNER JOIN round_itinerary_position AS position
            ON position.itinerary_id = rel.round_itinerary_id
          INNER JOIN res_partner AS customer
            ON position.partner_id = customer.id
          LEFT JOIN round_instance_round_tag_rel AS instance_tag
            ON instance.id = instance_tag.round_instance_id
          LEFT JOIN round_itinerary_position_round_tag_rel AS customer_tag
            ON position.id = customer_tag.round_itinerary_position_id
        WHERE instance.state = 'draft'
          AND (instance_tag.round_tag_id = customer_tag.round_tag_id
              OR customer_tag IS NULL
              OR instance_tag IS NULL)
          AND customer.id = %s
        ORDER BY instance.date ASC, instance.time_picking_planned ASC
        LIMIT 1;
        """

        self.env.cr.execute(best_instance_query, (partner.id,))
        result = self.env.cr.fetchone()

        if result:
            _logger.debug("Instance found with ID %s", result[0])
            return self.browse(result[0])

        return False

    count_picking_available_total = fields.Integer(
        "Picking Available Total", compute="_get_count_picking", readonly=True
    )
    count_picking_done_total = fields.Integer(
        "Picking Done Total", compute="_get_count_picking", readonly=True
    )
    count_picking_available_partner = fields.Integer(
        "Picking Available Partner", compute="_get_count_picking", readonly=True
    )
    count_picking_available_weight = fields.Integer(
        "Picking Available Total", compute="_get_count_weight", readonly=True
    )

    @api.depends("picking_ids")
    def _get_count_weight(self):
        self._cr.execute(
            """
            SELECT picking.delivery_round_id,
            sum(coalesce(product_template.weight, 0) *
                coalesce(stock_pack_operation.product_qty, 0))
            FROM stock_picking picking
            LEFT JOIN stock_picking_type
                ON picking.picking_type_id = stock_picking_type.id
            LEFT JOIN stock_pack_operation
                ON stock_pack_operation.picking_id = picking.id
            LEFT JOIN product_product
                ON stock_pack_operation.product_id = product_product.id
            LEFT JOIN product_template
                ON product_product.product_tmpl_id = product_template.id
            WHERE picking.state != 'cancel'
            AND stock_picking_type.subcode = 'PICK'
            AND picking.delivery_round_id in %s
            GROUP BY picking.delivery_round_id
            """,
            (tuple(self.ids),),
        )
        for r in self._cr.fetchall():
            self.browse(r[0]).count_picking_available_weight = r[1]

    @api.depends("picking_ids")
    def _get_count_picking(self):
        for rec in self:
            rec.count_picking_done_total = len(
                rec.picking_ids.filtered(lambda r: r.state == ("done"))
            )
            pickings = rec.picking_ids.filtered(
                lambda r: r.state in ("partially_available", "assigned", "done")
                or any(
                    move.state in ("done", "assigned")
                    or (move.state == "confirmed" and move.partially_available)
                    for move in r.move_lines
                )
            )
            rec.count_picking_available_total = len(pickings)
            rec.count_picking_available_partner = len(pickings.mapped("partner_id"))

    @api.multi
    def action_picking_tree_available(self):
        action = self.env["ir.actions.act_window"].for_xml_id(
            "delivery_rounds", "action_picking_tree_available_round"
        )

        domain_str = action.get("domain", "[]")
        domain = literal_eval(domain_str)

        domain += [("state", "!=", "cancel")]
        action["domain"] = domain

        return action

    @api.multi
    def toggle_picking_launched(self):
        started = self.filtered("picking_launched")
        stopped = self - started
        started.button_picking_stop()
        stopped.button_picking_start()

    @api.multi
    def button_picking_start(self):
        """ Pickings can be processed """
        for rec in self:
            rec.picking_launched = True
            if not rec.stat_time_picking:
                rec.stat_time_picking = time_now(self)

    @api.multi
    def button_picking_stop(self):
        """ Pickings cannot be processed """
        self.write({"picking_launched": False})

    @api.multi
    def toggle_partner_locked(self):
        opened = self.filtered(lambda r: r.state == "draft")
        closed = self.filtered(lambda r: r.state == "close")
        opened.button_close()
        closed.button_resetdraft()

    @api.multi
    def button_close(self):
        """ Do not accept new picking automaticaly.
        """
        not_started = self.filtered(lambda r: not r.picking_launched)
        not_started.button_picking_start()
        self.write({"state": "close", "stat_time_closed": time_now(self)})

    @api.multi
    def button_deliver(self):
        """ Deliver all customers. This validates all shipping orders that are
        available.
        Mark as done and unlink other deliveries
        """
        self._deliver()
        return True

    def _deliver(self, background=True):
        """ Separated for unit test """
        self.env.user.notify_info(_("Delivery round will be delivered in background."))
        self.filtered(lambda ri: ri.state != "done").mapped(
            "instance_customer_ids"
        ).filtered(lambda c: not c.delivered)._deliver(background=background)
        self.write(
            {
                "state": "delivering",
                "stat_time_loading": self._compute_stat_time_loading(),
            }
        )
        self.recheck_delivery_state()

    def _compute_stat_time_loading(self):
        """
        Compute the theoretical loading time of the truck

        The value returned is a time as float
        """
        return time_now(self)

    @api.multi
    def button_resetdraft(self):
        """ Mark state as draft. This allows new pickings
        """
        self.write({"state": "draft"})

    @api.multi
    def button_resetpending(self):
        """ Mark state as draft. This allows new pickings
        """
        self.write({"state": "pending"})

    @api.multi
    def button_done(self):
        """ Mark as done and unlink waiting deliveries """
        for shipping in self.mapped("shipping_ids"):
            if shipping.state == "waiting":
                shipping.delivery_round_id = False
        started = self.filtered("picking_launched")
        started.button_picking_stop()
        self.write({"state": "done"})

    @api.multi
    def _get_sorted_shipping_ids(self):
        """
        return the shippings into the expected delivery order
        """
        self.ensure_one()
        return self.shipping_ids.filtered(
            lambda shipping: shipping.state == "done"
        ).sorted("rank")

    @api.multi
    def print_all_deliveryslip(self):
        shipping_done = self._get_sorted_shipping_ids()
        return self.env["report"].get_action(shipping_done, "stock.report_deliveryslip")

    @api.multi
    def unlink(self):
        if set(self.mapped("state")) != {"draft"}:
            raise UserError(
                _("You cannot delete a delivery round that has been started")
            )
        if any(self.mapped("picking_ids.printed")):
            raise UserError(
                _("You cannot delete a delivery round having a started picking")
            )
        if any(self.mapped("shipping_ids.printed")):
            raise UserError(
                _("You cannot delete a delivery round having a started shipping")
            )
        pickings = self.mapped("picking_ids")
        res = super(RoundInstance, self).unlink()
        pickings._unassign_delivery_round()
        return res

    @api.multi
    @api.depends("shipping_ids")
    def _compute_shipping_count(self):
        for shipping in self:
            shipping.shipping_count = len(shipping.shipping_ids)

    shipping_count = fields.Integer(compute="_compute_shipping_count")

    @api.multi
    def action_view_shippings(self):
        self.ensure_one()

        action_data = self.env.ref("delivery_rounds.action_picking_tree_round").read()[
            0
        ]
        action_data["domain"] = [
            ("picking_type_code", "=", "outgoing"),
            ("delivery_round_id", "=", self.id),
        ]
        return action_data

    @api.multi
    @api.depends("picking_ids")
    def _compute_picking_count(self):
        for picking in self:
            picking.picking_count = len(picking.picking_ids)

    picking_count = fields.Integer(compute="_compute_picking_count")

    @api.multi
    def action_view_pickings(self):
        self.ensure_one()

        action_data = self.env.ref("delivery_rounds.action_picking_tree_round").read()[
            0
        ]
        action_data["domain"] = [
            ("picking_type_subcode", "=", "PICK"),
            ("delivery_round_id", "=", self.id),
        ]
        return action_data

    def _is_all_customer_delivered(self):
        self.ensure_one()
        return all(ic.delivered for ic in self.instance_customer_ids)

    @job(default_channel="root.background.stock_picking_deliver")  # priority=5
    @api.multi
    def recheck_delivery_state(self):
        for record in self.exists():
            if record.state != "delivering":
                continue

            if record._is_all_customer_delivered():
                # Close delivery round
                record.button_done()
                self.env.user.notify_info(
                    _("Delivery Round %s is now completed") % (self.display_name,)
                )


class RoundInstanceCustomer(models.Model):
    _name = "round.instance.customer"
    _order = "rank,delivered,write_date desc"
    _rec_name = "partner_id"

    delivery_round_id = fields.Many2one(
        comodel_name="round.instance",
        string="Delivery Round",
        required=True,
        readonly=True,
        index=True,
        ondelete="cascade",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
        readonly=True,
        index=True,
        ondelete="restrict",
        oldname="res_partner_id",
    )
    rank = fields.Integer(string="Rank")

    picking_ids = fields.One2many(
        "stock.picking", "delivery_round_customer_id", "Pickings", readonly=True
    )

    delivered = fields.Boolean("Delivered")
    delivery_error = fields.Char()

    @api.model
    def create(self, vals):
        record = super(RoundInstanceCustomer, self).create(vals)
        if "rank" in vals:
            record._propagate_rank()
        return record

    @api.multi
    def write(self, vals):
        result = super(RoundInstanceCustomer, self).write(vals)
        if "rank" in vals:
            self._propagate_rank()
        return result

    @api.multi
    def _link_pickings(self, pickings):
        self.ensure_one()
        # Note that in our case, an open picking cannot have multiple open
        # shippings, so we don't have to ensure a picking is not already done
        # for another delivery round
        pickings = pickings.filtered(
            lambda r: r.state not in ("draft", "cancel", "done")
            and r.delivery_round_customer_id.id != self.id
        )
        if pickings:
            _logger.debug("Link to delivery round the pickings/shippings %s", pickings)
            pickings.with_context(noround_write=True).write(
                {"delivery_round_customer_id": self.id, "rank": self.rank}
            )
            if self.env.context.get("manual_change_delivery_round"):
                # The delivery carrier on the procurement.group is used
                # by stock_groupbypartner for the grouping of moves:
                # moves will be added to a picking only if they share the
                # same delivery.carrier than their procurement group.
                # When we manually set the delivery round, if it is not
                # compatible with the one set on the actual delivery carrier,
                # we assign a special "manual" delivery carrier, so new moves
                # will never be grouped with this picking (because we cannot
                # use this delivery carrier)
                actual_carrier_template = pickings.mapped(
                    "group_id.carrier_id.delivery_template_id"
                )
                all_carrier_templates = (
                    self.env["delivery.carrier"]
                    .search([("delivery_template_id", "!=", False)])
                    .mapped("delivery_template_id")
                )
                new_template = self.delivery_round_id.template_id

                if (
                    not actual_carrier_template
                    and new_template not in all_carrier_templates
                ):
                    # carrier is "Alcyon delivery" and set on an Alcyon
                    # delivery round
                    return
                if actual_carrier_template and new_template in actual_carrier_template:
                    # carrier is a specific delivery and set on corresponding
                    # delivery round
                    return

                manual_method = self.env.ref(
                    "delivery_rounds.delivery_carrier_manual_round_change"
                )
                pickings.mapped("group_id").write({"carrier_id": manual_method.id})

    def _remove_if_empty(self):
        """ Remove partner from round instance if no more pickings or all
        canceled """
        if self and not self.mapped("picking_ids").filtered(
            lambda p: p.state != "cancel"
        ):
            _logger.debug(
                "Removing customers %s from round instance %s",
                self.mapped("partner_id").ids,
                self.mapped("delivery_round_id").ids,
            )
            self.unlink()

    @api.multi
    def _propagate_rank(self):
        for instance_customer in self:
            rank = instance_customer.rank
            # when we set a rank on a round instance customer,
            # we copy that value on the pickings
            pickings = instance_customer.picking_ids.filtered(lambda p: p.rank != rank)
            if not pickings:
                continue
            _logger.debug(
                "Rank set on round instance customer %s. Propagate to "
                "pickings and shippings %s",
                instance_customer.id,
                pickings.ids,
            )
            pickings.write({"rank": rank})

    count_picking_progress = fields.Char(
        "Picking Progress", compute="_get_count_picking", readonly=True
    )

    @api.depends("picking_ids")
    def _get_count_picking(self):
        for rec in self:
            pickings = rec.picking_ids.filtered(
                lambda r: r.picking_type_subcode == "PICK"
            )
            count_done = len(pickings.filtered(lambda r: r.state == ("done")))
            count_total = len(
                pickings.filtered(
                    lambda r: r.state in ("partially_available", "assigned", "done")
                    or any(
                        move.state in ("done", "assigned")
                        or (move.state == "confirmed" and move.partially_available)
                        for move in r.move_lines
                    )
                )
            )
            rec.count_picking_progress = "{}/{}".format(count_done, count_total)

    def button_deliver(self):
        """ Validate all shipping orders that are available """
        self.ensure_one()
        self._deliver(background=False)
        # we need to check for existence because the current record may have
        # been unlinked in _deliver()
        if self.exists() and not self.picking_ids:
            # Nothing was picked, all pickings have been disconnected
            raise UserError(_("No picking have been processed yet"))

    @contextmanager
    def _new_env(self, new_cr=True):
        with api.Environment.manage():
            if new_cr:
                registry = odoo.modules.registry.RegistryManager.get(self.env.cr.dbname)
                with closing(registry.cursor()) as cr:
                    try:
                        yield self.env(cr=cr)
                    except Exception:
                        cr.rollback()
                        raise
                    else:
                        # disable pylint error because this is a valid commit,
                        # we are in a new env
                        cr.commit()  # pylint: disable=invalid-commit
            else:
                # keep the same env
                yield self.env

    @contextmanager
    def _handle_delivery_error(self):
        try:
            yield
        except (ValidationError, UserError, AccessError) as err:
            # Do nothing on purpose, failed job should not need
            # user intervention. The record will be marked
            # as failed, users will see it on the round and be able
            # to retry to deliver manually.
            self.env.clear()
            self.delivery_error = err.name
        except Exception as err:
            _logger.exception(
                "Failed to deliver a shipping during a delivery round "
                "with an unexpected error: %s",
                unicode(err),
            )
            self.env.clear()
            self.delivery_error = _("Unexpected error (%s)") % unicode(err)
            if config["test_enable"] and not self.env.context.get(
                "test_delivery_error_handling"
            ):
                # always raise error in tests to early detect regressions
                raise

    @job(  # noqa: C901
        default_channel="root.background.stock_picking_deliver"
    )  # priority=5
    @api.multi
    def _deliver_job(self):
        # WARNING
        # this method opens a new transaction that locks the related
        # "round.instance" record. Any write or lock acquired on the related
        # "round.instance" before calling this method could make it fail.
        if not self.exists():
            return
        self.ensure_one()
        if self.delivered:
            return
        _logger.info(
            "Starting to deliver customer instance %d of instance %d",
            self.id,
            self.delivery_round_id.id,
        )
        # when a job is executing, we get this key in the context
        background = self.env.context.get("job_uuid") and not config["test_enable"]
        delivery_round = self.delivery_round_id

        with self._handle_delivery_error(), self.env.cr.savepoint():
            pickings = self.env["stock.picking"]
            shippings = self.env["stock.picking"]
            for pick in self.picking_ids:
                if pick.state in ["cancel", "done"]:
                    continue
                elif pick.picking_type_id.subcode == "PICK":
                    pickings |= pick
                elif pick.picking_type_id.code == "outgoing":
                    shippings |= pick

            # check there is no ongoing picking
            ongoing_pickings = pickings.filtered(
                lambda p: p.printed or any(op.qty_done for op in p.pack_operation_ids)
            )
            if ongoing_pickings:
                raise UserError(
                    _("You cannot deliver with ongoing picking(s): %s")
                    % (", ".join(ongoing_pickings.mapped("name")))
                )

            self.write({"delivered": True, "delivery_error": ""})

            # FIXME: should be moved out of delivery_round module and applied in do_transfer
            if self.partner_id.is_sale_back_order_cancel:
                shippings = shippings.with_context(cancel_backorder=True)

            delivery_round = self.delivery_round_id

            # We mark as printed to prevent to be a valid shipping when the
            # backorder is created.
            # For shippings that are not available (no pick done), do not track
            # the change as we are reverting it once detached
            # Most of the cases, there is only one shipping per delivery round
            # customer unless a shipping with another delivery method (carrier)
            # has been forced to this delivery round
            for shipping in shippings:
                if not shipping.pack_operation_ids:
                    shipping.with_context(tracking_disable=True).printed = True
                else:
                    shipping.printed = True

            for shipping in shippings:
                # Do not deliver shipping not available (no pick done)
                # Try to reassign move to another existing shipping
                if not shipping.pack_operation_ids:
                    shipping.with_context(no_new_picking=True)._create_backorder()
                    _logger.debug(
                        "Shipping detached from delivery round %s: %s (%s)",
                        delivery_round.id,
                        shipping.id,
                        shipping.name,
                    )
                    # First mark as not printed otherwise constrain will fail
                    # when shipping is detached from delivery round customer
                    shipping.with_context(tracking_disable=True).printed = False
                    shipping.delivery_round_customer_id = False
                    continue

                # Set quantity on all pack operations and deliver
                for pack in shipping.pack_operation_ids:
                    if pack.product_qty > 0:
                        pack.qty_done = pack.product_qty
                        for plot in pack.pack_lot_ids:
                            if plot.qty_todo > 0:
                                plot.qty = plot.qty_todo
                    else:
                        pack.unlink()
                shipping.do_transfer()

            # Detach the pickings that could not be done.
            # When we previously created the backorder on the shipping, if the
            # customer does not accept backorders, all moves have been canceled
            # and this causes the deletion of the round instance customer (see
            # stock.move action_cancel). So to access the pickings from self,
            # we first need to check if self still exists.
            if self.exists():
                pickings = self.picking_ids.filtered(
                    lambda p: p.state not in ("cancel", "done")
                )
                pickings.with_context(tracking_disable=True).write({"printed": True})
                pickings.with_context(no_new_picking=True)._create_backorder()
                _logger.debug(
                    "Pickings detached from delivery round %s: %s",
                    self.delivery_round_id.id,
                    ",".join(pickings.mapped("name")),
                )
                pickings.with_context(tracking_disable=True).write({"printed": False})
                # If all moves have been sent to another picking during
                # backorder creation, recompute state to draft to allow to
                # delete pack operations which happens automaticaly when
                # detached from delivery round
                pickings._compute_state()
                pickings.write({"delivery_round_customer_id": False})
                # If all moves have been sent to another picking during
                # backorder creation, mark it as done
                pickings_empty = pickings.filtered(lambda p: not p.move_lines)
                pickings_empty.write({"printed": True})
                pickings_empty._compute_state()

            # Ensure any backorder is reassigned
            shippings._delay_jobs_action_assign(shippings.mapped("partner_id"))

            # If this customer do not have any linked picking, remove it
            # We perform this step at last to prevent Missing record error
            if self.exists():
                self._remove_if_empty()

        if delivery_round.state == "delivering":
            delivery_round.with_delay(priority=5).recheck_delivery_state()

        if self.exists() and self.delivery_error:
            if background:
                # write a result to the job
                message = _(
                    "Should be delivered manually, could not"
                    " deliver because of %s" % (self.delivery_error,)
                )
                return message
            else:
                # if we raise the error using the normal way, the buttons
                # on the one2many list stop to work...
                self.env.user.notify_warning(
                    _("Error when delivering %s: %s")
                    % (self.display_name, self.delivery_error)
                )

    def _deliver(self, background=True):
        """ Validate all shipping orders that are available
        """
        for icust in self:
            if icust.delivered:
                continue
            if background:
                icust.with_delay(
                    description=_("Deliver customer %s of delivery round %s")
                    % (icust.display_name, icust.delivery_round_id.complete_name),
                    priority=5,
                )._deliver_job()
            else:
                icust._deliver_job()

    def print_deliveryslip(self):
        shippings = self.picking_ids.filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        shipping_done = shippings.filtered(lambda shipping: shipping.state == "done")
        if not shipping_done:
            raise UserError(
                _("The shipping is not part anymore of this delivery round")
            )
        return self.env["report"].get_action(shipping_done, "stock.report_deliveryslip")
