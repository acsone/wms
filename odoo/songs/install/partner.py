# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def create_customer_category(ctx):
    """ Importing suppliers from csv """
    content = resource_stream(req, 'data/install/customer.category.csv')
    load_csv_stream(ctx, 'res.partner.category', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring partner """
    create_customer_category(ctx)
