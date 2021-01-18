# -*- coding: utf-8 -*-
import logging
import StringIO
import traceback
import uuid

from odoo import _
from odoo.http import request
from odoo.tools import frozendict

from .. import constants

_logger = logging.getLogger(__name__)


class Savepoint(object):
    def __init__(self, cr):
        self._cr = cr
        self._name = uuid.uuid1().hex

    def start(self):
        self._cr.execute('SAVEPOINT "%s"' % self._name)

    def release(self):
        self._cr.execute('RELEASE SAVEPOINT "%s"' % self._name)

    def rollback(self):
        self._cr.execute('ROLLBACK TO SAVEPOINT "%s"' % self._name)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type_, value, _traceback):
        if type_:
            self.rollback()
        self.release()


class DomainInterface(object):
    EXAMPLE_REQU = ""
    EXAMPLE_RESP = ""
    EXAMPLE_RESU = ""
    REQU = ()
    RESP = ()
    RESU = ()

    def __init__(self, header, savepoint):
        self.request = request

        self._savepoint = savepoint
        self._header = header
        # Retrieve the current user
        operator_code = header[constants.USER_INDEX]
        self._operator_user = self.env["res.users"].sudo().get_user(operator_code)
        if self._operator_user:
            self.request.context = frozendict(
                self.request.context,
                lang=self._operator_user.lang,
                zetes_operator_uid=self._operator_user.id,
            )
            # Reset the environment so it will build a new one using
            # the updated context (it will keep the same cr and uid).
            # We have to keep using the zetes user as uid to have proper
            # permissions.
            self.request._env = None

        _logger.debug(u"User: %s", (self._operator_user.name or "no user"))

    def __repr__(self):
        return u"{}({!r}, {!r}, {!r})".format(
            self.__class__.__name__, self._header, self._savepoint, self.request
        )

    def rollback_to_savepoint(self):
        """Rollback to savepoint

        The savepoint is injected at instance creation, so it is likely that
        you will rollback everything that has been done by this DomainInterface
        since it has been created.
        """
        self._savepoint.rollback()

    def requ(self, params):
        """
        A requ should always return something.
        This kind of request will execute a method and return the result.
        During the execution of the method, Zetes will wait.

        This method must be implemented by each domain
        :param params:
        :return:
        """
        raise NotImplementedError("Please implement this method")

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
        raise NotImplementedError("Please implement this method")

    @property
    def env(self):
        return self.request.env

    def _get_pack_operation(self, _id, params, log_error_if_not_found=True):
        """
        Return the pack operation if it exists (None otherwise)
        """
        pack_op = self.env["stock.pack.operation"].search([("id", "=", _id)])
        if not pack_op and log_error_if_not_found:
            self._log_pack_op_not_found_error(_id, params)
        return pack_op

    def _log_pack_op_not_found_error(self, not_found_id, params):
        picking_id = (
            self.env["stock.pack.operation.deleted"].get(not_found_id).picking_id
        )
        if not picking_id:
            _logger.warning("Pack operations id %s unknown", not_found_id)
            return
        params.log(
            picking_id=picking_id.id,
            operation_id=None,
            exception=_("Try to process a deleted pack operation %s") % not_found_id,
            error_type="technical",
            requires_check=True,
        )


