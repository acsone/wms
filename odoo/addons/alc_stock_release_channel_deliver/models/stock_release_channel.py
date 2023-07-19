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

    def action_delivering(self):
        self._check_is_action_delivering_allowed()
        self.write({"state": "delivering"})
        for rec in self:
            rec.with_delay(
                description=_("Delivering release channel %(name)s.", name=rec.name)
            )._action_deliver()

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
        self._plan_shipments()

    def _shipment_advice_auto_process_notify_success(self):
        self.ensure_one()
        shipment_states = set(self.shipment_advice_ids.mapped("state"))
        not_done_states = ["confirmed", "in_progress"]
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

    def _shipment_advice_auto_process_notify_error(self, error, related_object):
        self.ensure_one()
        if self.state == "delivering_error":
            return
        self.action_delivering_error()
        self.delivering_error = self._get_delivering_error_message(
            error, related_object
        )

    @api.depends("state")
    def _compute_is_action_lock_allowed(self):
        res = super()._compute_is_action_lock_allowed()
        for rec in self:
            rec.is_action_lock_allowed = (
                rec.is_action_lock_allowed or rec.state == "delivering_error"
            )
        return res
