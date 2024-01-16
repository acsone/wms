# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.stock_release_channel_shipment_advice.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)

from .shipment_advice import ShipmentAdvice


class StockReleaseChannel(StockReleaseChannelBase):

    state = fields.Selection(
        selection_add=[
            ("delivering", "Delivering"),
            ("delivering_error", "Delivering Error"),
            ("delivered", "Delivered"),
        ],
        help="The state allows you to control the availability of the release channel.\n"
        "* Open: Manual and automatic picking assignment to the release is effective "
        "and release operations are allowed.\n "
        "* Locked: Release operations are forbidden. (Assignement processes are "
        "still working)\n"
        "* Delivering: A background task is running to automatically deliver ready shipments\n"
        "* Delivering Error: An error occurred in the delivery background task\n"
        "* Delivered: Ready transfers are delivered\n"
        "* Asleep: Assigned pickings not processed are unassigned from the release "
        "channel.\n",
    )

    is_action_delivering_allowed = fields.Boolean(
        compute="_compute_is_action_delivering_allowed"
    )
    is_action_delivering_error_allowed = fields.Boolean(
        compute="_compute_is_action_delivering_error_allowed"
    )
    is_action_delivered_allowed = fields.Boolean(
        compute="_compute_is_action_delivered_allowed"
    )
    delivering_error = fields.Text(readonly=True)
    in_process_shipment_advice_ids = fields.One2many[ShipmentAdvice](
        compute="_compute_in_process_shipment_advice_ids"
    )

    @api.depends("shipment_advice_ids", "process_end_date")
    def _compute_in_process_shipment_advice_ids(self):
        shipment_advice_model = self.env["shipment.advice"]
        for rec in self:
            rec.in_process_shipment_advice_ids = shipment_advice_model.search(
                [
                    ("in_release_channel_auto_process", "=", True),
                    ("release_channel_id", "=", rec.id),
                ]
            )

    @api.depends("state", "picking_to_plan_ids", "shipment_planning_method")
    def _compute_is_action_delivering_allowed(self):
        for rec in self:
            rec.is_action_delivering_allowed = (
                rec.state
                in (
                    "locked",
                    "delivering_error",
                )
                and bool(rec.picking_to_plan_ids)
                and rec.shipment_planning_method != "none"
            )

    @api.depends("state")
    def _compute_is_action_delivering_error_allowed(self):
        for rec in self:
            rec.is_action_delivering_error_allowed = rec.state == "delivering"

    @api.depends("state")
    def _compute_is_action_delivered_allowed(self):
        for rec in self:
            rec.is_action_delivered_allowed = rec.state == "delivering"

    def _check_is_action_delivering_allowed(self):
        for rec in self:
            if not rec.picking_to_plan_ids:
                raise UserError(
                    _("No picking to deliver for channel %(name)s.", name=rec.name)
                )
            started_pickings = rec.picking_ids.filtered("started")
            if started_pickings:
                raise UserError(
                    _(
                        "One of the pickings to deliver for channel %(name)s is started."
                        "\nPlease finish it manually or cancel its start to be able to deliver.\n"
                        "%(pickings)s",
                        name=rec.name,
                        pickings=", ".join(started_pickings.mapped("name")),
                    )
                )
            shipping_moves_to_unrelease = self._shipping_moves_to_unrelease()
            shipping_unrelease_not_allowed = shipping_moves_to_unrelease.filtered(
                lambda m: not m.unrelease_allowed
            ).picking_id
            if shipping_unrelease_not_allowed:
                picking_moves_to_unrelease = self._picking_moves_to_unrelease()
                picking_moves_to_unrelease = picking_moves_to_unrelease.filtered(
                    lambda p: p.state not in ("confirmed", "partially_available")
                ).picking_id
                raise UserError(
                    _(
                        "There are some preparations that have not been completed."
                        "If you choose to proceed, these preparations need to be unreleased.\n"
                        "Please handle them manually before proceeding with the delivery."
                        "\n\n%(shipping)s\n%(pickings)s",
                        shipping=", ".join(
                            shipping_unrelease_not_allowed.mapped("name")
                        ),
                        pickings=", ".join(picking_moves_to_unrelease.mapped("name")),
                    )
                )
            if not rec.is_action_delivering_allowed:
                raise UserError(
                    _(
                        "Action 'Delivering' is not allowed for channel %(name)s.",
                        name=rec.name,
                    )
                )

    def _check_is_action_delivering_error_allowed(self):
        for rec in self:
            if not rec.is_action_delivering_error_allowed:
                raise UserError(
                    _(
                        "Action 'Delivering Error' is not allowed for channel %(name)s.",
                        name=rec.name,
                    )
                )

    def _check_is_action_delivered_allowed(self):
        for rec in self:
            if not rec.is_action_delivered_allowed:
                raise UserError(
                    _(
                        "Action 'Delivered' is not allowed for channel %(name)s.",
                        name=rec.name,
                    )
                )

    def _picking_moves_to_unrelease(self):
        self.ensure_one()
        return self.env["stock.move"].search(
            [
                ("picking_type_id.code", "=", "internal"),
                ("picking_id.release_channel_id", "=", self.id),
                ("state", "not in", ("cancel", "done")),
            ]
        )

    def _shipping_moves_to_unrelease(self):
        self.ensure_one()
        return self._picking_moves_to_unrelease().move_dest_ids

    def _picking_to_unrelease_cancel_start(self):
        # unset "printed" on all preparation confirmed moves
        # otherwise the unrlease will not be allowed
        picking_moves_to_unrelease = self._picking_moves_to_unrelease()
        picking_to_unrelease = picking_moves_to_unrelease.filtered(
            lambda m: m.state in ("confirmed", "partially_available")
            and m.picking_id.state != "assigned"
        ).picking_id
        picking_to_unrelease.printed = False

    def action_delivering(self):
        self.ensure_one()
        self._picking_to_unrelease_cancel_start()
        self._check_is_action_delivering_allowed()
        shipping_moves_to_unrelease = self._shipping_moves_to_unrelease()
        if shipping_moves_to_unrelease:
            return {
                "name": _("Confirm delivery"),
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "stock.release.channel.deliver.check.wizard",
                "target": "new",
                "context": {"default_release_channel_id": self.id, **self.env.context},
            }
        self.write({"state": "delivering", "delivering_error": False})
        self.with_delay(
            description=_("Delivering release channel %(name)s.", name=self.name)
        )._action_deliver()
        return {}

    def action_delivering_error(self):
        self._check_is_action_delivering_error_allowed()
        self.write({"state": "delivering_error"})
        self.env.user.notify_danger(
            message=_(
                "An error occurred in the delivery background task for channel %(name)s",
                name=self.display_name,
            ),
            title="Delivering Error",
            sticky=True,
        )

    def action_delivered(self):
        self._check_is_action_delivered_allowed()
        self.write({"state": "delivered"})
        # after deliver, we need to unrelease backorders so they can be assigned
        # to release channel later
        self.unrlease_backorders()
        self.env.user.notify_success(
            message=_(
                "The delivery background task is done for channel %(name)s",
                name=self.display_name,
            ),
            title="Delivering done",
            sticky=True,
        )

    def _action_deliver(self):
        self.ensure_one()
        shipment_advice = self.in_process_shipment_advice_ids.filtered(
            lambda s: s.state in ("in_progress", "error")
        )
        if shipment_advice and len(shipment_advice) == 1:
            shipment_advice.with_delay(
                description=_(
                    "Automatically process the shipment advice %(name)s.",
                    name=shipment_advice.name,
                )
            )._auto_process()
        else:
            self._plan_shipments()

    def _shipment_advice_auto_process_notify_success(self):
        self.ensure_one()
        shipment_states = set(self.in_process_shipment_advice_ids.mapped("state"))
        not_done_states = ["confirmed", "in_progress", "in_process", "error"]
        if any(not_done_state in shipment_states for not_done_state in not_done_states):
            return
        self.action_delivered()

    @api.model
    def _get_delivering_error_message(self, error, related_object):
        return _(
            "An error occurred while processing the delivery automatically:\n- %(related_object_name)s: %(error)s",
            related_object_name=related_object.display_name,
            error=str(error),
        )

    def _shipment_advice_auto_process_notify_error(self, error_message):
        self.ensure_one()
        if self.state == "delivering_error":
            return
        self.action_delivering_error()
        self.delivering_error = error_message

    @api.depends("state")
    def _compute_is_action_lock_allowed(self):
        res = super()._compute_is_action_lock_allowed()
        for rec in self:
            rec.is_action_lock_allowed = (
                rec.is_action_lock_allowed or rec.state == "delivering_error"
            )
        return res

    @api.depends("state")
    def _compute_is_action_sleep_allowed(self):
        res = super()._compute_is_action_sleep_allowed()
        for rec in self:
            rec.is_action_sleep_allowed = (
                rec.is_action_sleep_allowed or rec.state == "delivered"
            )
        return res

    def unrelease_picking(self):
        shipping_moves_to_unrelease = self._shipping_moves_to_unrelease()
        shipping_moves_to_unrelease.unrelease(safe_unrelease=True)

    def unrlease_backorders(self):
        backorders = (
            self.in_process_shipment_advice_ids.loaded_picking_ids.backorder_ids
        )
        backorders.unrelease(safe_unrelease=True)
