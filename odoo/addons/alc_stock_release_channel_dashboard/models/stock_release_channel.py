# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from collections import defaultdict

from odoo import _, api, fields

from odoo.addons.alc_stock_release_channel_pick_allowed.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)

WAITING_PICKING_STATES = ("confirmed", "waiting")
DONE_PICKING_STATES = ("done", "cancel")
TODO_SHIPMENT_STATES = ("draft", "confirmed", "in_progress")


def _format_progress(todo, done):
    return f"{(done / todo) * 100:.0f}%" if todo else "0%"


class StockReleaseChannel(StockReleaseChannelBase):

    kanban_dashboard = fields.Json(
        compute="_compute_kanban_dashboard", compute_sudo=True
    )
    count_picking_release_ready = fields.Integer(compute="_compute_count_release_ready")
    count_move_release_ready = fields.Integer(compute="_compute_count_release_ready")

    def _get_picking_ids_per_channel(self, field):
        domains = self._field_picking_domains()
        domain = domains.get(field)
        data = self.env["stock.picking"].read_group(
            domain + [("release_channel_id", "in", self.ids)],
            ["release_channel_id", "picking_ids:array_agg(id)"],
            ["release_channel_id"],
        )
        return {
            row["release_channel_id"][0]: row["picking_ids"]
            for row in data
            if row["release_channel_id"]
        }

    def _compute_count_field(self, field):
        move_field = field.replace("picking", "move")
        picking_ids_per_channel = self._get_picking_ids_per_channel(field)
        stock_move_model = self.env["stock.move"]
        for channel in self:
            picking_ids = picking_ids_per_channel.get(channel.id, [])
            channel[field] = len(picking_ids)
            channel[move_field] = stock_move_model.search_count(
                [("picking_id", "in", picking_ids), ("state", "!=", "cancel")]
            )

    def _compute_count_release_ready(self):
        self._compute_count_field("count_picking_release_ready")

    def button_show_picking_out(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Outgoing Pickings"),
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [
                ("release_channel_id", "=", self.id),
                ("picking_type_code", "=", "outgoing"),
            ],
            "context": {"search_default_available": 1, **self.env.context},
        }

    def button_show_picking_int(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Internal Pickings"),
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [
                ("release_channel_id", "=", self.id),
                ("picking_type_code", "=", "internal"),
            ],
            "context": {"search_default_available": 1, **self.env.context},
        }

    @api.depends("pick_allowed", "pick_allowed_by_picking_type")
    def _compute_kanban_dashboard(self):
        picking_types = self.env["stock.picking.type"]._get_visible_in_dashboard()
        todo_by_rc_by_pt = self._count_picking_todo_by_type_id_by_release_id()
        started_by_rc_by_pt = self._count_picking_started_by_type_id_by_release_id()
        done_by_rc_by_pt = self._count_picking_done_by_type_id_by_release_id()
        waiting_by_rc_by_pt = self._count_picking_waiting_by_type_id_by_release_id()
        for rec in self:
            result = []
            if rec.state in ("delivering" "delivering_error" "delivered"):
                todo_shipment_advices = rec._count_shipment_advices_todo_by_release_id()
                done_shipment_advices = rec._count_shipment_advices_done_by_release_id()
                result.append(
                    rec._kanban_dashboard_shipment_advice_data(
                        todo_shipment_advices, done_shipment_advices
                    )
                )
            else:
                todo_by_pt = todo_by_rc_by_pt.get(rec.id, {})
                started_by_pt = started_by_rc_by_pt.get(rec.id, {})
                done_by_pt = done_by_rc_by_pt.get(rec.id, {})
                waiting_by_pt = waiting_by_rc_by_pt.get(rec.id, {})
                for picking_type in picking_types:
                    todo = todo_by_pt.get(picking_type.id, 0)
                    started = started_by_pt.get(picking_type.id, 0)
                    done = done_by_pt.get(picking_type.id, 0)
                    waiting = waiting_by_pt.get(picking_type.id, 0)
                    result.append(
                        rec._kanban_dashboard_picking_type_data(
                            picking_type, todo, started, done, waiting
                        )
                    )
            rec.kanban_dashboard = json.dumps(
                {
                    "data": result,
                    "tags": rec.stock_release_channel_tag_ids.mapped("name"),
                }
            )

    def _kanban_dashboard_data(self):
        picking_types = self.env["stock.picking.type"].search(
            [("release_channel_can_allow_pick", "=", True)]
        )
        todo_by_pt = self._count_picking_todo_by_type_id_by_release_id()
        done_by_pt_and_rc = self._count_picking_done_by_type_id_by_release_id()
        todo_shipment_advices = self._count_shipment_advices_todo_by_release_id()
        done_shipment_advices = self._count_shipment_advices_done_by_release_id()
        return (
            picking_types,
            todo_by_pt,
            done_by_pt_and_rc,
            todo_shipment_advices,
            done_shipment_advices,
        )

    def _count_picking_todo_by_type_id_by_release_id_domain(self):
        """
        Pickings to do:

        - picking not done: date_done=False
        - picking done in the current day
        """
        picking_type_ids = self.env[
            "stock.picking.type"
        ]._get_ids_visible_in_dashboard()
        return [
            ("release_channel_id", "in", self.ids),
            ("picking_type_id", "in", picking_type_ids),
            ("state", "!=", "cancel"),
            "|",
            ("date_done", "=", False),
            ("date_done", ">", fields.Datetime.now().replace(hour=0, minute=0)),
        ]

    def _count_picking_started_by_type_id_by_release_id_domain(self):
        todo_domain = self._count_picking_todo_by_type_id_by_release_id_domain()
        return todo_domain + [
            ("started", "=", True),
            ("state", "not in", DONE_PICKING_STATES),
        ]

    def _count_picking_done_by_type_id_by_release_id_domain(self):
        todo_domain = self._count_picking_todo_by_type_id_by_release_id_domain()
        return todo_domain + [("state", "in", DONE_PICKING_STATES)]

    def _count_picking_waiting_by_type_id_by_release_id_domain(self):
        todo_domain = self._count_picking_todo_by_type_id_by_release_id_domain()
        return todo_domain + [("state", "in", WAITING_PICKING_STATES)]

    def _count_pickings_by_type_id_by_release_id(self, domain):
        """Count pickings by picking type and release channel."""
        result = defaultdict(dict)
        for group in self.env["stock.picking"].read_group(
            domain,
            ["id:count", "picking_type_id", "release_channel_id"],
            ["release_channel_id", "picking_type_id"],
            lazy=False,
        ):
            result[group.get("release_channel_id")[0]][
                group.get("picking_type_id")[0]
            ] = group.get("__count")
        return result

    def _count_picking_todo_by_type_id_by_release_id(self):
        return self._count_pickings_by_type_id_by_release_id(
            self._count_picking_todo_by_type_id_by_release_id_domain()
        )

    def _count_picking_started_by_type_id_by_release_id(self):
        return self._count_pickings_by_type_id_by_release_id(
            self._count_picking_started_by_type_id_by_release_id_domain()
        )

    def _count_picking_done_by_type_id_by_release_id(self):
        return self._count_pickings_by_type_id_by_release_id(
            self._count_picking_done_by_type_id_by_release_id_domain()
        )

    def _count_picking_waiting_by_type_id_by_release_id(self):
        return self._count_pickings_by_type_id_by_release_id(
            self._count_picking_waiting_by_type_id_by_release_id_domain()
        )

    def _count_shipment_advices_todo_by_release_id(self):
        return len(self.in_process_shipment_advice_ids.loaded_picking_ids)

    def _count_shipment_advices_done_by_release_id(self):
        return len(
            self.in_process_shipment_advice_ids.loaded_picking_ids.filtered(
                lambda p: p.state in ("cancel", "done")
            )
        )

    def _kanban_dashboard_picking_type_data(
        self, picking_type, todo, started, done, waiting
    ):
        self.ensure_one()
        progress = _format_progress(todo, done)
        waiting_progress = _format_progress(todo, waiting)
        pick_allowed = self._get_picking_type_pick_allowed(picking_type.id)
        return {
            "id": picking_type.id,
            "model": picking_type._name,
            "name": picking_type.name,
            "todo": todo,
            "started": started,
            "done": done,
            "waiting": waiting,
            "progress": progress,
            "waiting_progress": waiting_progress,
            "pick_allowed": pick_allowed,
        }

    def _kanban_dashboard_shipment_advice_data(self, todo, done):
        self.ensure_one()
        progress = _format_progress(todo, done)
        return {
            "model": "shipment.advice",
            "name": _("Shipment advices"),
            "todo": todo,
            "done": done,
            "progress": progress,
        }

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
            domain = self._count_picking_done_by_type_id_by_release_id_domain()
        else:
            domain = self._count_picking_todo_by_type_id_by_release_id_domain()
        domain += [("picking_type_id", "=", picking_type_id)]
        return {
            "type": "ir.actions.act_window",
            "name": _("Pickings"),
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": domain,
        }

    def _kanban_dashboard_open_shipment_advice(self, done=False):
        if done:
            pickings = self.in_process_shipment_advice_ids.loaded_picking_ids
            domain = [("id", "in", pickings.ids)]
            return {
                "type": "ir.actions.act_window",
                "name": _("Shipment Advice"),
                "res_model": "stock.picking",
                "view_mode": "tree,form",
                "domain": domain,
            }
        return {
            "type": "ir.actions.act_window",
            "name": _("Shipment Advices"),
            "res_model": "shipment.advice",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.in_process_shipment_advice_ids.ids)],
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
