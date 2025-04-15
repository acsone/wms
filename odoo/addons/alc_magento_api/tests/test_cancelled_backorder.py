# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from .common import TestFacadePickings


class TestCancelledBackorder(TestFacadePickings):
    @freeze_time("1900-01-01")
    def test_backorders_cancelled(self):
        cancelled_backoder_facade = self._get_service_facade("cancelled_backorder")
        result, _error, _location = cancelled_backoder_facade(date="1900-01-01")
        # use search to get the ids in the order expected by the facade
        pickings_cancelled = self.env["stock.picking"].search(
            [("id", "in", [self.picking_half.id, self.picking_cancel.id])]
        )
        expeced_result = f"""<?xml version="1.0" encoding="UTF-8" ?>
        <backorders_cancelled>
            <order><internal_order_id>{pickings_cancelled[0].id}</internal_order_id>
                <item>
                    <qty_ordered>1.0</qty_ordered>
                    <date_cancelled>{pickings_cancelled[0].date.date()}</date_cancelled>
                    <sku>CNL</sku>
                </item>
            </order>
            <order>
                <internal_order_id>{pickings_cancelled[1].id}</internal_order_id>
                <item>
                    <qty_ordered>1.0</qty_ordered>
                    <date_cancelled>{pickings_cancelled[1].date.date()}</date_cancelled>
                    <sku>CNL</sku>
                </item>
            </order>
        </backorders_cancelled>"""
        self.assertXmlEqual(expeced_result, result)