class Parameters(object):
    def __init__(self, domain, action="resp", values=None):
        """
        Init the parameter
        :param domain: DomainInterface<class>: a link to the domain
        :param action: string: the action name
        :param values: list: a list of values (optional)
        """
        labels = getattr(domain, action.upper())

        new_header = list(domain._header)
        method = u"{}_{}".format(action.upper(), domain.__class__.__name__.upper())
        new_header[constants.METHOD_INDEX] = method

        self.__dict__.update(dict(zip(constants.HEADER_LABELS, new_header)))
        self._labels = labels
        self._action = action
        self._domain = domain

        if values:
            formatted_values = [value.strip() for value in values]
            self.__dict__.update(dict(zip(labels, formatted_values)))
            _logger.debug(str(self))

    def __repr__(self):
        return u"Parameters({!r}, {!r}, {!r})".format(
            self._domain, self._action, self.__dict__
        )

    def __str__(self):
        """
        Display the current parameter.
        If the value of the parameter has an example we display this value
        :return:
        """
        title = "===========> {}_{} <===========".format(
            self._action.upper(), self._domain.__class__.__name__.upper()
        )

        if not self._labels:
            return "{}\nNO VALUES".format(title)

        labels = constants.HEADER_LABELS + self._labels
        default_values = self.get_example()

        values = []
        for i, key in enumerate(labels):
            if not i:
                values.append("----------- header -----------")
            if i == len(constants.HEADER_LABELS):
                values.append("----------- values -----------")

            value = getattr(self, key, "")
            if isinstance(value, unicode):
                value = value.encode("utf-8").replace(",", " ")

            elif isinstance(value, (int, float)):
                value = str(value)

            if i < len(default_values) and default_values[i]:
                line = "{}. {}: {} ({})".format(i + 1, key, value, default_values[i])
            else:
                line = "{}. {}: {}".format(i + 1, key, value)
            values.append(line)

        return "{}\n{}".format(title, "\n".join(values))

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
        example_str = getattr(self._domain, "EXAMPLE_{}".format(action), [])
        if not example_str:
            return []

        return example_str.split(",")

    def get_labels(self):
        """
        Return a list with all labels
        :return: None
        """
        return [key for key in self.__dict__ if not key.startswith("_")]

    def format(self):
        """
        Format the parameter to have the good format for zetes.
        All values must be separated by a comma
        :return: Return a string
        """
        ordered_values = []
        for label in constants.HEADER_LABELS + self._labels:
            value = getattr(self, label, "")
            # pylint: disable=unidiomatic-typecheck
            if not value and type(value) is not int:
                value = ""
            elif isinstance(value, (str, unicode)):
                value = value.encode("utf-8").replace(",", " ")
            elif isinstance(value, (int, float)):
                value = str(value)
            else:
                raise Exception(
                    _("Cannot format the value %s with type %s") % (value, type(value))
                )

            ordered_values.append(value)

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(str(self))
            self.check(ordered_values)

        # Insert an empty value (used by Zetes)
        ordered_values.insert(0, "")

        return ",".join(ordered_values)

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
            message = _("Some attributes are not valid: %s") % ", ".join(
                list(bad_values)
            )
            _logger.error(message)

        default_values = self.get_example()
        if len(default_values) != len(ordered_values):
            _logger.error(
                _("The number of attributes doen't correspond " "to the example size")
            )

        empty_mandatory_values = []
        for i, label in enumerate(labels):
            if default_values[i] and not ordered_values[i]:
                empty_mandatory_values.append(label)

        if empty_mandatory_values:
            _logger.warning(
                _("There are some missing mandatory values: %s"),
                ", ".join(empty_mandatory_values),
            )

    def log(
        self,
        picking_id=None,
        operation_id=None,
        exception=None,
        error_type=None,
        requires_check=False,
    ):
        """
        Log an error in Odoo
        :param picking_id:  The picking ID (stock.picking)
        :param operation_id: The operation ID (stock.pack.operation)
        :param exception: An exception (the object himself or a string)
        :param error_type: The type of error (technical or human)
        :return: None
        """

        if exception and not isinstance(exception, (str, unicode)):
            exception = str(exception)

        stack = StringIO.StringIO()
        traceback.print_stack(file=stack)
        stack.seek(0)
        call_stack = stack.getvalue()

        self._domain.request.env["zetes.logger"].sudo().create(
            {
                "domain": self._domain.__class__.__name__.lower(),
                "action": self._action.lower(),
                "request": self.format(),
                "formatted_request": str(self),
                "user_id": (
                    self._domain._operator_user and self._domain._operator_user.id
                ),
                "error_type": error_type or "technical",
                "picking_id": picking_id,
                "operation_id": operation_id,
                "traceback": exception,
                "call_stack": call_stack,
                "requires_check": requires_check,
            }
        )

    def parse_line_id(self, line_id):
        """
        Parse value from request and extract the lot_id and the pack_operation
        id from lineId
        return tuple (pack_operation id, lot id)
        """
        if not line_id:
            return None, None

        if isinstance(line_id, int):
            line_id = str(line_id)

        line_id_list = line_id.split("_")
        if len(line_id_list) == 2:
            pack_operation_id = int(line_id_list[0])
            lot_id = int(line_id_list[1])
        else:
            pack_operation_id = int(line_id)
            lot_id = None
        return pack_operation_id, lot_id
