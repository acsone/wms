# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.modules.module import get_resource_path
from odoo.tests.common import TransactionCase


class TestDeliveryWindowImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Create 3 partners:

        * A: 1 DW on monday 10-12
        * B: 1 DW on friday 14-15
        * C: No delivery window
        """
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.AlcDeliveryWindow = cls.env["toursolver.delivery.window"]
        cls.AlcDeliveryWindowImporter = cls.env["alc.delivery.window.importer"]
        cls.monday = cls.env.ref("base_time_window.time_weekday_monday")
        cls.friday = cls.env.ref("base_time_window.time_weekday_friday")
        cls.partner_a = cls.env["res.partner"].create({"name": "A", "ref": "REFA"})
        cls.AlcDeliveryWindow.create(
            {
                "partner_id": cls.partner_a.id,
                "time_window_start": 10.0,
                "time_window_end": 12.0,
                "time_window_weekday_ids": [(4, cls.monday.id)],
            }
        )

        cls.partner_b = cls.env["res.partner"].create({"name": "B", "ref": "REFB"})
        cls.AlcDeliveryWindow.create(
            {
                "partner_id": cls.partner_b.id,
                "time_window_start": 14.0,
                "time_window_end": 15.0,
                "time_window_weekday_ids": [(4, cls.friday.id)],
            }
        )
        cls.partner_c = cls.env["res.partner"].create({"name": "C", "ref": "REFC"})
        cls.partner_d = cls.env["res.partner"].create({"name": "D", "ref": "REFD"})

    def _do_import(self, filename):
        file_path = get_resource_path(
            "alc_toursolver_delivery_window_import", "tests", "resources", filename
        )
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read())

        wizard = self.AlcDeliveryWindowImporter.create({"document": content})
        wizard.doit()

    def test_import_xlsx(self):
        self._do_import("test_import_1.xlsx")
        # no delivery windows specified for partner a -> existing are removed
        self.assertFalse(self.partner_a.toursolver_delivery_window_ids)
        # other delivery window for partner b -> new created
        dw = self.partner_b.toursolver_delivery_window_ids
        self.assertEqual(2, len(dw))
        self.assertEqual(self.monday, dw.mapped("time_window_weekday_ids"))
        # On partner C (no DW berore import), we have now 2 DW for all the days
        # (At import DW are grouped by start and end)
        self.assertEqual(2, len(self.partner_c.toursolver_delivery_window_ids))
        self.assertEqual(
            5,
            len(
                self.partner_c.toursolver_delivery_window_ids[0].time_window_weekday_ids
            ),
        )
        self.assertEqual(
            5,
            len(
                self.partner_c.toursolver_delivery_window_ids[1].time_window_weekday_ids
            ),
        )
