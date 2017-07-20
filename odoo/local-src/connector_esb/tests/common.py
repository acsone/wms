# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from collections import defaultdict
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

        # don't check the comments in the examples
        comments = exml.xpath('//comment()')
        for c in comments:
            p = c.getparent()
            p.remove(c)

        missing_elems = defaultdict(list)
        content_differs = defaultdict(list)
        for item in exml.xpath('//' + unique_key):
            # `item` is the el w/ unique_key
            # let's find its match in given xml and go up to the parent
            parent = gxml.xpath(
                '//{}[text()="{}"]/..'.format(unique_key, item.text))
            assert parent
            # then compare all the values there
            for expected_elem in item.getparent().iterchildren():
                elem = parent[0].find(expected_elem.tag)
                if elem is None:
                    missing_elems[item.text].append(expected_elem.tag)
                else:
                    if expected_elem.text != elem.text:
                        content_differs[item.text].append(
                            (elem.tag, expected_elem.text, elem.text)
                        )

        if missing_elems or content_differs:
            message = []
            keys = set(list(missing_elems) + list(content_differs))
            for key in keys:
                message.append(
                    u'Row with unique key: %s' % key
                )

                tags = missing_elems[key]
                if tags:
                    message.append(u'  Missing elements')
                for tag in tags:
                    message.append(u'   - {}'.format(tag))
                elems = content_differs[key]
                if elems:
                    message.append(u'  Content differs')
                for tag, expected, got in elems:
                    message.append(
                        u"   - {}: expect {!r}, got {!r}".format(
                            tag, expected, got
                        )
                    )
                message.append('')

            raise AssertionError(u'XML does not match:\n\n{}'.format(
                '\n'.join(message)
            ))

    def read_test_file(self, filename):
        path = os.path.join(
            os.path.dirname(__file__),
            'examples',
            filename
        )
        with open(path, 'r') as thefile:
            return thefile.read()
