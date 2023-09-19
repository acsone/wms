# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    def _get_delivery_date(self):
        """
        Get the delivery date from given picking.

        As the delivery date doesn't exist in Odoo, we use the date_done
        when the state is 'done'.
        :param picking: stock.picking
        :return: str
        """
        delivery_date = None
        if self.state == "done":
            delivery_date = self.date_done or self.write_date
        if delivery_date:
            delivery_date = delivery_date.date()
        return delivery_date
