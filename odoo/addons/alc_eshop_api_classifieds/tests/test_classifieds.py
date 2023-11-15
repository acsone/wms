# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import os

from dateutil.relativedelta import relativedelta
from fastapi import status

from odoo import fields
from odoo.exceptions import AccessDenied

from odoo.addons.alc_eshop_classifieds.tests.common import TestClassifiedMixin
from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import classified_ads_router


class TestDocumentsServiceFlow(FastAPITransactionCase, TestClassifiedMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        super().setUpRecords()
        cls.date_today = fields.Date.from_string(fields.Date.today())
        cls.date_tomorrow = cls.date_today + relativedelta(days=1)
        cls.date_yesterday = cls.date_today - relativedelta(days=1)
        cls.date_in_10_days = cls.date_today + relativedelta(days=10)
        cls.default_fastapi_router = classified_ads_router
        cls.default_fastapi_authenticated_partner = cls.partner_1

    def _assert_search_count(self, params, expected_count):
        with self._create_test_client() as test_client:
            response = test_client.get("/classified_ads/search", params=params)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertEqual(result["size"], expected_count)
            return result

    def _publish(self, classifieds):
        classifieds.submit()
        classifieds.confirm()

    def _get_classified_vals(self, **kwargs):
        vals = {
            "country_state_code": "WBR",
            "name": "fancy name",
            "body": "body",
            "category": "misc",
            "phone": "phone",
            "email": "email",
            "contact": "contact",
            "date_start": fields.Date.to_string(self.date_today),
            "date_end": fields.Date.to_string(self.date_in_10_days),
        }
        return dict(vals, **kwargs)

    def test_search_published(self):
        self._assert_search_count({}, 0)

        self._publish(self.classifieds)
        self._assert_search_count({}, 4)

        params = {"country_state_code": "WBR"}
        self._assert_search_count(params, 1)

        params = {"category": "employment"}
        self._assert_search_count(params, 1)

        params = {"contact": "CONTAC"}
        self._assert_search_count(params, 4)

        params = {"body": "body"}
        self._assert_search_count(params, 4)

        params = {"phone": "phone"}
        self._assert_search_count(params, 4)

        params = {"phone": "notaphonematch"}
        self._assert_search_count(params, 0)

        # given
        value = fields.Date.to_string(
            self.classified_1_misc.date_start
        )  # they all have the same date
        # when
        params = {"from_date": value}
        # then
        self._assert_search_count(params, 4)

        # given
        value = fields.Date.to_string(self.date_tomorrow)
        # when
        params = {"from_date": value}
        # then
        self._assert_search_count(params, 0)

    def test_search_publication_date(self):
        self._publish(self.classifieds)
        self.classified_1_employment.date_start = self.date_tomorrow
        self.classified_2_wbr.date_end = self.date_yesterday
        result = self._assert_search_count({}, 2)
        ids = {r["id"] for r in result["data"]}
        expected_ids = set((self.classified_1_misc | self.classified_2_misc).ids)
        self.assertEqual(ids, expected_ids)

    def test_get_publication_date(self):
        """It is published in the future, so not accessible yet publicly."""
        self.classified_1_misc.date_start = self.date_tomorrow
        self._publish(self.classified_1_misc)
        with self._create_test_client(partner=self.partner_2) as test_client:
            with self.assertRaises(AccessDenied):
                test_client.get(f"/classified_ads/{self.classified_1_misc.id}")

    def test_output_shape(self):
        # private fields are only returned in private endpoints
        _id = self.classified_1_misc.id
        self._publish(self.classified_1_misc)
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(f"/classified_ads/{_id}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertTrue("state" in result["data"][0])
            self.assertTrue("rejection_reason" in result["data"][0])

        with self._create_test_client(partner=self.partner_2) as test_client:
            response = test_client.get(f"/classified_ads/{_id}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertFalse("state" in result["data"][0])
            self.assertFalse("rejection_reason" in result["data"][0])

    def test_search_state(self):
        # in public mode, state is simply ignored
        # in private mode, it works as expected

        params = {"state": "draft"}
        self._assert_search_count(params, 0)

        self._publish(self.classified_1_misc)
        self._assert_search_count(params, 1)

        with self._create_test_client(partner=self.partner_1) as test_client:
            self.assertEqual(self.classified_1_employment.state, "draft")
            self.assertEqual(self.classified_1_misc.state, "published")
            response = test_client.get(
                "/classified_ads/my_classified_ads", params=params
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["id"], self.classified_1_employment.id)

            params = {"state": "published"}
            response = test_client.get(
                "/classified_ads/my_classified_ads", params=params
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["id"], self.classified_1_misc.id)

    def test_search_private(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get("/classified_ads/my_classified_ads")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertEqual(result["size"], 2)
            ids = [r["id"] for r in result["data"]]
            self.assertEqual(self.env["alc.classified"].browse(ids), self.classifieds_1)

        with self._create_test_client(partner=self.partner_2) as test_client:
            response = test_client.get("/classified_ads/my_classified_ads")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertEqual(result["size"], 2)
            ids = [r["id"] for r in result["data"]]
            self.assertEqual(self.env["alc.classified"].browse(ids), self.classifieds_2)

    def test_get(self):
        _id = self.classified_1_misc.id
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(f"/classified_ads/{_id}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertEqual(result["data"][0]["id"], _id)

        # get raises if the given id is not published
        with self._create_test_client(partner=self.partner_2) as test_client:
            with self.assertRaises(AccessDenied):
                test_client.get(f"/classified_ads/{_id}")

            self._publish(self.classified_1_misc)
            # now partner_2 can publicly access it
            response = test_client.get(f"/classified_ads/{_id}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertEqual(result["data"][0]["id"], _id)
            self.assertFalse("state" in result["data"][0])

    def test_creation_submission_flow(self):
        parameters = self._get_classified_vals()
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                "/classified_ads", data={"parameters": json.dumps(parameters)}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            result = response.json()
            self.assertEqual(result["size"], 1)
            _id = result["data"][0]["id"]
            classified = self.env["alc.classified"].browse(_id)
            self.assertEqual(result["data"][0]["name"], parameters["name"])
            self.assertEqual(result["data"][0]["name"], classified.name)
            self.assertEqual(result["data"][0]["state"], "draft")
            self.assertEqual(result["data"][0]["file"], None)

            response = test_client.post(f"/classified_ads/{_id}/submit")
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
            self.assertEqual(classified.state, "pending")

            parameters_update = {"name": "updated fancy name"}
            params_update = {
                "parameters": json.dumps(parameters_update),
            }
            response = test_client.post(
                f"/classified_ads/{_id}/update_set_to_draft", data=params_update
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(classified.name, parameters_update["name"])
            self.assertEqual(classified.state, "draft")

            reason = "we don't like you"
            classified.reject(reason)

            response = test_client.get(f"/classified_ads/{_id}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertEqual(result["data"][0]["rejection_reason"], reason)
            self.assertEqual(classified.state, "cancel")

            parameters_update = {"name": "corrected fancy name"}
            params_update = {
                "parameters": json.dumps(parameters_update),
            }

            response = test_client.post(
                f"/classified_ads/{_id}/update_set_to_pending", data=params_update
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(classified.name, parameters_update["name"])
            self.assertEqual(classified.state, "pending")

            response = test_client.delete(f"/classified_ads/{_id}")
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertFalse(classified.exists())

    def test_creation_without_file_parameter(self):
        """Check we can create a classified without passing a file."""
        parameters = self._get_classified_vals()
        with self._create_test_client(partner=self.partner_1) as test_client:
            params = {"parameters": json.dumps(parameters)}
            response = test_client.post("/classified_ads", data=params)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            result = response.json()
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["file"], None)

    def test_file_flow(self):
        """Test binary flow."""
        filename = os.path.join(os.path.dirname(__file__), "handbook.pdf")
        parameters = self._get_classified_vals()
        with self._create_test_client(partner=self.partner_1) as test_client:
            data = {
                "parameters": json.dumps(parameters),
            }
            with open(filename, "rb") as f:
                files = {"file": ("handbook.pdf", f.read(), "application/pdf")}
            response = test_client.post("/classified_ads", data=data, files=files)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            result = response.json()
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["file"]["mimetype"], "application/pdf")
            self.assertEqual(result["data"][0]["file"]["name"], "fancy-name.pdf")

            _id = result["data"][0]["id"]
            classified = self.env["alc.classified"].browse(_id)

            # replace the file with a new one
            files = {
                "file": ("name", b"new_content"),
            }
            response = test_client.post(
                f"/classified_ads/{_id}/update_set_to_draft", files=files
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertEqual(result["data"][0]["file"]["mimetype"], "application/pdf")
            self.assertEqual(classified.file.getvalue(), b"new_content")
            # self.assertNotEqual(classified.file.attachment, attachment_old)  # we removed the old file

            data = {"parameters": json.dumps({"file_delete": True})}
            response = test_client.post(
                f"/classified_ads/{_id}/update_set_to_pending", data=data
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertEqual(result["data"][0]["file"], None)
            self.assertFalse(classified.file)  # we removed the file
