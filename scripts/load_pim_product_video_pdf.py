#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import base64
import hashlib
import logging
import os

import click
import click_odoo
import unicodecsv as csv

_logger = logging.getLogger("PIM IMPORT")

ENV = None


def process_csv_file(root, filename, process_row_dict, delimiter=","):
    img_root = os.path.join(root, os.path.dirname(filename))
    csv_file = open(os.path.join(root, filename))
    csv_reader = csv.reader(csv_file, delimiter=delimiter)
    headers = next(csv_reader)
    missing_records = []
    for row in csv_reader:
        row_dict = dict(zip(headers, row))
        try:
            record = process_row_dict(img_root, row_dict)
        except Exception:
            record = None
            _logger.exception("Unable to import row %s", row_dict)
        if not record:
            missing_records.append(row)
    if missing_records:
        _logger.warning(missing_records)
    return missing_records


def char_parser(column_name, value):
    return value or False


PRODUCT_FILE_MAPPING = {
    "link_video-en_GB": ("link_video", char_parser),
}

PDF_FIELDS = ["pdf_file-fr_BE", "pdf_file-nl_BE", "pdf_file-en_GB"]

IMPORTED_FILE = {}


def process_product_row(root, rd):
    link_video = (
        rd["link_video-en_GB"] or rd["link_video-fr_BE"] or rd["link_video-nl_BE"]
    )
    if not any(rd[f] for f in PDF_FIELDS) and not link_video:
        return None

    product_domain = [("default_code", "=", rd["sku"])]
    model = ENV["product.template"].with_context(active_test=False, lang="en_US")
    product = model.search(product_domain)
    if product:
        updated = False
        if link_video:
            product.link_video = link_video
        for lang in ("fr_BE", "nl_BE"):
            link_video = rd["link_video-" + lang]
            if not link_video:
                continue
            product.with_context(lang=lang).write({"link_video": link_video})
            updated = True
        for sequence, pdf_field in enumerate(PDF_FIELDS):
            if not rd[pdf_field]:
                continue
            lang = pdf_field.split("-")[1]
            if lang == "en_GB":
                lang = "en_US"
            img_path = os.path.join(root, rd[pdf_field])

            file_content = open(img_path).read()
            md5_hash = hashlib.md5(file_content).hexdigest()
            media_id = IMPORTED_FILE.get(md5_hash)
            if not media_id:
                vals_media = {
                    "name": os.path.basename(img_path),
                    "file_type": "media",
                    "data": base64.b64encode(file_content),
                    "lang": lang,
                }
                media = ENV["storage.media"].create(vals_media)
                media_id = media.id
                IMPORTED_FILE[md5_hash] = media_id
            vals_rel = {
                "sequence": sequence,
                "media_id": media_id,
                "product_tmpl_id": product.id,
            }
            ENV["product.media.relation"].create(vals_rel)
            updated = True

        if updated:
            desc = "PIM Product %s updated" % product.display_name
            click.echo(desc)
    return product


@click.command()
@click.option("--root", required=True, help="Directory where the files are.")
@click.option("--filename", required=True, help="Main CSV.")
@click_odoo.env_options(default_log_level="info")
def main(env, root, filename, delimiter=";"):
    global ENV  # pylint: disable=global-statement
    ENV = env
    return process_csv_file(root, filename, process_product_row, delimiter)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
    #  USAGE: click-odoo -c .odoorc -- scripts/load_pim_product_data.py -d odoo-alcyon --root=tmp --filename=ff
    # 1_products_export_en_GB/1_products_export_en_GB_ecom_B2B_2021-09-02_14:46:09.csv
