from odoo.addons.alc_app_eshop_b2b.hooks import post_init_hook


def migrate(cr, version=None):
    post_init_hook(cr)
