from odoo.tests.common import TransactionCase


class TestDummy(TransactionCase):
    """A dummy test to remove once we've our first real tests written into a migrated addon. This test is required to make CI works with only one empty addon"""

    def test_true(self):
        self.assertTrue(True)
