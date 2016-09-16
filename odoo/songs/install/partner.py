# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def create_partner_categories(ctx):
    """ Creating partner categories """
    content = resource_stream(req, 'data/install/partner.category.csv')
    load_csv_stream(ctx, 'partner.alcyon_category', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring partner """
    create_partner_categories(ctx)
