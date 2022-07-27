# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class VeterinaryGroupService(Component):
    """
    Get access to veterinary groups informations
    """

    _inherit = "authenticated_partner.mixin"
    _name = "veterinary.group.service"
    _collection = "shopinvader.backend"
    _usage = "veterinary_groups"

    @restapi.method(
        [(["/"], "GET")],
        output_param=restapi.CerberusValidator("_search_output_schema"),
    )
    def search(self, **params):
        """Retrieve informations of all veterinary groups"""
        return self._search()

    ############
    # validators
    ############
    def _search_output_schema(self):
        return {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._veterinary_group_schema},
            },
        }

    @property
    def _veterinary_group_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "name": {"type": "string", "required": True, "nullable": False},
            "color": {"type": "string", "required": False, "nullable": True},
            "is_alcyonnaire": {"type": "boolean", "required": True, "nullable": False},
            "sequence": {"type": "integer", "required": True, "nullable": False},
        }

    ################
    # implementation
    ################
    def _search(self):
        groups = self.env["veterinary.group"].search([])
        return {
            "size": len(groups),
            "data": [self._group_to_json(g) for g in groups],
        }

    def _group_to_json(self, group):
        return dict(
            id=group.id,
            name=group.name,
            color=group.display_color or None,
            is_alcyonnaire=group.is_alcyonnaire,
            sequence=group.sequence,
        )
