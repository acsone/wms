# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import Command
from odoo.tests.common import TransactionCase


class TestURLLocalesCommon(TransactionCase):
    _url_res_model = None

    @classmethod
    def _create_index(cls, lang):
        raise NotImplementedError

    @classmethod
    def _setup_record_url(cls):
        cls.end_lang = cls.env.ref("base.lang_en")
        cls.fr_lang = cls.env.ref("base.lang_fr")
        cls.fr_lang.active = True
        cls.se_index_fr = cls._create_index(cls.fr_lang)
        cls.record._add_to_index(cls.se_index_fr)
        cls.record.write(
            {
                "url_ids": [
                    Command.create(
                        {
                            "key": "url_key_en",
                            "lang_id": cls.end_lang.id,
                            "res_model": cls._url_res_model,
                        }
                    ),
                    Command.create(
                        {
                            "key": "url_key_fr",
                            "lang_id": cls.fr_lang.id,
                            "res_model": cls._url_res_model,
                        }
                    ),
                ]
            }
        )
        cls.record._compute_binding_ids()
