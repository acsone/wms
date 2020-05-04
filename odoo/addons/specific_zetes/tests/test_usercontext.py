# -*- coding: utf-8 -*-
import mock

from .. import constants
from ..tools.domain_interface import Parameters
from ..tools.domain_usercontext import Usercontext
from .zetes_test_classes import ZetesTest


class TestUsercontext(ZetesTest):
    def test_requ_userscontext(self):
        self.picking.zetes_state = constants.AS_START

        # Check with no current picking
        domain = Usercontext(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update({"contextType": "1"})
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.unitSlam, "0")

        # Assign the picking to the current operator
        self.picking.operator_id = self.operator_user.id
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.unitSlam, "1")
        self.assertEqual(result.Usf01, str(self.picking.id))
