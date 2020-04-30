# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


def bool2int(field):
    """ A modifier intended to be used on the ``direct`` mappings.

    Convert True to 1 and False to 0

    Example::

        direct = [(bool2int('source'), 'target')]

    :param field: name of the source field in the record
    :param binding: True if the relation is a binding record
    """

    def modifier(self, record, to_attr):
        return int(record[field])

    return modifier


def dt2esbdate(field):
    """ A modifier intended to be used on the ``direct`` mappings.

    The source format is odoo.tools.DEFAULT_SERVER_DATETIME_FORMAT
    The source must be a Datetime field.

    Convert '2017-07-13 00:00:00' to '2017/07/13'

    Example::

        direct = [(dt2esbdate('source'), 'target')]

    :param field: name of the source field in the record
    :param binding: True if the relation is a binding record
    """

    def modifier(self, record, to_attr):
        value = record[field]
        if not value:
            return ''
        return value[:10].replace('-', '/')

    return modifier


def dt2nakeddate(field):
    """ A modifier intended to be used on the ``direct`` mappings.

    The source format is odoo.tools.DEFAULT_SERVER_DATETIME_FORMAT
    The source must be a Datetime field.

    Convert '2017-07-13 00:00:00' to '20170713'

    Example::

        direct = [(dt2nakeddate('source'), 'target')]

    :param field: name of the source field in the record
    :param binding: True if the relation is a binding record
    """

    def modifier(self, record, to_attr):
        value = record[field]
        if not value:
            return ''
        return value[:10].replace('-', '')

    return modifier


def falsy2emptystring(field):
    """ A modifier intended to be used on the ``direct`` mappings.

    Turn falsy values into an empty string

    Example::

        direct = [(falsy2emptystring('source'), 'target')]

    """

    def modifier(self, record, to_attr):
        value = record[field]
        if not value:
            return ''
        return value

    return modifier


def two_digits_fractional(field):
    """ A modifier intended to be used on the ``direct`` mappings.

        Convert a number so it always has 2 digits on the fractional part

    """

    def modifier(self, record, to_attr):
        return '{:.2f}'.format(record[field] or 0)

    return modifier


def three_digits_fractional(field):
    """ A modifier intended to be used on the ``direct`` mappings.

        Convert a number so it always has 3 digits on the fractional part

    """

    def modifier(self, record, to_attr):
        return '{:.3f}'.format(record[field] or 0)

    return modifier


def falsy2zero(field):
    """ A modifier intended to be used on the ``direct` mappings.

    Turn falsy values into zero 0

    Example::

        direct = [(falsy2zero('source'), 'target')]

    """

    def modifier(self, record, to_attr):
        value = record[field]
        if not value:
            return 0
        return value

    return modifier
