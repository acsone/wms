# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.models import se_index


class SeIndex(se_index.SeIndex):
    def _make_name(self) -> str:
        return super()._make_name().lower()
