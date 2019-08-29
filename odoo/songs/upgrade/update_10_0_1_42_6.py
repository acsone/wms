# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem

from ..common import define_settings


@anthem.log
def settings_account_config(ctx):
    """ Set tax calculation method as round_per_line """

    define_settings(
        ctx,
        'account.config.settings',
        {'tax_calculation_rounding_method': 'round_per_line'},
    )


@anthem.log
def post(ctx):
    """Applying update 10.0.1.42.6"""
    settings_account_config(ctx)
