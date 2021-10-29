#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
import os

import click
import click_odoo
import unicodecsv as csv

_logger = logging.getLogger("PIM IMPORT")

ENV = env  # pylint: disable=undefined-variable  # noqa


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


def load_species_ids(ref):
    mapping = {
        "non_specifie": "not_specified",
        "souris": "mouse",
        "tous": "all",
        "abeille": "bee",
        "bovin": "cattle",
        "caprin": "goat",
        "chat": "cat",
        "chien": "dog",
        "cobaye": "guinea_pig",
        "cheval": "horse",
        "chinchilla": "chinchilla",
        "furet": "ferret",
        "lapin": "rabbit",
        "oiseau": "bird",
        "ovin": "sheep",
        "pigeon": "pigeon",
        "porc": "pig",
        "rat": "rat",
        "reptile": "reptile",
        "volaille": "poultry",
        "autre": "other",
    }
    for k in mapping:
        ref[k] = ENV.ref("product_animal_species.%s" % mapping[k])


def load_attribute_set_category_mapping(ref):
    attribute_set_category_mapping_xmlids = {
        "alc_pim.attribute_set_medicaments": "alc_pim.med",
        "alc_pim.attribute_set_aliments": "alc_pim.ali",
        "alc_pim.attribute_set_materiel": "alc_pim.mat",
    }
    for attribute in attribute_set_category_mapping_xmlids:
        att_id = ENV.ref(attribute).id
        parent_cat_id = ENV.ref(attribute_set_category_mapping_xmlids[attribute]).id
        domain_cats = [("parent_id", "child_of", parent_cat_id)]
        cats = ENV["product.category"].search(domain_cats)
        ref[att_id] = cats.ids


def find_record_by_id(column_name, value):
    if column_name in {"marque_medicaments", "categories"}:
        record = ENV.ref("alc_pim." + value)
    elif column_name in {"espece", "espece_principale"}:
        record = SPECIES_IDS[value]
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


def amcra_parser(column_name, value):
    amcra_map = {"1": "yellow", "2": "orange", "3": "red"}
    return value and amcra_map["value"]


def thread_parser(column_name, value):
    thread_map = {
        "1": ENV.ref("alc_pim.attribute_option_monofilament").id,
        "2": ENV.ref("alc_pim.attribute_option_polyfilament").id,
    }
    return value and thread_map["value"]


def char_parser(column_name, value):
    return value or False


PRODUCT_FILE_MAPPING = {
    "categories": ("categ_ids", m2m_parser),
    "code_cnk": ("cnk_code", char_parser),
    "num_amm": ("code_amm", char_parser),
    "code_cti_ext": ("code_cti", char_parser),
    "pharma_only": ("pharmacy_only", bool_parser),
    "class_amcra": ("class_amcra", amcra_parser),
    "marque_medicaments": ("product_brand_id", m2o_parser),
    "tisse": ("fabric", bool_parser),
    "descr_courte-en_GB": ("description_shop_short", char_parser),
    "descr_long-en_GB": ("description_shop_long", char_parser),
    "link_notice-en_GB": ("link_notice", char_parser),
    "link_info_compl-en_GB": ("link_info", char_parser),
    "principe_actif": ("active_principle_option_ids", m2m_parser),
    "voie_dadmin": ("administration_route_option_ids", m2m_parser),
    "sterile": ("sterile", bool_parser),
    "espece": ("species_ids", m2m_parser),
    "espece_principale": ("species_id", m2o_parser),
}

IMGS = {"img", "img_2", "img_3", "img_4", "img_5"}


def process_imgs_fields(root, rd, product):
    existing_images = product.mapped("image_ids.image_id.name")  # slow? SQL needed?
    return [
        os.path.join(root, rd[img])
        for img in IMGS
        if rd[img] and os.path.basename(rd[img]) not in existing_images
    ]


def process_product_row(root, rd):
    product_domain = [("default_code", "=", rd["sku"])]
    model = ENV["product.template"].with_context(active_test=False)
    product = model.search(product_domain)
    if product:
        translations = {}
        pfm = PRODUCT_FILE_MAPPING
        vals = {pfm[f][0]: pfm[f][1](f, rd[f]) for f in pfm}
        translations["fr_BE"] = process_lang_fields(rd, "fr_BE")
        translations["nl_BE"] = process_lang_fields(rd, "nl_BE")
        imgs = process_imgs_fields(root, rd, product)
        attribute_set_id = process_attribute_set(product, vals)
        if attribute_set_id:
            vals["attribute_set_id"] = attribute_set_id
        desc = "PIM Import Product %s" % product.name
        product.with_delay(description=desc)._pim_import(vals, translations, imgs)
    return product


def process_attribute_set(product, vals):
    if not product.attribute_set_id:
        categ_ids = vals["categ_ids"] and vals["categ_ids"][0][2]
        categ_ids = categ_ids or product.categ_ids.ids
        for cat_id in categ_ids:
            for att, cat_ids in ATTRIBUTE_SET_CATEGORY_MAPPING.items():
                if cat_id in cat_ids:
                    return att
    return False


def process_lang_fields(rd, lang):
    fields = {
        "descr_courte",
        "descr_long",
        "link_notice",
        "link_info_compl",
    }
    fields_lang = {("-".join([f, "en_GB"]), "-".join([f, lang])) for f in fields}
    vals = {}
    for fe, fl in fields_lang:
        if rd[fe] != rd[fl]:
            vals[PRODUCT_FILE_MAPPING[fe][0]] = rd[fl]
    return vals


OPTIONS_IDS = {}  # to load based on path provided at execution
SPECIES_IDS = {}
ATTRIBUTE_SET_CATEGORY_MAPPING = {}


@click.command()
@click.option("--root", required=True, help="Directory where the files are.")
@click.option("--filename", required=True, help="Main CSV.")
@click_odoo.env_options(default_log_level="info")
def main(env, root, filename, delimiter=";"):
    global ENV  # pylint: disable=global-statement
    ENV = env
    load_species_ids(SPECIES_IDS)
    load_option_ids(root, OPTIONS_IDS)
    load_attribute_set_category_mapping(ATTRIBUTE_SET_CATEGORY_MAPPING)
    return process_csv_file(root, filename, process_product_row, delimiter)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
    #  USAGE: click-odoo -c .odoorc -- scripts/load_pim_product_data.py -d odoo-alcyon --root=tmp --filename=ff
    # 1_products_export_en_GB/1_products_export_en_GB_ecom_B2B_2021-09-02_14:46:09.csv
