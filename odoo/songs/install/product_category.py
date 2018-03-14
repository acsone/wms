# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def import_warnings(ctx):
    """ Importing product category warnings"""
    ProductCategory = ctx.env['product.category'].with_context(lang='fr_BE')
    content = resource_stream(req, 'data/install/product.category-fr.csv')
    load_csv_stream(ctx, ProductCategory, content, delimiter=',')
    ProductCategory = ctx.env['product.category'].with_context(lang='de_DE')
    content = resource_stream(req, 'data/install/product.category-de.csv')
    load_csv_stream(ctx, ProductCategory, content, delimiter=',')
    ProductCategory = ctx.env['product.category'].with_context(lang='nl_BE')
    content = resource_stream(req, 'data/install/product.category-nl.csv')
    load_csv_stream(ctx, ProductCategory, content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring products categories"""
    import_warnings(ctx)
