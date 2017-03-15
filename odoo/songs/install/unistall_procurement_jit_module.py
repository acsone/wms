# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from ..common import define_settings

import anthem


@anthem.log
def main(ctx):
    """ Uninstall procurement_jit module """

    # Default invoice
    define_settings(ctx,
                    'stock.config.settings',
                    {'module_procurement_jit': 0})
