#!/usr/bin/env python2
# -*- coding: utf-8 -*-

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


def load_option_ids(root, ref):
    csv_file = open(os.path.join(root, "alc_options.csv"))
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)  # skip headers
    for r in csv_reader:
        record = ENV["attribute.option"].search([("name", "=", r[1])])
        record.ensure_one()
        ref[r[0]] = record


def load_size_ids():
    for name, _id in [("small", "petit"), ("medium", "moyen"), ("big", "grand")]:
        SIZE_IDS[_id] = ENV.ref("alc_pim.option_attribute_animal_size_%s" % name)


def load_age_ids():
    AGE_IDS["puppy"] = ENV.ref("alc_pim.attribute_option_junior")
    for name in ["senior", "adult", "junior"]:
        AGE_IDS[name] = ENV.ref("alc_pim.attribute_option_%s" % name)


def find_record_by_id(column_name, value):
    if column_name == "categories" or "marque" in column_name:
        record = ENV.ref("alc_pim." + value)
    elif column_name in {"taille_animal"}:
        record = SIZE_IDS[value]
    elif column_name in {"categ_age"}:
        record = AGE_IDS[value]
    else:
        record = OPTIONS_IDS[value]
    return record


def bool_parser(column_name, value):
    return value and bool(int(value))


def m2m_parser(column_name, value_s):
    values = value_s.split(",") if value_s else []
    records = [find_record_by_id(column_name, v) for v in values]
    return [(6, 0, [r.id for r in records])] if records else [(5,)]


def m2o_parser(column_name, value):
    return find_record_by_id(column_name, value).id if value else False


def char_parser(column_name, value):
    return value or False


PRODUCT_FILE_MAPPING = {
    "taille_animal": ("animal_size_option_ids", m2m_parser),
    "categ_age": ("categ_age_option_ids", m2m_parser),
    "indications": ("indication_option_ids", m2m_parser),
    "presentation": ("presentation_option_id", m2o_parser),
}


def process_product_row(root, rd):
    pfm = PRODUCT_FILE_MAPPING
    vals = {pfm[f][0]: pfm[f][1](f, rd[f]) for f in pfm}
    to_update = False
    for v in vals.values():
        if v and v != [(5,)]:
            to_update = True
            break
    model = ENV["product.template"].with_context(active_test=False)
    product_id = PRODUCT_ID_BY_SKU.get(rd["sku"])
    if not product_id:
        click.echo("Product with sku %s not found" % rd["sku"])
        return None
    if product_id and to_update:
        product = model.browse(product_id)
        desc = "PIM Import Product %s" % product.name
        click.echo(desc)
        product.write(vals)
        return product
    return None


def load_product_id_by_sku():
    global PRODUCT_ID_BY_SKU  # pylint: disable=global-statement
    ENV.cr.execute(
        """
        select
            default_code,
            id
        from
            product_template
    """
    )
    PRODUCT_ID_BY_SKU = dict(ENV.cr.fetchall())


OPTIONS_IDS = {}  # to load based on path provided at execution
PRODUCT_ID_BY_SKU = {}
SIZE_IDS = {}
AGE_IDS = {}


@click.command()
@click.option("--root", required=True, help="Directory where the files are.")
@click.option("--filename", required=True, help="Main CSV.")
@click_odoo.env_options(default_log_level="info")
def main(env, root, filename, delimiter=";"):
    global ENV  # pylint: disable=global-statement
    ENV = env
    # ensure hierarchy is right
    load_option_ids(root, OPTIONS_IDS)
    load_size_ids()
    load_age_ids()
    load_product_id_by_sku()
    return process_csv_file(root, filename, process_product_row, delimiter)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
    #  USAGE: click-odoo -c .odoorc -- scripts/load_pim_product_data.py -d odoo-alcyon --root=tmp --filename=ff
    # 1_products_export_en_GB/1_products_export_en_GB_ecom_B2B_2021-09-02_14:46:09.csv
