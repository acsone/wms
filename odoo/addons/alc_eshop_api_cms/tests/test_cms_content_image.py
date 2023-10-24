# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from ..schemas import Content
from .common import CommonMixin


class TestCmsContentImage(TransactionCase, CommonMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        super()._init_langs()
        cls.ir_att_img_xml_id = "alc_eshop_cms.ir_att_img_team_bertrand"
        cls.ir_att_img = cls.env.ref(cls.ir_att_img_xml_id)
        cls.page = cls.env["alc.eshop.cms.page"].create(
            {
                "name": "Test page",
                "lang_ids": [(6, 0, cls.lang_fr.ids)],
                "cms_page_group_id": cls.env.ref(
                    "alc_eshop_cms.alc_eshop_cms_page_group_others"
                ).id,
                "cms_page_slot_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "alc_eshop_cms.alc_eshop_cms_page_slot_footer"
                            ).id
                        ],
                    )
                ],
                "content": cls._gen_content(
                    f"/web/image/{cls.ir_att_img.id}/test.jpg",
                    f"/web/image/{cls.ir_att_img_xml_id}/test.jpg",
                ),
            }
        )

    def setUp(self):
        super().setUp()
        self._init_fs_storage()
        self.fs_storage.model_ids |= self.env.ref(
            "fs_image_thumbnail.model_fs_thumbnail"
        )

    @classmethod
    def _gen_content(cls, *image_urls):
        return "<p>Test content</p>" + "".join(
            f'<img src="{url}" class="test class" width="100%"/>' for url in image_urls
        )

    def test_get_content_generate_storage_image(self):
        self.assertFalse(self.ir_att_img.thumbnail_ids)
        content = Content.from_odoo_record(self.page)
        self.assertTrue(content.data.content)
        self.assertEqual(len(self.ir_att_img.thumbnail_ids), 1)
        url = self.ir_att_img.thumbnail_ids.image.url
        self.assertEqual(content.data.content, self._gen_content(url, url))
        content = Content.from_odoo_record(self.page)
        self.assertEqual(len(self.ir_att_img.thumbnail_ids), 1)
        self.assertEqual(content.data.content, self._gen_content(url, url))
