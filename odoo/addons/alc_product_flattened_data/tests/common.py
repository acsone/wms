# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager
from unittest import mock

from odoo.tests import TransactionCase

from odoo.addons.alc_product_flattened_data.models.alc_product_flattened_data import (
    _ProductDataContainer,
)


class TestProductFlattenedData(TransactionCase):
    @classmethod
    @contextmanager
    def mock_product_data(cls, return_value=None):
        mock_path = (
            "odoo.addons.alc_product_flattened_data"
            ".models.alc_product_flattened_data"
            ".AlcProductFlattenedData._get_iterator"
        )
        if not return_value:
            record = cls._wrap_flattened_data(cls._example_product_flattened_data())
            return_value = (r for r in [record])  # make it an iterator
        with mock.patch(mock_path, return_value=return_value) as mocked:
            yield mocked, return_value

    @classmethod
    def _wrap_flattened_data(cls, vals, partner=None):
        return _ProductDataContainer(cls.env, partner or cls.partner, **vals)

    @classmethod
    def _example_product_flattened_data(cls):
        return {
            "id": 8248538,
            "allowed_partner_types": "food_only,student_like,equipment_only,guest,veterinary,misc,export_meds,wholesaler_veterinary,shareholder,supplier,export_customer,wholesaler_pharmacy",
            "barcode": False,
            "categ_en": "Medical Material / Pets / Dog / Baskets",
            "categ_fr": "Mat\xe9riel M\xe9dical / Animaux de compagnie / Chien / Corbeilles",
            "categ_nl": "Medisch materiaal / Huisdieren / Hond / Manden",
            "cnk_code": False,
            "code_amm": "False",
            "code_cti": False,
            "default_code": "8248538",
            "discount_special_date_end": False,
            "has_discount_special": False,
            "has_supplier_promotion": False,
            "indicated_price": 0.0,
            "manufacturer": "KRUUSE *",
            "name_de": "MATELAS FOAM DOGBED GRIS 120x100cm",
            "name_en": "MATELAS FOAM DOGBED GRIS 120x100cm",
            "name_fr": "MATELAS FOAM DOGBED GRIS 120x100cm",
            "name_nl": "KUSSEN FOAM DOGBED GRIJS 120x100cm",
            "price_cache": '{"price-prix-de-vente-brut-1": ['
            '{"date_end": null, "date_start": null, "id": null, "price": 94.09}]}',
            "supplier_discount_date_end": False,
            "supplier_discount_discount_sale": 0.0,
            "supplier_discount_only_for_veterinaries": False,
            "supplier_name": "KRUUSE *",
            "supplier_promotion_date_end": False,
            "supplier_promotion_only_for_veterinaries": False,
            "tax_amount": 21.0,
            "url_key_en": "p/matelas-foam-dogbed-gris-120x100cm-8248538",
            "url_key_fr": "p/matelas-foam-dogbed-gris-120x100cm-8248538",
            "url_key_nl": "p/kussen-foam-dogbed-grijs-120x100cm-8248538",
            "web_published": True,
        }
