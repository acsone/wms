# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import AlcEdiConnectorCase


class TestResPartner(AlcEdiConnectorCase):
    def test_01(self):
        """
        Data:
            supplier not linked to an edi connector
        Test Case:
            Set use_edi_connector on the supplier
        Expected result:
            ValidationError is raised
        """
        self.assertFalse(self.supplier_no_edi.use_edi_connector)
        self.assertFalse(self.supplier_no_edi.edi_backend_id)
        with self.assertRaises(ValidationError):
            self.supplier_no_edi.use_edi_connector = True

    def test_02(self):
        """
        Data:
            supplier linked to an edi connector and using the edi connector
        Test Case:
            Unset the edi connector
        Expected result:
            ValidationError is raised
        """
        self.assertTrue(self.supplier.use_edi_connector)
        self.assertTrue(self.supplier.edi_backend_id)
        with self.assertRaises(ValidationError):
            self.supplier.edi_backend_id = False
