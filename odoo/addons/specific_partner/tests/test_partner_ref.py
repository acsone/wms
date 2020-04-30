# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SavepointCase


class ResPartnerRefTestCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(ResPartnerRefTestCase, cls).setUpClass()
        ref_seq = cls.env.ref('base_partner_sequence.seq_res_partner')
        ref_seq.prefix = ''
        cls.fiji = cls.env.ref('base.fj')
        cls.fiji.esb_ref = '341'
        cls.model = cls.env['res.partner']
        cls.partner = cls.env['res.partner'].create(
            {'name': 'Doe Headquarters'}
        )

    def test_ref_unique_in_partner_contact(self):
        """Check that children of partner have a unique ref."""
        partner_contact = self.model.create(
            {
                'name': 'John',
                'type': 'contact',
                'parent_id': self.partner.id,
                'customer': True,
            }
        )

        assert self.partner.ref != partner_contact.ref
        self.assertTrue(partner_contact.ref)

        partner_address = self.model.create(
            {
                'name': 'Address',
                'parent_id': self.partner.id,
                'type': 'invoice',
                'street': 'street',
                'city': 'city',
                'zip': 'zip',
                'country_id': self.fiji.id,
            }
        )

        assert self.partner.ref != partner_address.ref
        self.assertTrue(partner_address.ref)
