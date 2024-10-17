from odoo import SUPERUSER_ID, api

from odoo.addons.alc_eshop_search_engine_ads.hooks import pre_init_hook


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if env.ref(
        "alc_eshop_ads_elasticsearch.index_config_eshop_ads",
        raise_if_not_found=False,
    ):
        env.ref("alc_eshop_search_engine_ads.index_config_eshop_ads").unlink()
        env.ref("alc_eshop_search_engine_ads.ir_cron_export_eshop_ads").unlink()
        env.cr.execute(
            """
                DELETE FROM ir_model_data
                WHERE module = 'alc_eshop_search_engine_ads'
                AND name  in (
                    'index_config_eshop_ads',
                    'ir_cron_export_eshop_ads'
            )"""
        )
        pre_init_hook(cr)
