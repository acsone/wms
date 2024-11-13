# Copyright 2024 ACSONE SA/NV

from odoo.tests.common import TransactionCase

from odoo.addons.alce_account_move_line_search.models.bank_rec_widget import _is_bbacomm


class TestBankRecWidget(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "partner"})
        cls.bank_journal = cls.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )

    def _create_st_line(self, payment_ref, partner=False):
        return self.env["account.bank.statement.line"].create(
            {
                "journal_id": self.bank_journal.id,
                "amount": 100,
                "date": "2024-01-01",
                "payment_ref": payment_ref,
                "partner_id": partner.id if partner else partner,
            }
        )

    def test_is_bbacomm(self):
        self.assertTrue(_is_bbacomm("+++000/0706/14582+++"))
        self.assertTrue(_is_bbacomm("+++000/0699/37808+++"))
        self.assertFalse(_is_bbacomm("FV/2025/01142"))

    def test_widget_context(self):
        # st line with partner and valid bba com
        st_line = self._create_st_line(
            payment_ref="+++000/0706/14582+++", partner=self.partner
        )
        wizard = self.env["bank.rec.widget"].new({"st_line_id": st_line.id})
        wizard._compute_amls_widget()
        context = wizard.amls_widget["context"]
        self.assertEqual(context.get("search_default_name"), "+++000/0706/14582+++")
        self.assertFalse(context.get("search_default_partner_id"))

        # st line with partner and invalid bba com
        st_line = self._create_st_line(
            payment_ref="FV/2025/01142", partner=self.partner
        )
        wizard = self.env["bank.rec.widget"].new({"st_line_id": st_line.id})
        wizard._compute_amls_widget()
        context = wizard.amls_widget["context"]
        self.assertIsNone(context.get("search_default_name"))
        self.assertEqual(context.get("search_default_partner_id"), self.partner.id)

        # st line without partner and invalid bba com
        st_line = self._create_st_line(payment_ref="FV/2025/01142")
        wizard = self.env["bank.rec.widget"].new({"st_line_id": st_line.id})
        wizard._compute_amls_widget()
        context = wizard.amls_widget["context"]
        self.assertIsNone(context.get("search_default_name"))
        self.assertIsNone(context.get("search_default_partner_id"))
