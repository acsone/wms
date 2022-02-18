# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

import mock

from odoo.tools import mute_logger

from odoo.addons.alc_documents.tests.common import TestAlcDocuments
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestDocumentsService(TestAlcDocuments, ComponentMixin):
    @classmethod
    @mute_logger("odoo.addons.queue_job.models.base")
    def setUpClass(cls):
        super(TestDocumentsService, cls).setUpClass()
        cls.setUpComponent()
        cls.partner_other = cls.env["res.partner"].create({"name": "Other"})

        # create a partner document
        vals_sale_order = cls._get_vals_sale_order()
        vals_sale_order["sale_channel"] = "phone"
        sale_order = cls.so_model_no_delay.create(vals_sale_order)
        sale_order.action_confirm()
        sale_order.create_reports()

    @classmethod
    @contextmanager
    def documents_service(cls, partner=None):
        partner_id = (partner or cls.partner).id
        context = dict(cls.env.context, authenticated_partner_id=partner_id)
        env = cls.env(context=context)
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=partner_id,
        )
        yield work.component(usage="documents")
