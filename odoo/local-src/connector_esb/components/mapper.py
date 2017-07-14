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
