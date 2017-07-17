# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import anthem
from ...install.accounting import set_esb_references


@anthem.log
def main(ctx):
    """ post-update 10.5.0 """
    set_esb_references(ctx)
