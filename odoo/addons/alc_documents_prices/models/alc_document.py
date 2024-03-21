# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

import unicodecsv as csv
import xlsxwriter

from odoo import api, fields

from odoo.addons.alc_documents.models import alc_document


class AlcDocument(alc_document.AlcDocument):

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
                "name": f"FR_PromotionsAlcyon.{file_format}",
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
                "name": f"Liste de prix Alcyon Belux.{file_format}",
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
        today = fields.Date.today()
        for document in self:
            document_date = document.attachment_id.create_date
            if not document_date or document_date.date() < today:
                document._generate_attachment_file()

    def _all_by_format(self):
        self.ensure_one()
        domain = [
            ("compute", "=", self.compute),
            ("partner_id", "=", self.partner_id.id),
        ]
        documents = self.search(domain)
        return documents.partition("format")

    def _process_prices_data_lines(self, prices_data_lines, lines):
        if self.compute == "discount":
            self._process_prices_data_lines_discount(prices_data_lines, lines)
        elif self.compute == "pricelist":
            self._process_prices_data_lines_pricelist(prices_data_lines, lines)
        return lines

    def _generate_attachment_file(self):
        self.ensure_one()
        self._all_by_format()

        prices_data_lines_iterator = self.env[
            "alc.product.flattened.data"
        ]._get_partner_products_iterator(self.partner_id)
        # if no attachment, we create an empty one to be able to stream the
        # new content to it
        if not self.attachment_id:
            vals = {
                "name": self.name,
                "raw": "empty",
                "res_model": "res.partner",
                "res_id": self.partner_id.id,
            }
            self.attachment_id = self.env["ir.attachment"].create(vals)

        with self.attachment_id.open("wb") as output_file:
            price_data_lines_processor = self._process_prices_data_lines_discount
            if self.compute == "pricelist":
                price_data_lines_processor = self._process_prices_data_lines_pricelist
            if self.format == "xlsx":
                self._create_attachment_xlsx(
                    price_data_lines_processor(prices_data_lines_iterator), output_file
                )
            else:
                self._create_attachment_csv(
                    price_data_lines_processor(prices_data_lines_iterator), output_file
                )

    def _get_lang_price_parser(self):
        parser = [
            {"name": "Reference", "get": "default_code"},
            {"name": "Article", "get": "name_fr"},
            {"name": "Code_Mot_Cle", "get": lambda r: ""},  # yes...
            {"name": "Mot_Cle", "get": "categ_fr"},
            {"name": "Fabricant", "get": "manufacturer"},
            {"name": "Code_national", "get": "cnk_code"},
            {"name": "Prix_Vente_Indicatif", "get": lambda r: r.indicated_price or 0},
            {"name": "TVA"},
            {"name": "Prix_Brut_HTVA_EUR"},
            {"name": "Prix_Brut_TVAC_EUR"},
            {"name": "Prix_Brut_TVAC_BEF", "get": lambda r: ""},  # yes
            {"name": "Article_NL", "get": "name_nl"},
            {"name": "Article_DE", "get": "name_de"},
            {"name": "ean_13", "get": "barcode"},
            {"name": "Article_EN", "get": "name_en"},
            {"name": "Category_NL", "get": "categ_nl"},
            {"name": "Category_EN", "get": "categ_en"},
        ]
        if self.env["ir.config_parameter"].sudo().get_param(
            "alc_documents_prices.include_code_amm", ""
        ).lower() in ["true", "1", "t", "y", "yes"]:
            parser.append({"name": "AMM_Number", "get": "code_amm"})
        return parser

    def _get_headers(self):
        # method coupled to _process_prices_data_lines_discount
        headers = []
        if self.compute == "discount":
            headers = [
                "Famille",
                "Fabriquant",
                "Référence interne",
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

    def _process_prices_data_lines_pricelist(self, prices_data_lines_iterator):
        """
        :param prices_data_lines_iterator: iterator of alc.product.flattened.data.

        :return: a generator of lines
        """
        # the langs are only used for the names, so we could possible optimize
        # by putting values in a dict from a read before, and not rely on ORM
        parser = self._get_lang_price_parser()
        for prices_data in prices_data_lines_iterator:
            prices = {
                "TVA": f"{prices_data.vat}%",
                "Prix_Brut_HTVA_EUR": prices_data.gross_price,
                "Prix_Brut_TVAC_EUR": prices_data.gross_price_with_vat,
            }
            line = []
            for field_parser in parser:
                get = field_parser.get("get", field_parser["name"])
                value = prices.get(get, "NOVALUE")
                if value == "NOVALUE":
                    value = (
                        getattr(prices_data, get)
                        if isinstance(get, str)
                        else get(prices_data)
                    ) or ""
                line.append(f"{value}")
            yield line

    def _process_prices_data_lines_discount(self, prices_data_lines_iterator):
        """
        :param prices_data_lines_iterator: iterator of alc.product.flattened.data.

        :return: a generator of lines
        """
        for prices_data in prices_data_lines_iterator:

            for discount_def in [
                "supplier_discount",
                "supplier_promotion",
                "discount_special",
            ]:
                discount_type = ""
                date_end = None
                if (
                    discount_def == "supplier_discount"
                    and prices_data.supplier_discount_discount_sale
                    and (
                        not prices_data.supplier_discount_only_for_veterinaries
                        or self.partner_id.partner_type == "veterinary"
                    )
                ):
                    dtype = prices_data.supplier_discount_discount_sale or 0
                    discount_type = f"{dtype}% off"
                    date_end = prices_data.supplier_discount_date_end
                elif (
                    discount_def == "supplier_promotion"
                    and prices_data.has_supplier_promotion
                    and (
                        not prices_data.supplier_promotion_only_for_veterinaries
                        or self.partner_id.partner_type == "veterinary"
                    )
                ):
                    discount_type = "Produits GRATUITS"
                    date_end = prices_data.supplier_promotion_date_end
                elif (
                    discount_def == "discount_special"
                    and prices_data.has_discount_special
                ):
                    discount_type = "Promotion spéciale"
                    date_end = prices_data.discount_special_date_end
                if discount_type:
                    date_end = fields.Date.from_string(date_end)
                    line = [
                        prices_data.categ_fr,
                        prices_data.supplier_name,
                        prices_data.default_code,
                        prices_data.name_fr,
                        discount_type,
                        date_end.strftime("%d/%m/%Y") if date_end else "",
                    ]
                    yield line

    def _create_attachment_csv(self, lines_generator, output_file):
        headers = self._get_headers()
        writer = csv.writer(output_file, delimiter=";")
        writer.writerow(headers)
        for line in lines_generator:
            writer.writerow(line)

    def _create_attachment_xlsx(self, lines_generator, output_file):
        filename = f"/tmp/{self.name}"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        headers = self._get_headers()
        for column, header in enumerate(headers):
            worksheet.write(0, column, header)
        for row, line in enumerate(lines_generator):
            for column, item in enumerate(line):
                worksheet.write(row + 1, column, item)
        workbook.close()
        with open(filename, "rb") as f:
            output_file.write(f.read())
        # remove the temporary file
        os.remove(filename)

    def _get_document_date(self):
        res = super()._get_document_date()
        if self.compute in ["pricelist", "discount"]:
            res = False
        return res
