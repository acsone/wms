# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from fastapi import status
from requests import Response

from odoo import tools
from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tools import mute_logger

from odoo.addons.alc_b2c_connector.routers.sales import router as sales_router
from odoo.addons.alc_b2c_connector.tests.common import CommonB2CSaleServiceCase

from ..hooks import _initialize_product_assortment_filter

ISO_DT_WITH_TZ = "2020-05-28T13:45:47+02:00"


class TestSalesService(CommonB2CSaleServiceCase):
    @classmethod
    @mute_logger("odoo.addons.queue_job.utils")
    def setUpClass(cls):
        super().setUpClass()

        cls.default_fastapi_router = sales_router

        # TODO: we should not need that of course, see other TODO in module
        cls.carrier_alcyon = cls.env.ref(
            "__setup__.deliver_carrier_alcyon", raise_if_not_found=False
        )
        if not cls.carrier_alcyon:
            product = cls.env["product.product"].create(
                {"name": "Service Test", "type": "service"}
            )
            cls.carrier_alcyon = cls.env["delivery.carrier"].create(
                {"name": "Alcyon Shipping", "product_id": product.id}
            )
            cls.env["ir.model.data"].create(
                {
                    "module": "__setup__",
                    "name": "deliver_carrier_alcyon",
                    "model": "delivery.carrier",
                    "res_id": cls.carrier_alcyon.id,
                }
            )
        cls.logiweb_be_partner = cls.env.ref("alc_logiweb.logiweb_be_partner")
        cls.logiweb_be_partner.ref = "AUNIQUESTRING"
        cls.logiweb_partner = cls.env.ref("alc_logiweb.logiweb_partner")
        cls.logiweb_partner.ref = "ANOTHERUNIQUESTRING"
        cls.belgium = cls.env.ref("base.be")
        cls.partner_type = "student_like"
        cls.logiweb_b2c_client = cls.env.ref("alc_logiweb.alc_b2c_client_logiweb")
        cls.logiweb_channel = cls.env.ref("alc_logiweb.sale_channel_logiweb")

        _initialize_product_assortment_filter(cls.env.cr)

        categ_mat = cls.env.ref("alc_product_category_data.product_categ_materiel")
        categ_ali = cls.env.ref("alc_product_food.product_categ_ali")
        cls.saleable_product.categ_id = categ_ali
        cls.saleable_product_2.categ_id = categ_mat
        cls.vt_partner.country_id = cls.belgium

        # create a b2c sale_order
        cls.logiweb_b2c_order = cls.env["sale.order"].create(
            {
                "alc_b2c_client_id": cls.logiweb_b2c_client.id,
                "b2c_ref": 77,
                "partner_id": cls.logiweb_be_partner.id,
                "partner_invoice_id": cls.vt_partner.id,
                "partner_shipping_id": cls.vt_partner.id,
                "pricelist_id": cls.pricelist_id.id,
                "order_line": [
                    Command.create(
                        {
                            "b2c_ref": 77,
                            "product_id": cls.saleable_product.id,
                            "name": cls.saleable_product.name,
                            "product_uom": cls.saleable_product.uom_id.id,
                            "product_uom_qty": 10,
                        },
                    )
                ],
                "sale_channel_id": cls.logiweb_b2c_client.sale_channel_id.id,
            }
        )

    def _get_customer(self, recipient_info, sale_channel=None):
        return self.env["res.partner"].search(
            [("ref", "=", f"{sale_channel}_{recipient_info['id']}")]
        )

    def _get_base_params(self, **kwargs):
        # missing the carrier and recipient, need to be provided
        country = kwargs["recipient"].get("country_code")
        params = {
            "id": 2,
            "customer_ref": (
                self.logiweb_be_partner.ref
                if country == "BE"
                else self.logiweb_partner.ref
            ),
            "date": ISO_DT_WITH_TZ,
            "lines": [
                {
                    "line_id": 2,
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        params.update(kwargs)
        return params

    @classmethod
    def _gen_recipent(cls, _id=None, title="mr", country_code="BE"):
        recipient = super()._gen_recipent(_id=_id, title=title)
        recipient["country_code"] = country_code
        return recipient

    def test_01(self):
        """
        Data:

            An existing veterinary
            A b2c client with sale_channel = amazon
        Test case:
            Create a new SO for a new partner and the existing veterinary
            Specify the carrier GLS into the SO
        Expected result:
            The specified carrier is not taken into account in new SO created
            The partner_id  is the customer
            The partner_invoice_id is the VT
            The partner_shipping_id is the VT
        """
        b2c_client = self.b2c_client
        recipient_info = self._gen_recipent()
        params = self._get_base_params(recipient=recipient_info, carrier="GLS_BE")
        params["customer_ref"] = self.vt_partner.ref
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create", headers={"api-key": b2c_client.api_key}, json=params
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertTrue(new_so)
        self.assertNotEqual(
            new_so.carrier_id,
            self.env.ref("alc_delivery_carrier_gls.delivery_carrier_gls_be"),
        )
        customer_partner = self._get_customer(
            recipient_info, b2c_client.sale_channel_id.code
        )
        self.assertEqual(new_so.partner_id, customer_partner)
        self.assertEqual(new_so.partner_invoice_id, self.vt_partner)
        self.assertEqual(new_so.partner_shipping_id, self.vt_partner)

    @tools.mute_logger("odoo.addons.alc_delivery_carrier_gls.models.delivery_carrier")
    def test_02(self):
        """
        Data:

            An existing veterinary
            A b2c client with sale_channel = logiweb
        Test case:
            Create a new SO for a new partner and the existing veterinary
            Specify the carrier GLS into the SO
        Expected result:
            The specified carrier is taken into account in new SO created
            The partner_id  is the customer
            The partner_invoice_id is the Logiweb
            The partner_shipping_id is the customer
        """
        b2c_client = self.logiweb_b2c_client
        recipient_info = self._gen_recipent()
        carrier = "GLS_BE"
        gls_parcel_shop = "GGG"
        params = self._get_base_params(
            recipient=recipient_info,
            carrier=carrier,
            gls_parcel_shop=gls_parcel_shop,
        )
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create", headers={"api-key": b2c_client.api_key}, json=params
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertTrue(new_so)
        self.assertEqual(
            new_so.carrier_id,
            self.env.ref("alc_delivery_carrier_gls.delivery_carrier_gls_be"),
        )
        self.assertEqual(new_so.gls_parcel_shop, gls_parcel_shop)
        customer_partner = self._get_customer(
            recipient_info, b2c_client.sale_channel_id.code
        )
        self.assertEqual(new_so.partner_id, customer_partner)
        self.assertEqual(new_so.partner_invoice_id, self.logiweb_be_partner)
        self.assertEqual(new_so.partner_shipping_id, customer_partner)

        with self._create_test_client() as client:
            response: Response = client.get(
                f"/sales/{new_so.b2c_ref}", headers={"api-key": b2c_client.api_key}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertTrue(res)
        self.assertEqual(res["carrier"], carrier)
        self.assertEqual(res["gls_parcel_shop"], gls_parcel_shop)

    def test_missing_carrier(self):
        """
        Data:

            An existing veterinary
            A b2c client with sale_channel = logiweb
        Test case:
            Create a new SO for a new partner and the existing veterinary
            without specifying the carrier into the SO
        Expected result:
            Validation error
        """
        b2c_client = self.logiweb_b2c_client
        recipient_info = self._gen_recipent()
        params = self._get_base_params(recipient=recipient_info)
        with self.assertRaises(ValidationError):
            with self._create_test_client() as client:
                client.post(
                    "/sales/create",
                    headers={"api-key": b2c_client.api_key},
                    json=params,
                )

    def test_wrong_carrier(self):
        b2c_client = self.logiweb_b2c_client
        params = self._get_base_params(recipient=self._gen_recipent(), carrier="GLC")
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create", headers={"api-key": b2c_client.api_key}, json=params
            )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_parcelshop_not_gls(self):
        b2c_client = self.logiweb_b2c_client
        params = self._get_base_params(
            recipient=self._gen_recipent(),
            carrier="ALCYON",
            gls_parcel_shop="GGG",
        )
        with self.assertRaises(ValidationError):
            with self._create_test_client() as client:
                client.post(
                    "/sales/create",
                    headers={"api-key": b2c_client.api_key},
                    json=params,
                )

    def test_create_through_logiweb_notbe_partner_notbe_logiweb(self):
        b2c_client = self.logiweb_b2c_client
        recipient_info = self._gen_recipent(country_code="FR")
        params = self._get_base_params(recipient=recipient_info, carrier="GLS_BE")
        params["customer_ref"] = self.logiweb_partner.ref
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create", headers={"api-key": b2c_client.api_key}, json=params
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        customer_partner = self._get_customer(
            recipient_info, b2c_client.sale_channel_id.code
        )
        so = self._get_so_from_name(res["ref"])
        self.assertEqual(so.partner_invoice_id, self.logiweb_partner)
        self.assertEqual(so.partner_shipping_id, customer_partner)

    def test_create_through_logiweb_be_partner_notbe_logiweb(self):
        b2c_client = self.logiweb_b2c_client
        recipient_info = self._gen_recipent()
        params = self._get_base_params(recipient=recipient_info, carrier="GLS_BE")
        params["customer_ref"] = self.logiweb_partner.ref
        with self.assertRaises(ValidationError):
            with self._create_test_client() as client:
                client.post(
                    "/sales/create",
                    headers={"api-key": b2c_client.api_key},
                    json=params,
                )

    def test_create_through_logiweb_notbe_partner_be_logiweb(self):
        b2c_client = self.logiweb_b2c_client
        recipient_info = self._gen_recipent(country_code="FR")
        params = self._get_base_params(recipient=recipient_info, carrier="GLS_BE")
        params["customer_ref"] = self.logiweb_be_partner.ref
        with self.assertRaises(ValidationError):
            with self._create_test_client() as client:
                client.post(
                    "/sales/create",
                    headers={"api-key": b2c_client.api_key},
                    json=params,
                )

    def test_create_through_logiweb_carrier_alcyon(self):
        b2c_client = self.logiweb_b2c_client
        recipient_info = self._gen_recipent()
        params = self._get_base_params(recipient=recipient_info, carrier="ALCYON")
        params["customer_ref"] = self.logiweb_partner.ref
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create", headers={"api-key": b2c_client.api_key}, json=params
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        customer_partner = self._get_customer(
            recipient_info, b2c_client.sale_channel_id.code
        )
        so = self._get_so_from_name(res["ref"])
        self.assertTrue(so)
        self.assertEqual(so.carrier_id, self.carrier_alcyon)
        self.assertEqual(so.partner_id, customer_partner)
        self.assertEqual(so.partner_invoice_id, self.logiweb_partner)
        self.assertEqual(so.partner_shipping_id, self.logiweb_partner)

    def test_create_through_logiweb_be_carrier_alcyon(self):
        b2c_client = self.logiweb_b2c_client
        recipient_info = self._gen_recipent()
        params = self._get_base_params(recipient=recipient_info, carrier="ALCYON")
        with self.assertRaises(ValidationError):
            with self._create_test_client() as client:
                client.post(
                    "/sales/create",
                    headers={"api-key": b2c_client.api_key},
                    json=params,
                )

    def test_update_partner_shipping(self):
        """For GLS orders, the shipping partner is the final customer.

        So in that case, we also need to update the shipping partner.
        """
        b2c_client = self.logiweb_b2c_client
        params = self._get_base_params(
            recipient=self._gen_recipent(),
            carrier="GLS_BE",
        )
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": b2c_client.api_key},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        so = self.env["sale.order"].search(
            [("b2c_ref", "=", res["id"]), ("alc_b2c_client_id", "=", b2c_client.id)]
        )
        old_partner = so.partner_id
        # when: we update the customer
        recipient_info_new = self._gen_recipent()
        params = {"recipient": recipient_info_new}
        with self._create_test_client() as client:
            response: Response = client.post(
                f"/sales/{res['id']}/update",
                headers={"api-key": b2c_client.api_key},
                json=params,
            )
        # then: the new partner is indeed the new one
        new_partner = so.partner_id
        self.assertNotEqual(new_partner, old_partner)
        self.assertEqual(new_partner.zip, recipient_info_new["zip"])
        # then: the shipping partner was also transferred to the non canceled picking
        self.assertEqual(so.partner_shipping_id, new_partner)
        picking = so.picking_ids.filtered(lambda pick: pick.state != "cancel")
        self.assertEqual(picking.partner_id, new_partner)

    def test_no_update_partner_shipping_alcyon(self):
        """If the shipping partner is the VT, it follows that it should not be updated.

        when the the customer is updated.
        """
        b2c_client = self.logiweb_b2c_client
        params = self._get_base_params(recipient=self._gen_recipent(), carrier="ALCYON")
        params["customer_ref"] = self.logiweb_partner.ref
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create", headers={"api-key": b2c_client.api_key}, json=params
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        so = self.env["sale.order"].search([("b2c_ref", "=", res["id"])])
        old_shipping_partner = so.partner_shipping_id
        # when: we update the customer
        params = {"recipient": self._gen_recipent()}
        with self._create_test_client() as client:
            response: Response = client.post(
                f"/sales/{res['id']}/update",
                headers={"api-key": b2c_client.api_key},
                json=params,
            )
        # then: the shipping partner hasn't changed
        self.assertEqual(so.partner_shipping_id, old_shipping_partner)
