# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    if not version:
        return
    file_path = "data/se_index_config_variants.xml"
    openupgrade.load_data(cr, "alc_search_engine", file_path, mode="init")
    # this should be followed by:
    # xml_ids = [
    #     "alc_search_engine.elasticsearch_shopinvader_variant_index_en_US",
    #     "alc_search_engine.elasticsearch_shopinvader_variant_index_nl_BE",
    #     "alc_search_engine.elasticsearch_shopinvader_variant_index_fr_BE",
    # ]
    # env.ref(xml_id).reindex()
    # But it needs a component adapter, so we will do it manually
