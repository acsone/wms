# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "alc_eshop_app.eshop_technical_user_group",
                "alc_app_eshop_b2b.eshop_technical_user_group",
            ),
            (
                "alc_eshop_app.eshop_manager_group",
                "alc_app_eshop_b2b.eshop_manager_group",
            ),
        ],
    )
    # xmli_ids from alc_search_engine
    xml_ids = [
        "index_config_shopinvader_variant_fr",
        "index_config_shopinvader_variant_nl",
        "index_config_shopinvader_variant_en",
        "index_config_shopinvader_category",
        "elasticsearch_shopinvader_variant_index_fr_BE",
        "elasticsearch_shopinvader_variant_index_nl_BE",
        "elasticsearch_shopinvader_variant_index_en_US",
        "elasticsearch_shopinvader_category_index_fr_BE",
        "elasticsearch_shopinvader_category_index_nl_BE",
        "elasticsearch_shopinvader_category_index_en_US",
        "eshop_ads_index_fr_BE",
        "eshop_ads_index_nl_BE",
        "eshop_ads_index_en",
        "eshop_info_banner_index_fr_BE",
        "eshop_info_banner_index_nl_BE",
        "eshop_info_banner_index_en",
    ]

    openupgrade.rename_xmlids(
        cr,
        [
            (f"alc_search_engine.{xml_id}", f"alc_app_eshop_b2b.{xml_id}")
            for xml_id in xml_ids
        ],
    )

    # xml_ids from shopinvader_image
    xml_ids = [
        "small",
        "medium",
        "large",
    ]
    openupgrade.rename_xmlids(
        cr,
        [
            (f"shopinvader_image.{xml_id}", f"alc_app_eshop_b2b.{xml_id}")
            for xml_id in xml_ids
        ],
    )


def post_init_hook(cr, registry=None):
    # reload index definitions
    openupgrade.load_data(cr, "alc_app_eshop_b2b", "data/se_index.xml", mode="init")
