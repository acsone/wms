# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import Counter
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

        missing_elems = Counter()
        content_differs = Counter()
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
                    missing_elems.update([expected_elem.tag])
                else:
                    if expected_elem.text != elem.text:
                        content_differs.update(
                            [(elem.tag, expected_elem.text, elem.text)]
                        )

        if missing_elems or content_differs:
            message = []
            if missing_elems:
                message.append(u'Missing elements')
            for tag, count in missing_elems.items():
                message.append(u' - {} ({} times)'.format(tag, count))
            if content_differs:
                message.append(u'Wrong elements')
            for (tag, expected, got), count in content_differs.items():
                message.append(
                    u" - in '{}' expect {!r}, got {!r} ({} times)".format(
                        tag, expected, got, count
                    )
                )

            raise AssertionError(u'XML does not match:\n\n{}'.format(
                '\n'.join(message)
            ))
