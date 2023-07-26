# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import OrderedDict, namedtuple

from odoo import _

from odoo.addons.report_xlsx_helper.report.report_xlsx_abstract import (
    ReportXlsxAbstract,
)
from odoo.addons.report_xlsx_helper.report.report_xlsx_format import FORMATS

ProductInfo = namedtuple(
    "ProductInfo",
    [
        "xml_id",
        "supplier_xml_id",
        "name",
        "default_code",
        "list_price",
        "sale_price_2",
        "indicated_price",
    ],
)


class ReportProductPriceImport(ReportXlsxAbstract):
    _name = "report.report_product_price_import_xlsx"
    _description = "Report model for report_xlsx"

    def _get_ws_params(self, wb, data, products):
        template = OrderedDict()
        template["product_id"] = {
            "header": {"value": "product_id"},
            "data": {"type": "string", "value": self._render("product_info.xml_id")},
            "width": 30,
        }
        template["supplier_id"] = {
            "header": {"value": "supplier_id"},
            "data": {
                "type": "string",
                "value": self._render("product_info.supplier_xml_id or '' "),
            },
            "width": 30,
        }
        template["supplier_name"] = {
            "header": {"value": "supplier_name"},
            "data": {
                "type": "string",
                "value": self._render("supplier.partner_id.name or ''"),
            },
            "width": 30,
        }
        template["product_name"] = {
            "header": {"value": "product_name"},
            "data": {"type": "string", "value": self._render("product_info.name")},
            "width": 50,
        }
        template["internal_reference"] = {
            "header": {"value": "internal_reference"},
            "data": {
                "type": "string",
                "value": self._render("product_info.default_code or ''"),
            },
            "width": 10,
        }
        template["supplier_reference"] = {
            "header": {"value": "supplier_reference"},
            "data": {
                "type": "string",
                "value": self._render("supplier.product_code or ''"),
            },
            "width": 10,
        }
        template["sale_taxes"] = {
            "header": {"value": "sale_taxes"},
            "data": {
                "type": "string",
                "value": self._render("', '.join(product.mapped('taxes_id.name'))"),
            },
            "width": 10,
        }
        template["purchase_price"] = {
            "header": {"value": "purchase_price"},
            "data": {"type": "number", "value": self._render("supplier.price")},
            "width": 7,
        }
        template["sale_price"] = {
            "header": {"value": "sale_price"},
            "data": {
                "type": "number",
                "value": self._render("product_info.list_price"),
            },
            "width": 7,
        }
        template["sale_price_2"] = {
            "header": {"value": "sale_price_2"},
            "data": {
                "type": "number",
                "value": self._render("product_info.sale_price_2"),
            },
            "width": 7,
        }
        template["indicated_price"] = {
            "header": {"value": "indicated_price"},
            "data": {
                "type": "number",
                "value": self._render("product_info.indicated_price"),
            },
            "width": 7,
        }
        ws_params = {
            "ws_name": _("Product prices"),
            "generate_ws_method": "_product_prices_report",
            "title": _("Product prices"),
            "wanted_list": list(template),
            "col_specs": template,
        }

        return [ws_params]

    def _product_prices_report(self, workbook, ws, ws_params, data, products):
        self._set_column_width(ws, ws_params)
        if "active_domain" in self.env.context:
            products = products.search(self.env.context["active_domain"])
        row_pos = 0
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=FORMATS["format_theader_yellow_left"],
        )
        ws.freeze_panes(row_pos, 0)

        default_supplier_infos = products._get_default_supplierinfo(products)
        supplier_info_none = self.env["product.supplierinfo"]

        for product in products:
            supplier_info = default_supplier_infos.get(product, supplier_info_none)
            product_info = self._get_product_data(product)
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="data",
                render_space={
                    "supplier": supplier_info,
                    "product_info": product_info,
                    "product": product,
                },
                default_format=FORMATS["format_tcell_left"],
            )

    def _get_product_data(self, product):
        data = product.export_data(
            [
                "id",
                "seller_ids/partner_id/id",
                "name",
                "default_code",
                "list_price",
                "sale_price_2",
                "indicated_price",
            ],
        )["datas"][0]
        return ProductInfo(*data)
