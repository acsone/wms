# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import unicodecsv as csv
import xlsxwriter

from odoo import api, fields, models


class AlcDocument(models.Model):

    _inherit = "alc.document"

    compute = fields.Selection(
        selection_add=[("pricelist", "Pricelist"), ("discount", "Discount")]
    )
    type = fields.Selection(
        selection_add=[("pricelist", "Pricelist"), ("discount", "Discount")]
    )

    @api.model
    def _generation_formats(self):
        return ["xlsx", "csv"]

    @api.model
    def _create_discount(self, partner):
        documents = self.browse()
        for file_format in self._generation_formats():
            vals = {
                "name": "FR_PromotionsAlcyon.%s" % file_format,
                "compute": "discount",
                "type": "discount",
                "partner_id": partner.id,
                "format": file_format,
            }
            documents |= self.create(vals)
        return documents

    @api.model
    def _create_pricelist(self, partner):
        documents = self.browse()
        for file_format in self._generation_formats():
            vals = {
                "name": "Liste de prix Alcyon Belux.%s" % file_format,
                "compute": "pricelist",
                "type": "pricelist",
                "partner_id": partner.id,
                "format": file_format,
            }
            documents |= self.create(vals)
        return documents

    def _compute_data_pricelist(self):
        self._compute_daily_file()

    def _compute_data_discount(self):
        self._compute_daily_file()

    def _compute_daily_file(self):
        today = fields.Date.from_string(fields.Date.today())
        for document in self:
            document_date = document.attachment_id.create_date
            if not document_date or fields.Date.from_string(document_date) < today:
                self._generate_attachment_file()

    def _all_by_format(self):
        self.ensure_one()
        domain = [
            ("compute", "=", self.compute),
            ("partner_id", "=", self.partner_id.id),
        ]
        documents = self.search(domain)
        return documents.partition("format")

    def _process_product_lines(self, products, lines):
        if self.compute == "discount":
            self._process_product_lines_discount(products, lines)
        elif self.compute == "pricelist":
            self._process_product_lines_pricelist(products, lines)
        return lines

    def _get_products_domain(self):
        partner_type = self.partner_id.partner_type
        return [("allowed_partner_types", "like", "%%%s%%" % partner_type)]

    def _generate_attachment_file(self):
        self.ensure_one()
        docs_by_format = self._all_by_format()

        domain_products = self._get_products_domain()
        products = self.env["product.product"].search(domain_products)

        lines = []
        self._process_product_lines(products, lines)

        for file_format, document in docs_by_format.items():
            if file_format == "xlsx":
                tmp_file = docs_by_format[file_format]._create_attachment_xlsx(lines)
            else:
                tmp_file = docs_by_format[file_format]._create_attachment_csv(lines)
            vals = {
                "name": document.name,
                "datas": open(tmp_file, "rb").read().encode("base64"),
                "datas_fname": document.name,
                "res_model": "res.partner",
                "res_id": document.partner_id.id,
            }
            document.attachment_id.unlink()
            document.attachment_id = self.env["ir.attachment"].create(vals)

    def _get_lang_price_parser(self):
        mget = lambda s: (lambda r: ",".join(r.mapped(s)))
        return [
            {"name": "Reference", "lang": "fr_BE", "get": "default_code"},
            {"name": "Article", "lang": "fr_BE", "get": "name"},
            {"name": "Code_Mot_Cle", "lang": "fr_BE", "get": lambda r: ""},  # yes...
            {"name": "Mot_Cle", "lang": "fr_BE", "get": mget("categ_ids.name")},
            {"name": "Fabricant", "lang": "fr_BE", "get": mget("manufacturer.name")},
            {"name": "Code_national", "lang": "fr_BE", "get": "cnk_code"},
            {"name": "Prix_Vente_Indicatif", "lang": "fr_BE", "get": "indicated_price"},
            {"name": "TVA"},
            {"name": "Prix_Brut_HTVA_EUR"},
            {"name": "Prix_Brut_TVAC_EUR"},
            {"name": "Prix_Brut_TVAC_BEF", "lang": "fr_BE", "get": lambda r: ""},  # yes
            {"name": "Article_NL", "lang": "nl_BE", "get": "name"},
            {"name": "Article_DE", "lang": "de_DE", "get": "name"},
            {"name": "ean_13", "lang": "fr_BE", "get": "barcode"},
            {"name": "Article_EN", "lang": "en_US", "get": "name"},
            {"name": "Category_NL", "lang": "nl_BE", "get": mget("categ_ids.name")},
            {"name": "Category_EN", "lang": "en_US", "get": mget("categ_ids.name")},
        ]

    def _get_headers(self):
        # method coupled to _process_product_lines_discount
        headers = []
        if self.compute == "discount":
            headers = [
                "Famille",
                "Fabriquant",
                u"Référence interne",
                "Nom du produit",
                "Type de promotion",
                "Date de fin de promotion",
            ]
        if self.compute == "pricelist":
            headers = [p["name"] for p in self._get_lang_price_parser()]
        return headers

    def _get_first_discount(self, discount_records):
        # record_discount should be implementing mixin_past
        started = discount_records.filtered(lambda d: not d.is_past and not d.is_future)
        return started.ordered("date_start")[0] if len(started) > 1 else started

    def _process_product_lines_pricelist(self, products, lines):
        # the langs are only used for the names, so we could possible optimize
        # by putting values in a dict from a read before, and not rely on ORM
        langs = ["fr_BE", "en_US", "nl_BE", "de_DE"]
        products_by_lang = {lang: products.with_context(lang=lang) for lang in langs}
        parser = self._get_lang_price_parser()
        price_key = self.partner_id.property_product_pricelist.role_name
        discount_key = self.partner_id.discount_pricelist_id.discount_role_name
        for product in products:
            # it should be specific_data.vat_tax_group but we should not depend on this
            tax = product.taxes_id.filtered(lambda t: t.tax_group_id.name == "TVA")
            base_price = product._price_cache_get(price_key).get("price", 0)
            if discount_key:
                discount = product._price_cache_get(discount_key).get("discount", 0)
                base_price -= base_price * (1 - discount / 100)
            prices = {
                "TVA": "%s%%" % tax.amount,
                "Prix_Brut_HTVA_EUR": base_price,
                "Prix_Brut_TVAC_EUR": base_price + base_price * tax.amount / 100,
            }
            line = []
            for field_parser in parser:
                get = field_parser.get("get", field_parser["name"])
                if get in prices:
                    value = prices[get]
                else:
                    record = products_by_lang[field_parser["lang"]].browse(product.id)
                    value = (record[get] if isinstance(get, str) else get(record)) or ""
                line.append("%s" % value)
            lines.append(line)
        return lines

    def _process_product_lines_discount(self, products, lines):
        for product in products:
            for product_field in [
                "supplier_discount_ids",
                "supplier_promotion_ids",
                "product_discount_special_ids",
            ]:
                records = product[product_field]
                record = self._get_first_discount(records)
                if record:
                    if record._name == "product.discount.special":
                        discount_type = u"Promotion spéciale"
                    elif record.is_promotion:
                        discount_type = "Produits GRATUITS"
                    else:
                        discount_type = "%s%% off" % record.discount_sale
                    date_end = fields.Date.from_string(record.date_end)
                    line = [
                        product.categ_id.name,
                        product.supplier_id.name,
                        product.default_code,
                        product.name,
                        discount_type,
                        date_end.strftime("%d/%m/%Y") if date_end else "",
                    ]
                    lines.append(line)
        return lines

    def _create_attachment_csv(self, lines):
        headers = self._get_headers()
        filename = "/tmp/%s" % self.name
        with open(filename, "w") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for line in lines:
                writer.writerow(line)
        return filename

    def _create_attachment_xlsx(self, lines):
        filename = "/tmp/%s" % self.name
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        headers = self._get_headers()
        for column, header in enumerate(headers):
            worksheet.write(0, column, header)
        for row, line in enumerate(lines):
            for column, item in enumerate(line):
                worksheet.write(row + 1, column, item)
        workbook.close()
        return filename
