from unittest.mock import patch

from odoo.tests.common import TransactionCase

REFRESH_MATERIALIZED_VIEW_FUNC = (
    "odoo.addons.alce_account_move_line_search.models."
    "account_root.AccountRoot.refresh_materialized_view"
)


class TestAccountRootMaterializedViewRefresh(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Prepare a sample account data to work with
        cls.account_data = {
            "code": "TEST",
            "name": "Test Account",
            "company_id": cls.env.ref("base.main_company").id,
            "account_type": "liability_current",
        }

    @patch(REFRESH_MATERIALIZED_VIEW_FUNC)
    def test_refresh_on_create(self, mock_refresh_view):
        # Create an account and check if refresh_materialized_view is called
        self.env["account.account"].create([self.account_data])
        mock_refresh_view.assert_called_once()

    @patch(REFRESH_MATERIALIZED_VIEW_FUNC)
    def test_refresh_on_write(self, mock_refresh_view):
        # Create an account, update it, and check if refresh_materialized_view is called
        account = self.env["account.account"].create([self.account_data])
        account.write({"name": "Updated Test Account"})
        self.assertEqual(
            mock_refresh_view.call_count, 2
        )  # Called once on create, once on write

    @patch(REFRESH_MATERIALIZED_VIEW_FUNC)
    def test_refresh_on_unlink(self, mock_refresh_view):
        # Create an account, delete it, and check if refresh_materialized_view is called
        account = self.env["account.account"].create([self.account_data])
        account.unlink()
        self.assertEqual(
            mock_refresh_view.call_count, 2
        )  # Called once on create, once on unlink
