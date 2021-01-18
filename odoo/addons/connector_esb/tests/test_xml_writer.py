# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, tools

from .common import ESBXMLTestCase

TEST_DATA0 = {}
TEST_RESULT0 = """
    <ROOT>
    </ROOT>
"""

TEST_DATA1 = {"baz_out": "baz value", "foo_out": "foo value", "bar_out": "bar value"}
TEST_RESULT1 = """
    <ROOT>
        <Root xmlns:dt="urn:schemas-microsoft-com:datatypes" dt:dt="">
            <baz_out>baz value</baz_out>
            <foo_out>foo value</foo_out>
            <bar_out>bar value</bar_out>
        </Root>
    </ROOT>
"""
TEST_DATA2 = [
    {"baz_out": "baz value", "foo_out": "foo value", "bar_out": "bar value"},
    {"baz_out": "baz value 2", "foo_out": "foo value 2", "bar_out": "bar value 2"},
    {"baz_out": "baz value 3", "foo_out": "foo value 3", "bar_out": "bar value 3"},
]
TEST_RESULT2 = """
    <ROOT>
        <Root xmlns:dt="urn:schemas-microsoft-com:datatypes" dt:dt="">
            <Row>
                <baz_out>baz value</baz_out>
                <foo_out>foo value</foo_out>
                <bar_out>bar value</bar_out>
            </Row>
            <Row>
                <baz_out>baz value 2</baz_out>
                <foo_out>foo value 2</foo_out>
                <bar_out>bar value 2</bar_out>
            </Row>
            <Row>
                <baz_out>baz value 3</baz_out>
                <foo_out>foo value 3</foo_out>
                <bar_out>bar value 3</bar_out>
            </Row>
        </Root>
    </ROOT>
"""
TEST_RESULT3 = """
    <result>
        <resultItem>
            <baz_out>baz value</baz_out>
            <foo_out>foo value</foo_out>
            <bar_out>bar value</bar_out>
        </resultItem>
    </result>
"""
TEST_RESULT4 = """
    <result>
        <resultItem>
            <baz_out>baz value</baz_out>
            <foo_out>foo value</foo_out>
            <bar_out>bar value</bar_out>
        </resultItem>
        <resultItem>
            <baz_out>baz value 2</baz_out>
            <foo_out>foo value 2</foo_out>
            <bar_out>bar value 2</bar_out>
        </resultItem>
        <resultItem>
            <baz_out>baz value 3</baz_out>
            <foo_out>foo value 3</foo_out>
            <bar_out>bar value 3</bar_out>
        </resultItem>
    </result>
"""
TEST_RESULT5 = """
    <result>
        <stockItem>
            <baz_out>baz value</baz_out>
            <foo_out>foo value</foo_out>
            <bar_out>bar value</bar_out>
        </stockItem>
        <stockItem>
            <baz_out>baz value 2</baz_out>
            <foo_out>foo value 2</foo_out>
            <bar_out>bar value 2</bar_out>
        </stockItem>
        <stockItem>
            <baz_out>baz value 3</baz_out>
            <foo_out>foo value 3</foo_out>
            <bar_out>bar value 3</bar_out>
        </stockItem>
    </result>
"""


