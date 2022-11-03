# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

LAST_DIGITS_RE = r'(\d+)"*$'
LAST_DIGITS_RE_OPERATOR = re.compile(LAST_DIGITS_RE)


def increment_suite_name(suite_name):
    """Increment the suite name

    We take the suite name from his sale orders and increment the last
    digit part of the last suite name:

    ex:
        sn12345 -> sn 12346
        sn - 1 - 12 -> sn - 1 - 13
        12 -> 13
        sn -> sn1
    """
    suite_name = suite_name or ""
    suite_name = suite_name.strip()
    last_digits = 0
    last_digits_search = LAST_DIGITS_RE_OPERATOR.search(suite_name)
    if last_digits_search:
        last_digits = last_digits_search.group(1)
    next_suite = str(int(last_digits) + 1)
    if last_digits_search:
        next_suite_name = LAST_DIGITS_RE_OPERATOR.sub(next_suite, suite_name)
    else:
        next_suite_name = suite_name + next_suite
    if isinstance(next_suite_name, unicode):
        next_suite_name = next_suite_name.encode("utf-8")
    return str(next_suite_name)
