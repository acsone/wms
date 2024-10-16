from odoo import SUPERUSER_ID, api

from odoo.addons.alc_eshop_search_engine_info_banner.hooks import pre_init_hook


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if env.ref(
        "alc_eshop_info_banner_elasticsearch.index_config_eshop_info_banner",
        raise_if_not_found=False,
    ):
        env.ref(
            "alc_eshop_search_engine_info_banner.index_config_eshop_info_banner"
        ).unlink()
        env.ref(
            "alc_eshop_search_engine_info_banner.ir_cron_contract_costs_generator"
        ).unlink()
        env.cr.execute(
            """
                DELETE FROM ir_model_data
                WHERE module = 'alc_eshop_search_engine_info_banner'
                AND name  in (
                    'index_config_eshop_info_banner',
                    'ir_cron_contract_costs_generator'
            )"""
        )

        pre_init_hook(cr)
