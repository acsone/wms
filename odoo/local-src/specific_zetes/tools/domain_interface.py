# -*- coding: utf-8 -*-
import logging

from openerp.addons.web.http import request

_logger = logging.getLogger(__name__)
# ONLY FOR TEST
_logger.setLevel(logging.DEBUG)

HEADER_LABELS = ('serNum', 'verNum', 'appNum', 'msgType', 'operId', 'langId',
            'msgDate', 'msgTime', 'packageId')


class DomainInterface:
    EXAMPLE_REQU = ''
    EXAMPLE_RESP = ''
    EXAMPLE_RESU = ''
    REQU = ()
    RESP = ()
    RESU = ()

    def __init__(self, header):
        self._header = header
        operator_code = header[4]
        self._user = request.env['res.users'].get_user(operator_code)
        _logger.debug('User: {}'.format(self._user.name or 'no user'))

    def requ(self, params):
        raise NotImplementedError('Please implement this method')

    def resu(self, params):
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
        new_header[3] = method

        self.__dict__.update(dict(zip(HEADER_LABELS, new_header)))
        self._labels = labels
        self._action = action
        self._domain = domain

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

        labels = HEADER_LABELS + self._labels
        default_values = self.get_example()

        values = []
        for i in range(len(labels)):
            key = labels[i]

            if not i:
                values.append('----------- header -----------')
            if i == len(HEADER_LABELS):
                values.append('----------- values -----------')

            value = getattr(self, key, '')
            if isinstance(value, (str, unicode)):
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
        for label in HEADER_LABELS + self._labels:
            value = getattr(self, label, '')
            if value is not 0 and not value:
                value = ''
            elif isinstance(value, (str, unicode)):
                value = value.encode('utf-8').replace(',', ' ')
            elif isinstance(value, (int, float)):
                value = str(value)
            else:
                raise Exception('Cannot format the value {} with type {}'
                                .format(value, type(value)))

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
        labels = HEADER_LABELS + self._labels
        current_labels = self.get_labels()

        bad_values = set(current_labels) - set(labels)
        if bad_values:
            message = 'Some attributes are not valid: {}'\
                .format(', '.join(list(bad_values)))
            _logger.error(message)

        default_values = self.get_example()
        if len(default_values) != len(ordered_values):
            _logger.error('The number of label doen\'t correspond '
                            'to the example size')

        empty_mandatory_values = []
        for i in range(len(labels)):
            if default_values[i] and not ordered_values[i]:
                empty_mandatory_values.append(labels[i])

        if empty_mandatory_values:
            _logger.warning('There are some missing mandatory values: {}'
                            .format(', '.join(empty_mandatory_values)))
