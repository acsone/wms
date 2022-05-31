# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestClassifiedCase


class TestClassified(TestClassifiedCase):
    def test_alc_classified_count(self):
        (self.partner_1 | self.partner_2)._compute_alc_classified_count()
        self.assertEqual(self.partner_1.alc_classified_count, 2)
        self.assertEqual(self.partner_2.alc_classified_count, 2)

    def test_sale_order_flow(self):
        classified = self.classified_1_misc
        classified.submit()
        self.assertEqual(classified.state, "pending")
        # given
        rejection_reason = "lol"
        # when
        wizard_id = classified.action_reject()["res_id"]
        wizard = self.env["alc.classified.wizard.rejection"].browse(wizard_id)
        wizard.reason = rejection_reason
        wizard.execute()
        # then
        self.assertEqual(classified.state, "cancel")
        self.assertEqual(classified.rejection_reason, rejection_reason)
        # when
        vals = {"name": "new title"}
        classified.update_set_to_pending(vals)
        # then
        self.assertEqual(classified.state, "pending")
        self.assertEqual(classified.name, vals["name"])
        self.assertEqual(classified.rejection_reason, rejection_reason)
        # when
        classified.confirm()
        # then
        self.assertEqual(classified.state, "published")
        self.assertFalse(classified.rejection_reason)
