# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def migrate(cr, version):
    xml_id_old = "specific_data.vat_tax_group"
    xml_id_new = "account_tax_one_vat.vat_tax_group"
    openupgrade.rename_xmlids(cr, [(xml_id_old, xml_id_new)])
