# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import vatnumber


def vat(value):
    value = (value or '').strip().lower()
    if not value:
        return False

    country, number = value[:2], value[2:].replace(' ', '')
    if country not in vatnumber.countries():
        return False

    return getattr(vatnumber, 'check_vat_' + country)(value)
