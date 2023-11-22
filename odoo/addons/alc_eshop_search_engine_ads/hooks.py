from openupgradelib import openupgrade


def pre_init_hook(cr):

    # Moved xml_id from specific_data
    xml_ids = [
        "ir_cron_export_eshop_ads",
        "index_config_eshop_ads",
    ]

    openupgrade.rename_xmlids(
        cr,
        [
            (
                f"alc_eshop_ads_elasticsearch.{xml_id}",
                f"alc_eshop_search_engine_ads.{xml_id}",
            )
            for xml_id in xml_ids
        ],
    )
