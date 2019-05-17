# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import anthem

from ..install.common import load_translations


@anthem.log
def post(ctx):
    """Applying update 10.0.1.36.0"""
    load_translations(
        ctx, ['website_purchase_review', 'specific_purchase'], overwrite=True
    )
