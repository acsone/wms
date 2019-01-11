# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import update_translations


@anthem.log
def translations(ctx):
    update_translations(ctx, ['specific_report'])
