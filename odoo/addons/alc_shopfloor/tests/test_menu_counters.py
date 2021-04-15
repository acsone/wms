# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from .test_menu_base import MenuCountersCommonCase


class TestMenuCountersCommonCase(MenuCountersCommonCase):
    def test_menu_search(self):
        expected_counters = {
            self.menu1.id: {
                "operations_count": 2,
                "picking_count": 2,
                "priority_operations_count": 2,
                "priority_picking_count": 2,
            },
        }
        response = self.service.dispatch("search")
        self._assert_menu_response(
            response,
            self.menu_items.sorted("sequence"),
            expected_counters=expected_counters,
        )
