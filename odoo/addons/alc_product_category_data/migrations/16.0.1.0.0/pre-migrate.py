# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_product_category_data.hooks import pre_init_hook


def migrate(cr, version):
    pre_init_hook(cr)
