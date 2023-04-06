# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

import xlrd

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tools import float_is_zero


class ProductPriceInfo:
    """Used to map store information read from xlsx file.

    Note: product_id and supplier_id are not odoo ids. These are xml_ids
    """

    __slots__ = [
        "product_id",
        "supplier_id",
        "supplier_name",
        "product_name",
        "internal_reference",
        "supplier_reference",
        "purchase_price",
        "sale_price",
        "sale_price_2",
        "indicated_price",
        "supplier",
        "product",
    ]

    def __init__(self, **kwargs):
        for attr in self.__slots__:
            value = kwargs.get(attr)
            value = value.strip() if value is not None else value
            setattr(self, attr, value)

    # pylint: disable=method-required-super
    def copy(self):
        new = ProductPriceInfo()
        for attr in self.__slots__:
            setattr(new, attr, getattr(self, attr))
        return new


def _ensure_float(price_str):
    return float(price_str)


class ProductPriceImporter(models.TransientModel):

    _name = "alc.product.price.importer"
    _description = "Product prices mass import wizard"

    document = fields.Binary(string="XLSX file", required=True)

    def doit(self):
        self.ensure_one()
        content = base64.decodebytes(self.document)
        product_price_infos = list(self._iter_data(content))
        self._do_update_prices(product_price_infos)
        action = {
            "type": "ir.actions.act_window",
            "name": _("Updated products"),
            "res_model": "product.template",
            "domain": [("id", "in", [i.product.id for i in product_price_infos])],
            "view_mode": "tree,form",
        }
        return action

    @api.model
    def _iter_data(self, content):
        book = xlrd.open_workbook(file_contents=content, on_demand=True)
        try:
            tuple_rows = self.env["base_import.import"]._read_xls_book(
                book, book._sheet_names[0]
            )
            rows = tuple_rows[1]
            headers = rows[0]
            for values in rows[1:]:
                yield ProductPriceInfo(**dict(zip(headers, values, strict=True)))
        finally:
            del book

    @api.model
    def _retrieve_records(self, product_prices_info):
        """Retrieve product and supplier."""
        product_id_by_xmlid = self.__get_xml_ids("product.template")
        supplier_id_by_xmlid = self.__get_xml_ids("res.partner")
        ProductTemplate = self.env["product.template"]
        ResPartner = self.env["res.partner"]
        for price_info in product_prices_info:
            product_xml_id = price_info.product_id
            product_id = product_id_by_xmlid.get(product_xml_id)
            if not product_id:
                raise ValidationError(
                    _(
                        "Unknown product identifier %(product_xml_id)s",
                        product_xml_id=product_xml_id,
                    )
                )
            price_info.product = ProductTemplate.browse(product_id)
            supplier_xml_id = price_info.supplier_id
            supplier_id = supplier_id_by_xmlid.get(supplier_xml_id)
            if not supplier_id:
                raise ValidationError(
                    _(
                        "Unknown supplier identifier %(supplier_xml_id)s",
                        supplier_xml_id=supplier_xml_id,
                    )
                )
            price_info.supplier = ResPartner.browse(supplier_id)

    @api.model
    def __get_xml_ids(self, model_name):
        self.env.cr.execute(
            """
            SELECT
                concat(module, '.', name),
                res_id
            FROM
                ir_model_data
            WHERE
                model = %s
        """,
            (model_name,),
        )
        return dict(self.env.cr.fetchall())

    @api.model
    def _do_update_prices(self, product_price_infos):
        """
        Call the steps required to update all the prices information.

        related to a product.
        Each step is called with all the prices information to allow batch
        processing
        """
        self._retrieve_records(product_price_infos)
        self._update_product_prices(product_price_infos)
        self._update_supplier_default_prices(product_price_infos)
        self._update_supplier_promo_prices(product_price_infos)
        self._update_pricelist_pb2(product_price_infos)

    @api.model
    def _update_product_prices(self, product_price_infos):
        """Update the list_price and indicated price on the product template."""
        for price_info in product_price_infos:
            price_info.product.write(
                {
                    "list_price": _ensure_float(price_info.sale_price),
                    "indicated_price": _ensure_float(price_info.indicated_price),
                }
            )

    @api.model
    def _update_supplier_default_prices(self, product_price_infos):
        """Update the price of the default product.supplierinfo."""
        ProductTemplate = self.env["product.template"]
        ids = [i.product.id for i in product_price_infos]
        default_supplier_infos = ProductTemplate._get_default_supplierinfo(
            ProductTemplate.browse(ids)
        )
        for price_info in product_price_infos:
            product_supplierinfo = default_supplier_infos.get(price_info.product)
            if product_supplierinfo:
                if (
                    default_supplier_infos[price_info.product].partner_id
                    != price_info.supplier
                ):
                    raise ValidationError(
                        _(
                            "The default supplier %(product_supplier_name)s "
                            "for product %(product_name)s is not the same "
                            "one as found into the file (%(price_supplier_name)s)",
                            product_supplier_name=product_supplierinfo.partner_id.name,
                            product_name=price_info.product.name,
                            price_supplier_name=price_info.supplier.name,
                        )
                    )
                product_supplierinfo.write(
                    {"price": _ensure_float(price_info.purchase_price)}
                )
            else:
                price_info.product.write(
                    {
                        "seller_ids": [
                            Command.create(
                                {
                                    "partner_id": price_info.supplier.id,
                                    "price": _ensure_float(price_info.purchase_price),
                                    "product_code": price_info.supplier_reference,
                                },
                            )
                        ]
                    }
                )

    @api.model
    def _update_supplier_promo_prices(self, product_price_infos):
        """Update all the active or future product.supplierinfo defined for promo."""
        ProductSupplierInfo = self.env["product.supplierinfo"]
        today = fields.Date.today()
        for price_info in product_price_infos:
            ProductSupplierInfo.search(
                [
                    ("product_tmpl_id", "=", price_info.product.id),
                    ("partner_id", "=", price_info.supplier.id),
                    ("date_end", ">=", today),
                ]
            ).write({"price": _ensure_float(price_info.purchase_price)})

    @api.model
    def _update_pricelist_pb2(self, product_price_infos):
        """
        Keep pricelist_pb2 in sync with the provided sale_price_2.

        For each product_price_info:
            If sale_price_2 is not set or 0:
                -> remove item from the pricelist if exists
            Is sale_price_2 is set:
                -> Update item into the pricelist if exists or create a new one.

        Rem: At this stage we don't support price versioning (price fields
          on the product template are not versioned by default) Therefore changes
          are applied immediately. That's why we update the existing pricelist item
          if one exists instead of closing the existing one and creating a new
          starting from now.
        """
        ProductPricelistItem = self.env["product.pricelist.item"]
        pricelist = self.env.ref("alc_product_pricelist_data.product_pricelist_pb2")

        pricelist_items = self.env["product.pricelist.item"].search(
            [
                ("pricelist_id", "=", pricelist.id),
                ("applied_on", "=", "1_product"),
                ("product_tmpl_id", "in", [i.product.id for i in product_price_infos]),
            ]
        )
        pricelist_items_by_product = {i.product_tmpl_id: i for i in pricelist_items}
        prec = self.env["decimal.precision"].precision_get("Product Price")
        for price_info in product_price_infos:
            sale_price_2 = price_info.sale_price_2
            if sale_price_2:
                sale_price_2 = _ensure_float(price_info.sale_price_2)
            sale_price_2_is_set = sale_price_2 and not float_is_zero(
                sale_price_2, precision_digits=prec
            )
            pricelist_item = pricelist_items_by_product.get(price_info.product)
            if sale_price_2_is_set:
                if pricelist_item:
                    pricelist_item.write(
                        {"compute_price": "fixed", "fixed_price": sale_price_2}
                    )
                else:
                    ProductPricelistItem.create(
                        {
                            "applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": sale_price_2,
                            "product_tmpl_id": price_info.product.id,
                            "pricelist_id": pricelist.id,
                        }
                    )
            elif pricelist_item:
                pricelist_item.unlink()
