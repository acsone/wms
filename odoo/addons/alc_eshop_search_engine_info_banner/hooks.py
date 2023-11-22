from openupgradelib import openupgrade


def pre_init_hook(cr):

    # Moved xml_id from specific_data
    xml_ids = [
        "ir_cron_export_eshop_info_banners",
        "index_config_eshop_info_banner",
    ]

    openupgrade.rename_xmlids(
        cr,
        [
            (
                f"alc_eshop_info_banner_elasticsearch.{xml_id}",
                f"alc_eshop_search_engine_info_banner.{xml_id}",
            )
            for xml_id in xml_ids
        ],
    )
