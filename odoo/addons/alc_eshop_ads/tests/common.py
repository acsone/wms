# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import datetime
import os

from odoo.addons.component.tests.common import SavepointComponentCase


class TestEShopAdsCommon(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(TestEShopAdsCommon, cls).setUpClass()
        cls.EShopAds = cls.env["alc.eshop.ads"]
        cls.image = cls._get_image("black-image.jpg")

    @classmethod
    def _get_date(cls, day_offset=0):
        return datetime.date.today() + datetime.timedelta(days=day_offset)

    @classmethod
    def _get_image(cls, name):
        path = os.path.dirname(os.path.abspath(__file__))
        f = open(os.path.join(path, "static", name))
        return base64.b64encode(f.read())
