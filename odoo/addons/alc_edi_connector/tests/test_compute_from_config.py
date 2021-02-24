# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.server_environment import serv_config


class TestComputeFromConfig(TransactionCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super(TestComputeFromConfig, cls).setUpClass(*args, **kwargs)

        serv_config.add_section("edi_backend_test_config")
        serv_config.set("edi_backend_test_config", "channel", "sftp")
        serv_config.set("edi_backend_test_config", "hostname", "localhost")
        serv_config.set("edi_backend_test_config", "username", "test_user")
        serv_config.set("edi_backend_test_config", "password", "123ADVThudlsZ345")
        serv_config.set("edi_backend_test_config", "port", "33")
        serv_config.set(
            "edi_backend_test_config", "pk_env_variable", "4FRJIGTksu456GFdlf"
        )
        serv_config.set("edi_backend_test_config", "path_read", "/go/to/read/")
        serv_config.set("edi_backend_test_config", "path_write", "/go/to/write/")

        serv_config.add_section("edi_backend_config_second")
        serv_config.set("edi_backend_config_second", "channel", "sftp")
        serv_config.set("edi_backend_config_second", "hostname", "distanthost")
        serv_config.set("edi_backend_config_second", "username", "test_admin")
        serv_config.set("edi_backend_config_second", "password", "123ADVTlsZ345")
        serv_config.set("edi_backend_config_second", "port", "42")
        serv_config.set(
            "edi_backend_config_second", "pk_env_variable", "4FRJTksu456GFdlf"
        )
        serv_config.set(
            "edi_backend_config_second", "path_read", "/go/to/distant/read/"
        )
        serv_config.set(
            "edi_backend_config_second", "path_write", "/go/to/distant/write/"
        )

    def test_00(self):
        """
        DATA:
        config file with info for edi_backend

        Test case:
        Check that infos on edi.backend model are filled

        Expected result:
        Infos on edi.backend are the same as from the config file mimic by the serv_config.set above.
        """

        self.edi_backend1 = self.env["edi.backend"].create(
            {
                "name": "Test Config",
                "edi_export_task_def_ids": [
                    (
                        0,
                        0,
                        {
                            "kind": "ubl.order.exporter",
                            "export_filename": "PO{id}_{date}-{time}.xml",
                        },
                    )
                ],
                "edi_import_task_def_ids": [
                    (
                        0,
                        0,
                        {
                            "kind": "ubl.order.response.importer",
                            "file_matcher_pattern": "PO.*.xml$",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "kind": "ubl.despatch.advice.importer",
                            "file_matcher_pattern": "DespatchAdvice.*.xml$",
                        },
                    ),
                ],
            }
        )

        self.edi_backend2 = self.env["edi.backend"].create(
            {
                "name": "Config Second",
                "edi_export_task_def_ids": [
                    (
                        0,
                        0,
                        {
                            "kind": "ubl.order.exporter",
                            "export_filename": "PO{id}_{date}-{time}.xml",
                        },
                    )
                ],
                "edi_import_task_def_ids": [
                    (
                        0,
                        0,
                        {
                            "kind": "ubl.order.response.importer",
                            "file_matcher_pattern": "PO.*.xml$",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "kind": "ubl.despatch.advice.importer",
                            "file_matcher_pattern": "DespatchAdvice.*.xml$",
                        },
                    ),
                ],
            }
        )

        self.assertEqual(self.edi_backend1.key, "edi_backend_test_config")
        self.assertEqual(self.edi_backend1.channel, "sftp")
        self.assertEqual(self.edi_backend1.hostname, "localhost")
        self.assertEqual(self.edi_backend1.username, "test_user")
        self.assertEqual(self.edi_backend1.password, "123ADVThudlsZ345")
        self.assertEqual(self.edi_backend1.port, 33)
        self.assertEqual(self.edi_backend1.pk_env_variable, "4FRJIGTksu456GFdlf")
        self.assertEqual(self.edi_backend1.path_read, "/go/to/read/")
        self.assertEqual(self.edi_backend1.path_write, "/go/to/write/")

        self.assertEqual(self.edi_backend2.key, "edi_backend_config_second")
        self.assertEqual(self.edi_backend2.channel, "sftp")
        self.assertEqual(self.edi_backend2.hostname, "distanthost")
        self.assertEqual(self.edi_backend2.username, "test_admin")
        self.assertEqual(self.edi_backend2.password, "123ADVTlsZ345")
        self.assertEqual(self.edi_backend2.port, 42)
        self.assertEqual(self.edi_backend2.pk_env_variable, "4FRJTksu456GFdlf")
        self.assertEqual(self.edi_backend2.path_read, "/go/to/distant/read/")
        self.assertEqual(self.edi_backend2.path_write, "/go/to/distant/write/")
