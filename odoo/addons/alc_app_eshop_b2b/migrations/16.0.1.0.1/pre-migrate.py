# pylint: disable=odoo-addons-relative-import
from odoo.addons.alc_app_eshop_b2b.hooks import pre_init_hook


def migrate(cr, version=None):
    pre_init_hook(cr)
