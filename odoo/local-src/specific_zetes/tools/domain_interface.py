# -*- coding: utf-8 -*-
import logging

from odoo import _
from odoo.http import request

from .. import constants

_logger = logging.getLogger(__name__)


class DomainInterface:
    EXAMPLE_REQU = ''
    EXAMPLE_RESP = ''
    EXAMPLE_RESU = ''
    REQU = ()
    RESP = ()
    RESU = ()

    def __init__(self, header, request_overwrite=None):
        if request_overwrite:
            self.request = request_overwrite
        else:
            self.request = request

        self._header = header
        # Retrieve the current user
        operator_code = header[constants.USER_INDEX]
        self._user = self.request.env['res.users'].get_user(operator_code)
        _logger.debug('User: {}'.format(self._user.name or 'no user'))

    def requ(self, params):
        """
        A requ should always return something.
        This kind of request will execute a method and return the result.
        During the execution of the method, Zetes will wait.

        This method must be implemented by each domain
        :param params:
        :return:
        """
        raise NotImplementedError('Please implement this method')

    def resu(self, params):
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        This method must be implemented by each domain.
        :param params:
        :return:
        """
        raise NotImplementedError('Please implement this method')


class Parameters:
    def __init__(self, domain, action='resp', values=None):
        """
        Init the parameter
        :param domain: DomainInterface<class>: a link to the domain
        :param action: string: the action name
        :param values: list: a list of values (optional)
        """
        labels = getattr(domain, action.upper())

        new_header = list(domain._header)
        method = '{}_{}'.format(action.upper(),
                                domain.__class__.__name__.upper())
        new_header[constants.METHOD_INDEX] = method

        self.__dict__.update(dict(zip(constants.HEADER_LABELS, new_header)))
        self._labels = labels
        self._action = action
        self._domain = domain

        if domain._user:
            domain.request.context = \
                dict(domain.request.context, lang=domain._user.lang)

        if values:
            formatted_values = [value.strip() for value in values]
            self.__dict__.update(dict(zip(labels, formatted_values)))
            _logger.debug(str(self))

    def __str__(self):
        """
        Display the current parameter.
        If the value of the parameter has an example we display this value
        :return:
        """
        title = '===========> {}_{} <==========='.format(
            self._action.upper(),
            self._domain.__class__.__name__.upper(),
        )

        if not self._labels:
            return '{}\nNO VALUES'.format(title)

        labels = constants.HEADER_LABELS + self._labels
        default_values = self.get_example()

        values = []
        for i in range(len(labels)):
            key = labels[i]

            if not i:
                values.append('----------- header -----------')
            if i == len(constants.HEADER_LABELS):
                values.append('----------- values -----------')

            value = getattr(self, key, '')
            if isinstance(value, unicode):
                value = value.encode('utf-8').replace(',', ' ')

            elif isinstance(value, (int, float)):
                value = str(value)

            if i < len(default_values) and default_values[i]:
                line = '{}. {}: {} ({})'.format(i + 1,
                                                key,
                                                value,
                                                default_values[i])
            else:
                line = '{}. {}: {}'.format(i + 1,
                                           key,
                                           value)
            values.append(line)

        return '{}\n{}'.format(title, '\n'.join(values))

    def update(self, values):
        """
        Update the current parameter with new values
        :param values: a dictionary with new values
        :return: None
        """
        self.__dict__.update(values)

    def get_example(self):
        """
        Return an example for this action
        :return: None
        """
        action = self._action.upper()
        example_str = getattr(self._domain, 'EXAMPLE_{}'.format(action), [])
        if not example_str:
            return []

        return example_str.split(',')

    def get_labels(self):
        """
        Return a list with all labels
        :return: None
        """
        return [key for key in self.__dict__.keys() if not key.startswith('_')]

    def format(self):
        """
        Format the parameter to have the good format for zetes.
        All values must be separated by a comma
        :return: Return a string
        """
        ordered_values = []
        for label in constants.HEADER_LABELS + self._labels:
            value = getattr(self, label, '')
            if value is not 0 and not value:
                value = ''
            elif isinstance(value, (str, unicode)):
                value = value.encode('utf-8').replace(',', ' ')
            elif isinstance(value, (int, float)):
                value = str(value)
            else:
                raise Exception(_('Cannot format the value %s with type %s'
                                  ) % (value, type(value)))

            ordered_values.append(value)

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(str(self))
            self.check(ordered_values)

        # Insert an empty value (used by Zetes)
        ordered_values.insert(0, '')

        return ','.join(ordered_values)

    def check(self, ordered_values):
        """
        This method will check following rules:
        - The parameter has no values with wrong label
        - The size of the result corresponds to the example
        - The parameter contains all mandatory values
        :param ordered_values:
        :return: None
        """
        labels = constants.HEADER_LABELS + self._labels
        current_labels = self.get_labels()

        bad_values = set(current_labels) - set(labels)
        if bad_values:
            message = _('Some attributes are not valid: {}'
                        .format(', '.join(list(bad_values))))
            _logger.error(message)

        default_values = self.get_example()
        if len(default_values) != len(ordered_values):
            _logger.error(_('The number of attributes doen\'t correspond '
                            'to the example size'))

        empty_mandatory_values = []
        for i in range(len(labels)):
            if default_values[i] and not ordered_values[i]:
                empty_mandatory_values.append(labels[i])

        if empty_mandatory_values:
            _logger.warning(_('There are some missing mandatory values: {}'
                            .format(', '.join(empty_mandatory_values))))

    def log(self, picking_id=None, operation_id=None,
            exception=None, error_type=None):
        """
        Log an error in Odoo
        :param picking_id:  The picking ID (stock.picking)
        :param operation_id: The operation ID (stock.pack.operation)
        :param exception: An exception (the object himself)
        :param error_type: The type of error (technical or human)
        :return: None
        """
        self._domain.request.env['zetes.logger'].sudo().create({
            'domain': self._domain.__class__.__name__.lower(),
            'action': self._action.lower(),
            'request': self.format(),
            'formatted_request': str(self),
            'user_id': self._domain._user and self._domain._user.id,
            'error_type': error_type or 'technical',
            'picking_id': picking_id,
            'operation_id': operation_id,
            'traceback': exception and str(exception) or None,
        })
