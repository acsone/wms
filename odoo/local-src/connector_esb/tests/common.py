# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import SavepointComponentCase

import xmlunittest
from lxml import etree


class ESBTestCase(SavepointComponentCase):

    @classmethod
    def setUpClass(cls):
        super(ESBTestCase, cls).setUpClass()

    def setUp(self):
        super(ESBTestCase, self).setUp()
        self.backend_model = self.env['esb.backend']
        self.backend = self.backend_model.get_singleton()


class ESBXMLTestCase(ESBTestCase, xmlunittest.XmlTestMixin):
    """Test XML files."""

    def flatten(self, txt):
        return ''.join([x.strip() for x in txt.splitlines()])

    def assertXmlEquivalentData(self, given, expected, unique_key):
        """Compare xml values.

        Go through all items in `expected`, selected w/ `unique_key`
        and check matching values in `given`.
        """
        gxml = etree.fromstring(given)
        exml = etree.fromstring(expected)
        for item in exml.xpath('//' + unique_key):
            # `item` is the el w/ unique_key
            # let's find its match in given xml and go up to the parent
            parent = gxml.xpath(
                '//{}[text()="{}"]/..'.format(unique_key, item.text))
            assert parent
            # then compare all the values there
            for el in item.getparent().iterchildren():
                self.assertEqual(el.text, parent[0].find(el.tag).text)
