# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class ShopfloorMenu(Component):
    _inherit = "shopfloor.menu"

    def _convert_one_record(self, record):
        values = super(ShopfloorMenu, self)._convert_one_record(record)
        if record.picking_type_ids:
            counters = self._get_operation_counters(record)
            values.update(counters)
        return values

    def _get_operation_counters(self, record):
        """Lookup for all lines per menu item and compute counters.
        """
        # TODO: maybe to be improved w/ raw SQL as this run for each menu item
        # and it's called every time the menu is opened/gets refreshed
        move_line_search = self._actions_for(
            "search_pack_operation", picking_types=record.picking_type_ids
        )
        locations = record.picking_type_ids.mapped("default_location_src_id")
        lines_per_menu = move_line_search.search_pack_operations_by_location(locations)
        return move_line_search.counters_for_lines(lines_per_menu)

    def _one_record_parser(self, record):
        parser = super(ShopfloorMenu, self)._one_record_parser(record)
        if not record.picking_type_ids:
            return parser
        return parser + [
            ("picking_type_ids:picking_types", ["id", "name"]),
        ]


class ShopfloorMenuValidatorResponse(Component):
    """Validators for the Menu endpoints responses"""

    _inherit = "shopfloor.menu.validator.response"

    @property
    def _record_schema(self):
        schema = super(ShopfloorMenuValidatorResponse, self)._record_schema
        schema.update(
            {
                "picking_types": self.schemas._schema_list_of(
                    self._picking_type_schema, required=False, nullable=True
                )
            }
        )
        schema.update(self.schemas.move_operations_counters())
        return schema

    @property
    def _picking_type_schema(self):
        return {
            "id": {"coerce": to_int, "required": True, "type": "integer"},
            "name": {"type": "string", "nullable": False, "required": True},
        }
