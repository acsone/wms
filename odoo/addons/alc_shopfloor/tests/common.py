# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import difflib
import pprint
from collections import namedtuple

from odoo import models
from odoo.tools import float_compare

from odoo.addons.shopfloor_base.tests.common import CommonCase as BaseCommonCase


# pylint: disable=missing-return
class CommonCase(BaseCommonCase):
    @classmethod
    def setUpClassVars(cls):
        super(CommonCase, cls).setUpClassVars()
        stock_location = cls.env.ref("stock.stock_location_stock")
        cls.stock_location = stock_location
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.dispatch_location = cls.env.ref("stock.location_dispatch_zone")
        cls.packing_location = cls.env.ref("stock.location_pack_zone")
        cls.input_location = cls.env.ref("stock.stock_location_company")
        cls.shelf1 = cls.env.ref("stock.stock_location_components")
        cls.shelf2 = cls.env.ref("stock.stock_location_14")
        cls.env.cr.execute(
            "update stock_location set barcode=floor(random() * 100000) where barcode is null"
        )

    @classmethod
    def _shopfloor_user_values(cls):
        vals = super(CommonCase, cls)._shopfloor_user_values()
        vals["groups_id"] = [(6, 0, [cls.env.ref("stock.group_stock_user").id])]
        return vals

    @classmethod
    def setUpClassBaseData(cls):
        super(CommonCase, cls).setUpClassBaseData()
        cls.customer = cls.env["res.partner"].sudo().create({"name": "Customer"})

        cls.customer_location.sudo().barcode = "CUSTOMERS"
        cls.dispatch_location.sudo().barcode = "DISPATCH"
        cls.packing_location.sudo().barcode = "PACKING"
        cls.input_location.sudo().barcode = "INPUT"
        cls.shelf1.sudo().barcode = "SHELF1"
        cls.shelf2.sudo().barcode = "SHELF2"

        cls.product_a = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Product A",
                    "type": "product",
                    "default_code": "A",
                    "barcode": "A",
                    "weight": 2,
                }
            )
        )
        cls.product_a_packaging = (
            cls.env["product.packaging"]
            .sudo()
            .create(
                {
                    "name": "Box",
                    "product_tmpl_id": cls.product_a.product_tmpl_id.id,
                    "barcode": "ProductABox",
                }
            )
        )
        cls.product_b = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Product B",
                    "type": "product",
                    "default_code": "B",
                    "barcode": "B",
                    "weight": 3,
                }
            )
        )
        cls.product_b_packaging = (
            cls.env["product.packaging"]
            .sudo()
            .create(
                {
                    "name": "Box",
                    "product_tmpl_id": cls.product_b.product_tmpl_id.id,
                    "barcode": "ProductBBox",
                }
            )
        )
        cls.product_c = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Product C",
                    "type": "product",
                    "default_code": "C",
                    "barcode": "C",
                    "weight": 3,
                }
            )
        )
        cls.product_c_packaging = (
            cls.env["product.packaging"]
            .sudo()
            .create(
                {
                    "name": "Box",
                    "product_tmpl_id": cls.product_c.product_tmpl_id.id,
                    "barcode": "ProductCBox",
                }
            )
        )
        cls.product_d = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Product D",
                    "type": "product",
                    "default_code": "D",
                    "barcode": "D",
                    "weight": 3,
                }
            )
        )
        cls.product_d_packaging = (
            cls.env["product.packaging"]
            .sudo()
            .create(
                {
                    "name": "Box",
                    "product_tmpl_id": cls.product_d.product_tmpl_id.id,
                    "barcode": "ProductDBox",
                }
            )
        )

    @classmethod
    def _create_picking(cls, picking_type=None, lines=None, confirm=True):
        Picking = cls.env["stock.picking"]
        picking_type = picking_type or cls.picking_type
        move_lines = []
        picking_values = {
            "partner_id": cls.customer.id,
            "picking_type_id": picking_type.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
            "move_lines": move_lines,
        }
        if lines is None:
            lines = [(cls.product_a, 10), (cls.product_b, 10)]
        for product, qty in lines:
            move_lines.append(
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "picking_type_id": picking_type.id,
                        "product_uom_qty": qty,
                        "product_uom": product.uom_id.id,
                        "location_id": picking_type.default_location_src_id.id,
                        "location_dest_id": picking_type.default_location_dest_id.id,
                    },
                )
            )
        picking = Picking.create(picking_values)
        if confirm:
            picking.action_confirm()
        return picking

    @classmethod
    def _update_qty_in_location(
        cls, location, product, quantity, package=None, lot=None
    ):
        quants = (
            cls.env["stock.quant"]
            .sudo()
            ._gather(product, location, lot_id=lot, package_id=package, strict=True)
        )
        qty_available = sum(quants.mapped("qty"))
        # this method adds the quantity to the current quantity, so remove it
        qty_to_add = quantity - qty_available
        if qty_to_add >= 0:
            cls.env["stock.quant"]._update_available_quantity(
                product, location, qty_to_add, package_id=package, lot_id=lot
            )
        else:
            qty_to_remove = -qty_to_add
            for quant in quants:
                if qty_to_remove >= quant.qty:
                    new_quantity = 0
                    qty_to_remove -= quant.qty
                else:
                    new_quantity = quant.qty - qty_to_remove
                    qty_to_remove -= qty_to_remove
                quant.write({"qty": new_quantity})
                if qty_to_remove <= 0:
                    break

    @classmethod
    def _fill_stock_for_moves(
        cls, moves, in_package=False, same_package=True, in_lot=False, location=False
    ):
        """Satisfy stock for given moves.

        :param moves: stock.move recordset
        :param in_package: stock.quant.package record or simple boolean
            If a package record is given, it will be used as package.
            If a boolean true is given, a new package will be created for each move.
        :param same_package:
            modify the behavior of `in_package` to use the same package for all moves.
        :param in_lot: stock.production.lot record or simple boolean
            If a lot record is given, it will be used as lot.
            If a boolean true is given, a new lot will be created.
        """
        product_packages = {}
        product_locations = {}
        package = None
        if in_package:
            if isinstance(in_package, models.BaseModel):
                package = in_package
            else:
                package = cls.env["stock.quant.package"].create({})
        for move in moves:
            key = (move.product_id, location or move.location_id)
            product_locations.setdefault(key, 0)
            product_locations[key] += move.product_qty
            if in_package:
                if isinstance(in_package, models.BaseModel):
                    package = in_package
                if not package or package and not same_package:
                    package = cls.env["stock.quant.package"].create({})
                product_packages[key] = package
        for (product, loc), qty in product_locations.items():
            lot = None
            if in_lot:
                if isinstance(in_lot, models.BaseModel):
                    lot = in_lot
                else:
                    lot = cls.env["stock.production.lot"].create(
                        {"product_id": product.id}
                    )
            if not (in_lot or in_package):
                # always add more quantity in stock to avoid to trigger the
                # "zero checks" in tests, not for lots which must have a qty
                # of 1 and not for packages because we need the strict number
                # of units to pick a package
                qty *= 2
            cls._update_qty_in_location(loc, product, qty, package=package, lot=lot)

    # used by _create_package_in_location
    PackageContent = namedtuple(
        "PackageContent",
        # recordset of the product,
        # quantity in float
        # recordset of the lot (optional)
        "product quantity lot",
    )

    def _create_package_in_location(self, location, content):
        """Create a package and quants in a location

        content is a list of PackageContent
        """
        package = self.env["stock.quant.package"].create({})
        for product, quantity, lot in content:
            self._update_qty_in_location(
                location, product, quantity, package=package, lot=lot
            )
        return package

    def _create_lot(self, product):
        return self.env["stock.production.lot"].create({"product_id": product.id})

    def assertRecordValues(self, records, expected_values):  # noqa: C901
        """ Compare a recordset with a list of dictionaries representing the expected results.
        This method performs a comparison element by element based on their index.
        Then, the order of the expected values is extremely important.

        Note that:
          - Comparison between falsy values is supported: False match with None.
          - Comparison between monetary field is also treated according the currency's rounding.
          - Comparison between x2many field is done by ids. Then, empty expected ids must be [].
          - Comparison between many2one field id done by id. Empty comparison can be done using any falsy value.

        :param records:               The records to compare.
        :param expected_values:       List of dicts expected to be exactly matched in records
        """

        def _compare_candidate(record, candidate, field_names):
            """ Compare all the values in `candidate` with a record.
            :param record:      record being compared
            :param candidate:   dict of values to compare
            :return:            A dictionary will encountered difference in values.
            """
            diff = {}
            for field_name in field_names:
                record_value = record[field_name]
                field = record._fields[field_name]
                field_type = field.type
                if field_type == "monetary":
                    # Compare monetary field.
                    currency_field_name = record._fields[field_name].currency_field
                    record_currency = record[currency_field_name]
                    if field_name not in candidate:
                        diff[field_name] = (record_value, None)
                    elif record_currency:
                        if record_currency.compare_amounts(
                            candidate[field_name], record_value
                        ):
                            diff[field_name] = (
                                record_value,
                                record_currency.round(candidate[field_name]),
                            )
                    elif candidate[field_name] != record_value:
                        diff[field_name] = (record_value, candidate[field_name])
                elif field_type == "float" and field.digits:
                    prec = field.digits[1]
                    if (
                        float_compare(
                            candidate[field_name], record_value, precision_digits=prec
                        )
                        != 0
                    ):
                        diff[field_name] = (record_value, candidate[field_name])
                elif field_type in ("one2many", "many2many"):
                    # Compare x2many relational fields.
                    # Empty comparison must be an empty list to be True.
                    if field_name not in candidate:
                        diff[field_name] = (sorted(record_value.ids), None)
                    elif set(record_value.ids) != set(candidate[field_name]):
                        diff[field_name] = (
                            sorted(record_value.ids),
                            sorted(candidate[field_name]),
                        )
                elif field_type == "many2one":
                    # Compare many2one relational fields.
                    # Every falsy value is allowed to compare with an empty record.
                    if field_name not in candidate:
                        diff[field_name] = (record_value.id, None)
                    elif (
                        record_value or candidate[field_name]
                    ) and record_value.id != candidate[field_name]:
                        diff[field_name] = (record_value.id, candidate[field_name])
                else:
                    # Compare others fields if not both interpreted as falsy values.
                    if field_name not in candidate:
                        diff[field_name] = (record_value, None)
                    elif (
                        candidate[field_name] or record_value
                    ) and record_value != candidate[field_name]:
                        diff[field_name] = (record_value, candidate[field_name])
            return diff

        # Compare records with candidates.
        different_values = []
        field_names = list(expected_values[0].keys())
        for index, record in enumerate(records):
            is_additional_record = index >= len(expected_values)
            candidate = {} if is_additional_record else expected_values[index]
            diff = _compare_candidate(record, candidate, field_names)
            if diff:
                different_values.append(
                    (
                        index,
                        "additional_record" if is_additional_record else "regular_diff",
                        diff,
                    )
                )
        for index in range(len(records), len(expected_values)):
            diff = {}
            for field_name in field_names:
                diff[field_name] = (None, expected_values[index][field_name])
            different_values.append((index, "missing_record", diff))

        # Build error message.
        if not different_values:
            return

        errors = ["The records and expected_values do not match."]
        if len(records) != len(expected_values):
            errors.append(
                "Wrong number of records to compare: %d records versus %d expected values."
                % (len(records), len(expected_values))
            )

        for index, diff_type, diff in different_values:
            if diff_type == "regular_diff":
                errors.append("\n==== Differences at index %s ====" % index)
                record_diff = ["{}:{}".format(k, v[0]) for k, v in diff.items()]
                candidate_diff = ["{}:{}".format(k, v[1]) for k, v in diff.items()]
                errors.append(
                    "\n".join(difflib.unified_diff(record_diff, candidate_diff))
                )
            elif diff_type == "additional_record":
                errors += [
                    "\n==== Additional record ====",
                    pprint.pformat({k: v[0] for k, v in diff.items()}),
                ]
            elif diff_type == "missing_record":
                errors += [
                    "\n==== Missing record ====",
                    pprint.pformat({k: v[1] for k, v in diff.items()}),
                ]

        self.fail("\n".join(errors))


