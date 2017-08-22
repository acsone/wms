# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.uninstaller import uninstall


@anthem.log
def uninstall_sale_product_additional(ctx):
    """ Uninstall sale_product_additional modules """
    uninstall(ctx, ['sale_product_additional'])


@anthem.log
def main(ctx):
    """ Main: update 10.7.0 """
    uninstall_sale_product_additional(ctx)
