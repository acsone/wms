# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from fastapi.testclient import TestClient

from odoo.tests.common import TransactionCase

from odoo.addons.fastapi.context import odoo_env_ctx

from ..hooks import _initialize_product_assortment_filter


class CommonCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _initialize_product_assortment_filter(cls.env.cr)
        cls.currency_id = cls.env.user.company_id.currency_id
        cls.pricelist_id = cls.env.ref(
            "alc_product_pricelist_data.product_pricelist_pb1"
        )
        # ensure same currency across products and pricelists
        cls.pricelist_id.currency_id = cls.currency_id
        cls.ProductProduct = cls.env["product.product"]
        # disable all products
        cls.ProductProduct.search([]).mapped("orderpoint_ids").write({"active": False})
        cls.ProductProduct.search([]).write({"active": False})
        cls.env.ref("alc_b2c_connector.alc_b2c_rest_api_user").email = "test@test.be"
        cls.env["stock.location"]._parent_store_compute()
        cls.env["product.category"]._parent_store_compute()

        # create specific taxes
        cls.tax_fixed = cls.env["account.tax"].create(
            {
                "sequence": 10,
                "name": "Tax 10.0 (Fixed)",
                "amount": 10.0,
                "amount_type": "fixed",
                "type_tax_use": "sale",
            }
        )
        cls.tax_6_percent = cls.env["account.tax"].create(
            {
                "name": "Tax 6%",
                "amount": 6.0000,
                "amount_type": "percent",
                "type_tax_use": "sale",
            }
        )
        # create products
        cls.saleable_product = cls.ProductProduct.create(
            {
                "name": "Product 1",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0001",
                "default_code": "12345",
                "cnk_code": "CNK123",
                "taxes_id": [(6, False, [cls.tax_6_percent.id])],
            }
        )
        cls.change_product_qty(cls.saleable_product, 5)
        cls.saleable_product_2 = cls.ProductProduct.create(
            {
                "name": "Product 2",
                "sale_ok": True,
                "type": "product",
                "list_price": 20,
                "barcode": "XXX0002",
                "default_code": "23456",
                "cnk_code": "CNK234",
                "taxes_id": [(6, False, [cls.tax_fixed.id])],
            }
        )
        cls.change_product_qty(cls.saleable_product_2, 110)
        cls.not_saleable_product = cls.ProductProduct.create(
            {
                "name": "Product 3",
                "sale_ok": False,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0003",
                "default_code": "34567",
            }
        )
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Inbound payment mode",
                "company_id": cls.env.ref("base.main_company").id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "payment_type": "inbound",
            }
        )
        cls.auth_api_key = cls.env["auth.api.key"].create(
            {"name": "test api key", "key": "1234", "user_id": cls.env.user.id}
        )
        cls.sale_channel = cls.env.ref("sale_channel.sale_channel_amazon")
        cls.endpoint = cls.env.ref("alc_b2c_connector.fastapi_endpoint_b2c")
        cls.endpoint_setting = cls.env["fastapi.endpoint.settings"].create(
            {
                "name": "B2c backend test",
                "product_assortment_id": cls.env.ref(
                    "alc_b2c_connector.b2c_product_assortment_filter"
                ).id,
                "pricelist_id": cls.pricelist_id.id,
                "sale_team_id": cls.env.ref("sales_team.salesteam_website_sales").id,
                "payment_mode_id": cls.payment_mode.id,
                "sale_channel_id": cls.sale_channel.id,
                "is_sale_back_order_accepted": False,
                "auth_api_key_id": cls.auth_api_key.id,
                "fastapi_endpoint_id": cls.endpoint.id,
            }
        )
        cls.app = cls.endpoint._get_app()
        cls.client = TestClient(cls.app)
        cls._ctx_token = odoo_env_ctx.set(cls.env)

    @classmethod
    def change_product_qty(cls, product, qty):
        cls.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": qty,
            }
        ).change_product_qty()

    @classmethod
    def tearDownClass(cls) -> None:
        odoo_env_ctx.reset(cls._ctx_token)
        cls.endpoint._reset_app()
        super().tearDownClass()

    def _get_path(self, path) -> str:
        return self.endpoint.root_path + path
