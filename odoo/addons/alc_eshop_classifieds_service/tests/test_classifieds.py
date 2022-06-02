# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields

from .common import TestClassifiedsService


class TestDocumentsServiceFlow(TestClassifiedsService):
    def test_search_published(self):
        with self.classifieds_service() as service:
            result = service.dispatch("search", params={})
            self.assertEqual(result["size"], 0)

            self.publish(self.classifieds)
            result = service.dispatch("search", params={})
            self.assertEqual(result["size"], 4)

            params = {"country_state_code": "WBR"}
            result = service.dispatch("search", params=params)
            self.assertEqual(result["size"], 1)

            params = {"category": "employment"}
            result = service.dispatch("search", params=params)
            self.assertEqual(result["size"], 1)

            params = {"contact": "CONTAC"}
            result = service.dispatch("search", params=params)
            self.assertEqual(result["size"], 4)

            params = {"body": "body"}
            result = service.dispatch("search", params=params)
            self.assertEqual(result["size"], 4)

            params = {"phone": "phone"}
            result = service.dispatch("search", params=params)
            self.assertEqual(result["size"], 4)

            params = {"phone": "notaphonematch"}
            result = service.dispatch("search", params=params)
            self.assertEqual(result["size"], 0)

            # given
            value = self.classified_1_misc.date_start  # they all have the same date
            value = fields.Datetime.from_string(value)
            value = fields.Datetime.context_timestamp(self.classifieds_1, value)
            # when
            result = service.search(from_date=value)
            # then
            self.assertEqual(result["size"], 4)

            # given
            value += relativedelta(days=1)  # after all of them
            # when
            result = service.search(from_date=value)
            # then
            self.assertEqual(result["size"], 0)

    def test_output_shape(self):
        # private fields are only returned in private endpoints
        _id = self.classified_1_misc.id
        self.publish(self.classified_1_misc)
        with self.classifieds_service() as service:
            result = service.dispatch("get", _id)
            self.assertTrue("state" in result["data"][0])
            self.assertTrue("rejection_reason" in result["data"][0])

        with self.classifieds_service(self.partner_2) as service:
            result = service.dispatch("get", _id)
            self.assertFalse("state" in result["data"][0])
            self.assertFalse("rejection_reason" in result["data"][0])

    def test_search_state(self):
        # in public mode, state is simply ignored
        # in private mode, it works as expected
        with self.classifieds_service() as service:
            params = {"state": "draft"}
            result = service.dispatch("search", params=params)
            self.assertEqual(result["size"], 0)

            self.publish(self.classified_1_misc)

            result = service.dispatch("search", params=params)
            self.assertEqual(result["size"], 1)

            result = service.dispatch("search_my_classifieds", params=params)
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["id"], self.classified_1_employment.id)

            params = {"state": "published"}
            result = service.dispatch("search_my_classifieds", params=params)
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["id"], self.classified_1_misc.id)

    def test_search_private(self):
        with self.classifieds_service() as service:
            # when
            result = service.dispatch("search_my_classifieds", params={})
            # then
            self.assertEqual(result["size"], 2)
            ids = [r["id"] for r in result["data"]]
            self.assertEqual(service.model.browse(ids), self.classifieds_1)

        with self.classifieds_service(self.partner_2) as service:
            # when
            result = service.dispatch("search_my_classifieds", params={})
            # then
            self.assertEqual(result["size"], 2)
            ids = [r["id"] for r in result["data"]]
            self.assertEqual(service.model.browse(ids), self.classifieds_2)

    def test_get(self):
        _id = self.classified_1_misc.id
        with self.classifieds_service() as service:
            result = service.dispatch("get", _id)
            self.assertEqual(result["data"][0]["id"], _id)

        # get raises if the given id is not published
        with self.classifieds_service(self.partner_2) as service:
            with self.assertRaises(Exception):
                service.dispatch("get", _id)

            self.publish(self.classified_1_misc)
            # now partner_2 can publicly access it
            result = service.dispatch("get", _id)
            self.assertEqual(result["data"][0]["id"], _id)
            self.assertFalse("state" in result["data"][0])

    def test_creation_submission_flow(self):
        date_today = fields.Datetime.from_string(fields.Datetime.now())
        date_in_10_days = date_today + relativedelta(days=10)
        params = {
            "country_state_code": "WBR",
            "name": "fancy name",
            "body": "body",
            "category": "misc",
            "phone": "phone",
            "email": "email",
            "contact": "contact",
            "date_start": date_today,
            "date_end": date_in_10_days,
        }
        with self.classifieds_service() as service:
            result = service.dispatch("create_new", params=params)
            self.assertEqual(result["size"], 1)
            _id = result["data"][0]["id"]
            classified = service.model.browse(_id)
            self.assertEqual(result["data"][0]["name"], classified.name)
            self.assertEqual(result["data"][0]["state"], "draft")

            service.dispatch("submit", _id)
            self.assertEqual(classified.state, "pending")

            params_update = {"name": "updated fancy name"}
            service.dispatch("update_set_to_draft", _id, params=params_update)
            self.assertEqual(classified.name, params_update["name"])
            self.assertEqual(classified.state, "draft")

            reason = "we don't like you"
            classified.reject(reason)

            result = service.dispatch("get", classified.id)
            self.assertEqual(result["data"][0]["rejection_reason"], reason)
            self.assertEqual(classified.state, "cancel")

            params_update = {"name": "corrected fancy name"}
            service.dispatch("update_set_to_pending", _id, params=params_update)
            self.assertEqual(classified.name, params_update["name"])
            self.assertEqual(classified.state, "pending")

            service.dispatch("delete", _id)
            self.assertFalse(classified.exists())
