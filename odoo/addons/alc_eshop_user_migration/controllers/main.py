# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.controllers import main


class RestController(main.RestController):
    _root_path = "/magento_account_validator/"
    _collection_name = "magento.account.validator"
