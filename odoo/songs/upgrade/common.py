# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def deactivate_check_on_vat(ctx):
    """ Deactivate check on vat """

    # We want to activate this check after having imported partner data
    # to avoid to have an error on vat which became invalid on db2 database
    ctx.env.ref('base.main_company').write({
        'vat_check_vies': False,
    })