class XMLTestCase(ESBXMLTestCase):
    def setUp(self):
        super(XMLTestCase, self).setUp()
        self.timestamp = self.env.ref("connector_esb.esb_timestamp_product")

    @property
    def model(self):
        return self.env["product.product"]

    def test_path(self):
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            writer = work.component(usage="local.xml.writer")
            self.assertEqual(writer.path(), "/tmp")

        self.timestamp.path = "/write/here/please"
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            writer = work.component(usage="local.xml.writer")
            self.assertEqual(writer.path(), "/write/here/please")

        backend = self.backend.with_context(xml_out_path="/somewhere/else")
        with backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            writer = work.component(usage="local.xml.writer")
            self.assertEqual(writer.path(), "/somewhere/else")

    def test_default_filename(self):
        today = fields.Date.today().replace("-", "")
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            writer = work.component_by_name("esb.xml.writer")
            self.assertEqual(writer.filename(), u"Products_{}.xml".format(today))

    @tools.mute_logger("dicttoxml")
    def test_xml_base(self):
        with self.backend.work_on(self.model._name) as work:
            writer = work.component(usage="xml.producer")
            result = writer.produce(TEST_DATA1)
            root = self.assertXmlDocument(result)
            paths = ("//Root", "//bar_out", "//foo_out", "//baz_out")
            self.assertXpathsExist(root, paths)
            self.assertXmlEquivalentOutputs(
                self.flatten(result), self.flatten(TEST_RESULT1)
            )

    @tools.mute_logger("dicttoxml")
    def test_xml_multiple_lines(self):
        with self.backend.work_on(self.model._name) as work:
            writer = work.component(usage="xml.producer")
            result = writer.produce(TEST_DATA2)
            root = self.assertXmlDocument(result)
            paths = ("//Root", "//Row/bar_out", "//Row/foo_out", "//Row/baz_out")
            self.assertXpathsExist(root, paths)
            self.assertXmlEquivalentOutputs(
                self.flatten(result), self.flatten(TEST_RESULT2)
            )

    @tools.mute_logger("dicttoxml")
    def test_xml_webservice_base(self):
        with self.backend.work_on(self.model._name) as work:
            writer = work.component(usage="xml.webservice.producer")
            result = writer.produce([TEST_DATA1])
            root = self.assertXmlDocument(result)
            paths = ("//resultItem", "//bar_out", "//foo_out", "//baz_out")
            self.assertXpathsExist(root, paths)
            self.assertXmlEquivalentOutputs(
                self.flatten(result), self.flatten(TEST_RESULT3)
            )

    @tools.mute_logger("dicttoxml")
    def test_xml_webservice_multiple_lines(self):
        with self.backend.work_on(self.model._name) as work:
            writer = work.component(usage="xml.webservice.producer")
            result = writer.produce(TEST_DATA2)
            root = self.assertXmlDocument(result)
            paths = (
                "//resultItem",
                "//resultItem/bar_out",
                "//resultItem/foo_out",
                "//resultItem/baz_out",
            )
            self.assertXpathsExist(root, paths)
            self.assertXmlEquivalentOutputs(
                self.flatten(result), self.flatten(TEST_RESULT4)
            )

    @tools.mute_logger("dicttoxml")
    def test_xml_webservice_different_list_item(self):
        with self.backend.work_on(self.model._name) as work:
            writer = work.component(usage="xml.webservice.producer")
            result = writer.produce(TEST_DATA2, list_item_el="stockItem")
            root = self.assertXmlDocument(result)
            paths = (
                "//stockItem",
                "//stockItem/bar_out",
                "//stockItem/foo_out",
                "//stockItem/baz_out",
            )
            self.assertXpathsExist(root, paths)
            self.assertXmlEquivalentOutputs(
                self.flatten(result), self.flatten(TEST_RESULT5)
            )

    @tools.mute_logger("dicttoxml")
    def test_xml_base_empty(self):
        with self.backend.work_on(self.model._name) as work:
            writer = work.component(usage="xml.producer")
            result = writer.produce(TEST_DATA0)
            root = self.assertXmlDocument(result)
            paths = ()
            self.assertXpathsExist(root, paths)
            self.assertXmlEquivalentOutputs(
                self.flatten(result), self.flatten(TEST_RESULT0)
            )

    @tools.mute_logger("dicttoxml")
    def test_no_xml_version(self):
        with self.backend.work_on(self.model._name) as work:
            writer = work.component(usage="xml.producer")
            result = writer.produce(TEST_DATA0)
            result = self.flatten(result)
            self.assertEqual(result.find("version"), -1)
