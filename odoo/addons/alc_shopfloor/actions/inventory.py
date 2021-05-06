# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _

from odoo.addons.component.core import Component


class InventoryAction(Component):
    """Provide methods to work with inventories

    Several processes have to create inventories at some point,
    for instance when there is a stock issue.
    """

    _name = "shopfloor.inventory.action"
    _inherit = "shopfloor.process.action"
    _usage = "inventory"

    def create_draft_check_empty(self, location, product, ref=None):
        """Create a draft inventory for a product with a zero quantity"""
        if ref:
            name = _("Zero check issue on location {} ({})").format(location.name, ref)
        else:
            name = _("Zero check issue on location {}").format(location.name)
        return self._create_draft_inventory(location, product, name)

    def _inventory_exists(
        self, location, product, package=None, lot=None, states=("draft", "confirm")
    ):
        """Return if an inventory for location and product exist"""
        domain = [
            ("location_id", "=", location.id),
            ("product_id", "=", product.id),
            ("state", "in", states),
        ]
        if package is not None:
            domain.append(("package_id", "=", package.id))
        if lot is not None:
            domain.append(("lot_id", "=", lot.id))
        return self.env["stock.inventory"].search_count(domain)

    def _create_draft_inventory(self, location, product, name, lot=None, package=None):

        vals = {"name": name, "location_id": location.id}
        if package:
            vals.update({"filter": "pack", "package_id": package.id})
        elif lot:
            vals.update({"filter": "lot", "lot_id": lot.id})
        else:
            vals.update({"filter": "product", "product_id": product.id})
        return self.env["stock.inventory"].sudo().create(vals)

    def create_control_stock(self, location, product, package, lot, name=None):
        """Create a draft inventory so a user has to check a location

        If a draft or in progress inventory already exists for the same
        combination of product/package/lot, no inventory is created.
        """
        if not self._inventory_exists(location, product):
            product_name = self._stock_issue_product_description(product, package, lot)

            if not name:
                name = _("Control stock issue in location {} for {}").format(
                    location.name, product_name
                )
            self._create_draft_inventory(
                location, product, name, lot=lot, package=package
            )

    def create_stock_issue(self, move, location, package, lot):
        """Create an inventory for a stock issue

        It reduces the quantity in a location in a way that:
        * assigned move lines in other batch transfers stay assigned.
        * assigned move lines in same batch but already picked stay assigned.
        """
        other_operations = self._stock_issue_get_related_pack_operations(
            move, location, package, lot
        )
        if not lot:
            qty_to_keep = sum(other_operations.mapped("product_qty"))
        else:
            pack_lots = other_operations.mapped("pack_lot_ids")
            pack_lots = pack_lots.filtered(lambda pl, _lot=lot: _lot == pl.lot_id)
            qty_to_keep = sum(pack_lots.mapped("qty_todo"))
        self.create_stock_correction(move, location, package, lot, qty_to_keep)
        move.action_assign()

    def create_stock_correction(self, move, location, package, lot, quantity):
        """Create an inventory with a forced quantity"""
        values = self._stock_correction_inventory_values(
            move, location, package, lot, quantity
        )
        inventory = self.env["stock.inventory"].sudo().create(values)
        inventory.action_start()
        inventory.action_done()

    def _stock_issue_get_related_pack_operations(self, move, location, package, lot):
        """Lookup for all the other operations that match given operation"""
        domain = [
            ("location_id", "=", location.id),
            ("product_id", "=", move.product_id.id),
            ("package_id", "=", package.id),
            ("state", "in", ("assigned", "partially_available")),
        ]
        operations = self.env["stock.pack.operation"].search(domain)
        operations = operations.filtered(
            lambda op, m=move: move in op.mapped("linked_move_operation_ids.move_id")
        )
        if lot:
            operations = operations.filtered(
                lambda op, _lot=lot: _lot in op.mapped("pack_lot_ids.lot_id")
            )
        return operations

    def _stock_correction_inventory_values(
        self, move, location, package, lot, line_qty
    ):
        name = _(
            "{picking.name} stock correction in location {location.name} "
            "for {product_desc}"
        ).format(
            picking=move.picking_id,
            location=location,
            product_desc=self._stock_issue_product_description(
                move.product_id, package, lot
            ),
        )
        line_values = {
            "location_id": location.id,
            "product_id": move.product_id.id,
            "package_id": package.id,
            "prod_lot_id": lot.id,
            "product_qty": line_qty,
        }
        vals = {
            "name": name,
            "line_ids": [(0, 0, line_values)],
        }
        if package:
            vals.update({"filter": "pack", "package_id": package.id})
        elif lot:
            vals.update({"filter": "lot", "lot_id": lot.id})
        else:
            vals.update({"filter": "product", "product_id": move.product_id.id})
        return vals

    def _stock_issue_product_description(self, product, package, lot):
        parts = []
        if package:
            parts.append(package.name)
        parts.append(product.name)
        if lot.name:
            parts.append(_("Lot: ") + lot.name)
        return " - ".join(parts)
