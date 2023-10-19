from odoo.http import request

from odoo.addons.stock_barcode.controllers import stock_barcode


class StockBarcodeController(stock_barcode.StockBarcodeController):
    def _try_new_internal_picking(self, barcode):
        """If barcode represents a location, open a new picking from this location."""
        scan_location = request.env["stock.location"].search(
            [("barcode", "=", barcode), ("usage", "=", "internal")], limit=1
        )
        if scan_location:
            # set the right picking type by looking on scanned location source
            internal_picking_type = scan_location.get_barcode_picking_type_id()
            if internal_picking_type:
                dest_loc = internal_picking_type.default_location_dest_id
                # Create and confirm an internal picking
                picking = request.env["stock.picking"].create(
                    {
                        "picking_type_id": internal_picking_type[0].id,
                        "location_id": scan_location.id,
                        "location_dest_id": dest_loc.id,
                    }
                )
                picking.action_confirm()
                return picking._get_std_view_action()
        return super()._try_new_internal_picking(barcode=barcode)

    def _try_open_picking(self, barcode):
        """If barcode represents a picking, open it."""
        res = super()._try_open_picking(barcode=barcode)
        if res:
            action = (
                request.env["stock.picking"]
                .sudo()
                ._get_std_view_action(res["action"]["context"]["active_id"])
            )
            return action
        return False
