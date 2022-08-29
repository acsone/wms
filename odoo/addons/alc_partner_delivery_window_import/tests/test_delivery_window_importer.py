# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.modules.module import get_resource_path
from odoo.tests.common import SavepointCase


class TestDeliveryWindowImport(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """
        Create 3 partners:
        * A: 1 DW on monday 10-12
        * B: 1 DW on friday 14-15
        * C: No delivery window
        """
        super(TestDeliveryWindowImport, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.AlcDeliveryWindow = cls.env["alc.delivery.window"]
        cls.AlcDeliveryWindowImporter = cls.env["alc.delivery.window.importer"]
        cls.monday = cls.env.ref(
            "alc_partner_delivery_window.alc_delivery_weed_day_monday"
        )
        cls.friday = cls.env.ref(
            "alc_partner_delivery_window.alc_delivery_weed_day_friday"
        )
        cls.partner_a = cls.env["res.partner"].create({"name": "A", "ref": "REFA"})
        cls.AlcDeliveryWindow.create(
            {
                "partner_id": cls.partner_a.id,
                "start": 10.0,
                "end": 12.0,
                "week_day_ids": [(4, cls.monday.id)],
            }
        )

        cls.partner_b = cls.env["res.partner"].create({"name": "B", "ref": "REFB"})
        cls.AlcDeliveryWindow.create(
            {
                "partner_id": cls.partner_b.id,
                "start": 14.0,
                "end": 15.0,
                "week_day_ids": [(4, cls.friday.id)],
            }
        )
        cls.partner_c = cls.env["res.partner"].create({"name": "C", "ref": "REFC"})
        cls.partner_d = cls.env["res.partner"].create({"name": "D", "ref": "REFD"})

    def _do_import(self, filename):
        file_path = get_resource_path(
            "alc_partner_delivery_window_import", "tests", "resources", filename
        )
        with open(file_path, "rb") as f:
            # remove pylint deprecated once on py3
            # pylint: disable=deprecated-method
            content = base64.encodestring(f.read())

        wizard = self.AlcDeliveryWindowImporter.create({"document": content})

        wizard.doit()

    def test_import_xlsx(self):
        self._do_import("test_import_1.xlsx")
        # no delivery windows specified for partner a -> existing are removed
        self.assertFalse(self.partner_a.alc_delivery_window_ids)
        # other delivery window for partner b -> new created
        dw = self.partner_b.alc_delivery_window_ids
        self.assertEqual(2, len(dw))
        self.assertEqual(self.monday, dw.mapped("week_day_ids"))
        # On partner C (no DW berore import), we have now 2 DW for all the days
        # (At import DW are grouped by start and end)
        self.assertEqual(2, len(self.partner_c.alc_delivery_window_ids))
        self.assertEqual(5, len(self.partner_c.alc_delivery_window_ids[0].week_day_ids))
        self.assertEqual(5, len(self.partner_c.alc_delivery_window_ids[1].week_day_ids))
        # partner D has no DW since it's not a TOP400
        self.assertFalse(self.partner_d.alc_delivery_window_ids)
