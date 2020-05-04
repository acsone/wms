# -*- coding: utf-8 -*-
import mock

from .. import constants
from ..tools.domain_interface import DomainInterface, Parameters
from ..tools.domain_usercontext import Usercontext
from .zetes_test_classes import OPERATOR_CODE, ZetesTest


class TestDomainInterface(ZetesTest):
    def test_domain(self):
        """
        Create a simple domain without any values
        :return:
        """
        header_unknown_user = [
            "208030824",
            "2.2.3",
            "3iV_101",
            "REQU_USERCONTEXT",
            "111",
            "1",
            "20170207",
            "072932",
            "98427733121320",
        ]

        domain = DomainInterface(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )
        self.assertEqual(domain._operator_user.id, self.operator_user.id)

        domain_with_unknow_user = DomainInterface(
            header_unknown_user, mock.MagicMock(name="Savepoint()")
        )
        self.assertEqual(domain_with_unknow_user._operator_user, self.env["res.users"])

    def test_params(self):
        """
        Create a parameters (from a usercontext domain)
        :return:
        """
        domain = Usercontext(self._default_header(), mock.MagicMock(name="Savepoint()"))
        response_params = Parameters(domain)

        # Check values
        self.assertEqual(response_params.serNum, "208030824")
        self.assertEqual(response_params.operId, OPERATOR_CODE)
        self.assertEqual(response_params.packageId, "98427733121320")
        self.assertEqual(response_params.msgType, "RESP_USERCONTEXT")

        self.assertEqual(response_params._labels, Usercontext.RESP)
        self.assertEqual(response_params._action, "resp")

        result_str = response_params.format()
        result_expected = (
            ",208030824,2.2.3,3iV_101,RESP_USERCONTEXT,99,1,20170207,072932,"
            "98427733121320,,,,,,,,,,,,,,,,,,,"
        )
        self.assertEqual(result_str, result_expected)

    def test_execute_simple_request(self):
        """
        Try to execute a simple request
        :return:
        """
        domain = Usercontext(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update({"contextType": "1"})
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.assignmentType, "1")
        self.assertEqual(result.operName, "User test")
        self.assertEqual(result._domain._operator_user.operator_code, OPERATOR_CODE)

        # Execute the method str
        expected_title = "===========> RESP_USERCONTEXT <==========="
        self.assertTrue(expected_title in result.__str__())

        # Change a value in the object
        result.respCode = constants.RESPONSE_CODE_ERROR
        self.assertEqual(result.respCode, constants.RESPONSE_CODE_ERROR)

        # Execute the method get_example
        example = result.get_example()
        self.assertEqual(",".join(example), result._domain.EXAMPLE_RESP)