class PickingBatchMixin:

    BatchProduct = namedtuple(
        "BatchProduct",
        # browse record of the product,
        # quantity in float
        "product quantity",
    )

    @classmethod
    def _create_picking_batch(cls, products):
        """Create a picking batch

        :param products: list of list of BatchProduct. The outer list creates
        pickings and the innerr list creates moves in these pickings
        """
        picking_ids = []
        for transfer in products:
            picking_ids.append(
                cls._create_picking(
                    lines=[(b.product, b.quantity) for b in transfer]
                ).id
            )
        batch = cls.env["stock.picking.batch"].create(
            {"picking_ids": [(6, picking_ids)]}
        )
        batch.picking_ids.action_confirm()
        batch.picking_ids.action_assign()
        return batch

    @classmethod
    def _simulate_batch_selected(
        cls, batches, in_package=False, in_lot=False, fill_stock=True
    ):
        """Create a state as if a batch was selected by the user

        * The picking batch is in progress
        * It is assigned to the current user
        * All the move lines are available

        Note: currently, this method create a source package that contains
        all the products of the batch. It is enough for the current tests.
        """
        pickings = batches.mapped("picking_ids")
        if fill_stock:
            cls._fill_stock_for_moves(
                pickings.mapped("move_lines"), in_package=in_package, in_lot=in_lot
            )
        pickings.action_assign()
        batches.write({"state": "in_progress", "operator_id": cls.env.uid})
