# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestUrlCase


class TestCategoryUrl(TestUrlCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        cls.lang_en = cls.env.ref("base.lang_en")
        cls.categ_1 = cls.env["product.category"].create({"name": "Root"})
        cls.categ_2 = cls.env["product.category"].create(
            {"name": "Level 1", "parent_id": cls.categ_1.id}
        )
        cls.categ_3 = cls.env["product.category"].create(
            {"name": "Level 2", "parent_id": cls.categ_2.id}
        )

    def test_00(self):
        """Main category."""
        self.categ_1._update_url_key(lang="en_US")
        self.assertUrlForLang(self.categ_1, "en_US", "c/root")

    def test_01(self):
        """Subcategory."""
        self.categ_3._update_url_key(lang="en_US")
        self.assertUrlForLang(self.categ_1, "en_US", "c/root")
        self.assertUrlForLang(self.categ_2, "en_US", "c/root/level-1")
        self.assertUrlForLang(self.categ_3, "en_US", "c/root/level-1/level-2")

    def test_02(self):
        """Update main."""
        self.categ_3._update_url_key(lang="en_US")
        self.categ_1.name = "New Root"
        self.categ_3._update_url_key(lang="en_US")
        self.assertUrlForLang(self.categ_1, "en_US", "c/new-root")
        self.assertUrlForLang(self.categ_2, "en_US", "c/new-root/level-1")
        self.assertUrlForLang(self.categ_3, "en_US", "c/new-root/level-1/level-2")

    def test_03(self):
        """Update child."""
        self.categ_3._update_url_key(lang="en_US")
        self.categ_2.name = "New Level 1"
        self.categ_3._update_url_key(lang="en_US")
        self.assertUrlForLang(self.categ_1, "en_US", "c/root")
        self.assertUrlForLang(self.categ_2, "en_US", "c/root/new-level-1")
        self.assertUrlForLang(self.categ_3, "en_US", "c/root/new-level-1/level-2")
