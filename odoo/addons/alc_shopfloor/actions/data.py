# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields

from odoo.addons.component.core import Component
from odoo.addons.shopfloor_base.utils import ensure_model


class DataAction(Component):
    _inherit = "shopfloor.data.action"

    @ensure_model("stock.location")
    def location(self, record, **kw):
        return self._jsonify(
            record.with_context(location=record.id), self._location_parser, **kw
        )

    def locations(self, record, **kw):
        return self.location(record, multi=True)

    @property
    def _location_parser(self):
        return [
            "id",
            "name",
            # Fallback to name if barcode is not valued.
            ("barcode", lambda rec, fname: rec[fname] if rec[fname] else rec.name),
        ]

    @ensure_model("stock.picking")
    def picking(self, record, **kw):
        return self._jsonify(record, self._picking_parser, **kw)

    def pickings(self, record, **kw):
        return self.picking(record, multi=True)

    @property
    def _picking_parser(self):
        return [
            "id",
            "name",
            "origin",
            "note",
            ("partner_id:partner", self._partner_parser),
            ("carrier_id:carrier", self._simple_record_parser()),
            "operation_count",
            "total_weight:weight",
            "min_date:scheduled_date",
        ]

    @ensure_model("stock.quant.package")
    def package(self, record, picking=None, with_packaging=False, **kw):
        """Return data for a stock.quant.package

        If a picking is given, it will include the number of lines of the package
        for the picking.
        """
        parser = self._package_parser
        if with_packaging:
            parser += self._package_packaging_parser
        data = self._jsonify(record, parser, **kw)
        # handle special cases
        if data and picking:
            # TODO: exclude canceled and done?
            lines = picking.pack_operation_ids.filtered(
                lambda l: l.package_id == record
            )
            data.update({"operation_count": len(lines)})
        return data

    def packages(self, records, picking=None, **kw):
        return [self.package(rec, picking=picking, **kw) for rec in records]

    @property
    def _package_parser(self):
        return [
            "id",
            "name",
            "shopfloor_weight:weight",
            ("package_storage_type_id:storage_type", ["id", "name"]),
        ]

    @property
    def _package_packaging_parser(self):
        return [
            ("packaging_id:packaging", self._packaging_parser),
        ]

    @ensure_model("product.packaging")
    def packaging(self, record, **kw):
        return self._jsonify(record, self._packaging_parser, **kw)

    def packaging_list(self, record, **kw):
        return self.packaging(record, multi=True)

    @property
    def _packaging_parser(self):
        return [
            "id",
            ("packaging_type_id:name", lambda rec, fname: rec.packaging_type_id.name),
            ("packaging_type_id:code", lambda rec, fname: rec.packaging_type_id.code),
            "qty",
        ]

    @ensure_model("product.packaging")
    def delivery_packaging(self, record, **kw):
        return self._jsonify(record, self._delivery_packaging_parser, **kw)

    def delivery_packaging_list(self, records, **kw):
        return self.delivery_packaging(records, multi=True)

    @property
    def _delivery_packaging_parser(self):
        return [
            "id",
            "name",
            (
                "packaging_type_id:packaging_type",
                lambda rec, fname: rec.packaging_type_id.display_name,
            ),
            "barcode",
        ]

    @ensure_model("stock.production.lot")
    def lot(self, record, **kw):
        return self._jsonify(record, self._lot_parser, **kw)

    def lots(self, record, **kw):
        return self.lot(record, multi=True)

    @property
    def _lot_parser(self):
        return self._simple_record_parser() + ["ref"]

    @ensure_model("stock.pack.operation")
    def _operation(self, record, with_picking=False, **kw):
        record = record.with_context(location=record.location_id.id)
        parser = self._pack_operation_parser
        if with_picking:
            parser += [("picking_id:picking", self._picking_parser)]
        data = self._jsonify(record, parser)
        if record.product_id:
            data["type"] = "product"
        elif record.package_id:
            data["type"] = "package"
        if data:
            data.update(
                {
                    # cannot use sub-parser here
                    # because result might depend on picking
                    "package_src": self.package(
                        record.package_id, record.picking_id, **kw
                    ),
                    "package_dest": self.package(
                        record.result_package_id.with_context(
                            picking_id=record.picking_id.id
                        ),
                        record.picking_id,
                        **kw
                    ),
                }
            )
        res = [data]
        if record.pack_lot_ids:
            data["type"] = "lot"
            res = []
            for pack_lot in record.pack_lot_ids:
                data_copy = data.copy()
                data_copy.update(self._pack_operation_lot(pack_lot))
                res.append(data_copy)
        return res

    def operations(self, records, **kw):
        res = []
        for rec in records:
            res.extend(self._operation(rec, **kw))
        return res

    @property
    def _pack_operation_parser(self):
        return [
            "id",
            "qty_done",
            "is_done",
            ("product_qty:quantity"),
            (
                "product_id:product",
                lambda rec, fname: self.product(
                    rec.product_id or rec.package_id.single_product_id
                ),
            ),
            ("location_id:location_src", self._location_parser),
            ("location_dest_id:location_dest", self._location_parser),
            "priority",
        ]

    @ensure_model("stock.pack.operation.lot")
    def _pack_operation_lot(self, record):
        return self._jsonify(record, self._pack_operation_lot_parser)

    @property
    def _pack_operation_lot_parser(self):
        return [("lot_id:lot", self._lot_parser), "qty_todo:quantity", "qty:qty_done"]

    @ensure_model("product.product")
    def product(self, record, **kw):
        return self._jsonify(record, self._product_parser, **kw)

    def products(self, record, **kw):
        return self.product(record, multi=True)

    @property
    def _product_parser(self):
        return [
            "id",
            "name",
            "display_name",
            "default_code",
            "barcode",
            ("packaging_ids:packaging", self._product_packaging),
            ("uom_id:uom", self._simple_record_parser() + ["factor", "rounding"]),
            ("seller_ids:supplier_code", self._product_supplier_code),
        ]

    def _product_packaging(self, rec, field):
        return self._jsonify(
            rec.packaging_ids.filtered(lambda x: x.qty),
            self._packaging_parser,
            multi=True,
        )

    def _product_supplier_code(self, rec, field):
        supplier_info = fields.first(
            rec.seller_ids.filtered(lambda x: x.product_id == rec)
        )
        return supplier_info.product_code or ""

    @ensure_model("stock.picking.batch")
    def picking_batch(self, record, with_pickings=False, **kw):
        parser = self._picking_batch_parser
        if with_pickings:
            parser.append(("picking_ids:pickings", self._picking_parser))
        return self._jsonify(record, parser, **kw)

    def picking_batches(self, record, with_pickings=False, **kw):
        return self.picking_batch(record, with_pickings=with_pickings, multi=True)

    @property
    def _picking_batch_parser(self):
        return ["id", "name", "picking_count", "operation_count", "total_weight:weight"]

    @ensure_model("stock.picking.type")
    def picking_type(self, record, **kw):
        parser = self._picking_type_parser
        return self._jsonify(record, parser, **kw)

    def picking_types(self, record, **kw):
        return self.picking_type(record, multi=True)

    @property
    def _picking_type_parser(self):
        return [
            "id",
            "name",
        ]
