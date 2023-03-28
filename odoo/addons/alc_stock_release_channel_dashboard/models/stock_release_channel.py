# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from odoo import _, api, fields

from odoo.addons.alc_stock_release_channel_pick_allowed.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)

DONE_PICKING_STATES = ("done", "cancel")
TODO_SHIPMENT_STATES = ("draft", "confirmed", "in_progress")


def _format_progress(todo, done):
    return f"{(done / todo) * 100:.0f}%" if todo else "0%"


class StockReleaseChannel(StockReleaseChannelBase):

    kanban_dashboard = fields.Json(
        compute="_compute_kanban_dashboard", compute_sudo=True
    )

    @api.depends("pick_allowed", "pick_allowed_by_picking_type")
    def _compute_kanban_dashboard(self):
        for rec in self:
            (
                picking_types,
                todo_by_pt,
                done_by_pt_and_rc,
                todo_shipment_advices,
                done_shipment_advices,
            ) = rec._kanban_dashboard_data()
            result = []
            for picking_type in picking_types:
                todo = todo_by_pt.get(picking_type.id, 0)
                done = done_by_pt_and_rc.get((picking_type.id, rec.id), 0)
                result.append(
                    rec._kanban_dashboard_picking_type_data(picking_type, todo, done)
                )
            result.append(
                rec._kanban_dashboard_shipment_advice_data(
                    todo_shipment_advices, done_shipment_advices
                )
            )
            rec.kanban_dashboard = json.dumps(result)

    def _kanban_dashboard_data(self):
        picking_types = self.env["stock.picking.type"].search(
            [("release_channel_can_allow_pick", "=", True)]
        )
        todo_by_pt = self._kanban_dashboard_todo_by_picking_type()
        done_by_pt_and_rc = (
            self._kanban_dashboard_done_by_picking_type_and_release_channel()
        )
        todo_shipment_advices = self._kanban_dashboard_todo_shipment_advices()
        done_shipment_advices = self._kanban_dashboard_done_shipment_advices()
        return (
            picking_types,
            todo_by_pt,
            done_by_pt_and_rc,
            todo_shipment_advices,
            done_shipment_advices,
        )

    def _kanban_dashboard_todo_by_picking_type_domain(self):
        return [
            ("release_channel_id", "=", self.id),
            ("scheduled_date", "=", self.process_end_date),
        ]

    def _kanban_dashboard_done_by_picking_type_domain(self):
        todo_domain = self._kanban_dashboard_todo_by_picking_type_domain()
        return todo_domain + [("state", "in", DONE_PICKING_STATES)]

    def _kanban_dashboard_todo_by_picking_type(self):
        result = {}
        for group in self.env["stock.picking"].read_group(
            self._kanban_dashboard_todo_by_picking_type_domain(),
            ["picking_type_id"],
            ["picking_type_id"],
        ):
            result[group.get("picking_type_id")[0]] = group.get("picking_type_id_count")
        return result

    def _kanban_dashboard_done_by_picking_type_and_release_channel(self):
        result = {}
        for group in self.env["stock.picking"].read_group(
            self._kanban_dashboard_done_by_picking_type_domain(),
            ["picking_type_id", "release_channel_id"],
            ["picking_type_id", "release_channel_id"],
            lazy=False,
        ):
            result[
                (group.get("picking_type_id")[0], group.get("release_channel_id")[0])
            ] = group.get("__count")
        return result

    def _kanban_dashboard_todo_shipment_advices(self):
        result = {}
        for group in self.env["shipment.advice"].read_group(
            [
                ("state", "in", TODO_SHIPMENT_STATES),
                ("release_channel_id", "in", self.ids),
            ],
            ["release_channel_id"],
            ["release_channel_id"],
        ):
            result[group.get("release_channel_id")[0]] = group.get(
                "release_channel_id_count"
            )
        return result

    def _kanban_dashboard_done_shipment_advices(self):
        result = {}
        for group in self.env["shipment.advice"].read_group(
            [
                ("state", "=", "in_progress"),
                ("release_channel_id", "in", self.ids),
            ],
            ["release_channel_id"],
            ["release_channel_id"],
        ):
            result[group.get("release_channel_id")[0]] = group.get(
                "release_channel_id_count"
            )
        return result

    def _kanban_dashboard_picking_type_data(self, picking_type, todo, done):
        self.ensure_one()
        progress = _format_progress(todo, done)
        pick_allowed = self._get_picking_type_pick_allowed(picking_type.id)
        return {
            "id": picking_type.id,
            "model": picking_type._name,
            "name": picking_type.name,
            "todo": todo,
            "done": done,
            "progress": progress,
            "pick_allowed": pick_allowed,
        }

    def _kanban_dashboard_shipment_advice_data(
        self, todo_shipment_advices, done_shipment_advices
    ):
        self.ensure_one()
        todo = todo_shipment_advices.get(self.id, 0)
        done = done_shipment_advices.get(self.id, 0)
        progress = _format_progress(todo, done)
        return {
            "model": "shipment.advice",
            "name": "Shipment advices",
            "todo": todo,
            "done": done,
            "progress": progress,
        }

    def button_toggle_locked(self):
        opened = self.filtered(lambda r: r.state == "open")
        locked = self.filtered(lambda r: r.state == "locked")
        opened.write({"state": "locked"})
        locked.write({"state": "open"})

    def _kanban_dashboard_action_open_channel(self):
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
        }

    def _kanban_dashboard_action_open_picking(self, picking_type_id, done=False):
        if done:
            domain = self._kanban_dashboard_done_by_picking_type_domain()
        else:
            domain = self._kanban_dashboard_todo_by_picking_type_domain()
        domain += [("picking_type_id", "=", picking_type_id)]
        return {
            "type": "ir.actions.act_window",
            "name": _("Pickings"),
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": domain,
        }

    def _kanban_dashboard_open_shipment_advice(self, done=False):
        domain = [("release_channel_id", "=", self.id)]
        if done:
            domain.append(("state", "=", "in_progress"))
        else:
            domain.append(("state", "in", ("draft", "confirmed", "in_progress")))
        return {
            "type": "ir.actions.act_window",
            "name": _("Shipment Advices"),
            "res_model": "shipment.advice",
            "view_mode": "tree,form",
            "domain": domain,
        }

    def action_kanban_dashboard_open(self):
        filter_type = self.env.context.get("filter_type")
        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")
        if active_model == self._name:
            return self._kanban_dashboard_action_open_channel()
        if active_model == "stock.picking.type":
            return self._kanban_dashboard_action_open_picking(
                active_id, done=filter_type == "done"
            )
        if active_model == "shipment.advice":
            return self._kanban_dashboard_open_shipment_advice(
                done=filter_type == "done"
            )
        return {}
