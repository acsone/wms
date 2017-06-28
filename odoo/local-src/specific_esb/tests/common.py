# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase

import xmlunittest
import xmltodict


class ESBTestCase(SavepointCase):

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(ESBTestCase, cls).setUpClass()
        cls.setup_languages()

    @classmethod
    def setup_languages(cls):
        installed = cls.env['res.lang'].search([
            ('translatable', '=', True)]).mapped('code')
        for code in ('fr_BE', 'nl_BE', 'de_DE'):
            if code not in installed:
                cls.env['base.language.install'].create(
                    {'lang': code}).lang_install()

    def setUp(self):
        super(ESBTestCase, self).setUp()
        self.backend_model = self.env['esb.backend']
        self.backend = self.backend_model.create({'name': 'ESB test'})


class ESBXMLTestCase(ESBTestCase, xmlunittest.XmlTestMixin):
    """Test XML files."""

    def flatten(self, txt):
        return ''.join([x.strip() for x in txt.splitlines()])

    def assertXmlEquivalentData(self, given, expected):
        """Compare xml values."""
        # xmlunittest.assertXmlEquivalentOutputs
        # fails if the files are not identical
        # so if the elements' order changes
        # is going to raise an error.
        import pdb; pdb.set_trace()
        self.assertDictEqual(
            xmltodict.parse(given),
            xmltodict.parse(expected)
        )
