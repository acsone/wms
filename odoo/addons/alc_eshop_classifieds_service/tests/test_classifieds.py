# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import json
import os

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
            # when
            result = service.dispatch("search", params={"from_date": value})
            # then
            self.assertEqual(result["size"], 4)

            # given
            value = fields.Date.to_string(self.date_tomorrow)
            # when
            result = service.dispatch("search", params={"from_date": value})
            # then
            self.assertEqual(result["size"], 0)

    def test_search_publication_date(self):
        with self.classifieds_service() as service:
            self.publish(self.classifieds)
            self.classified_1_employment.date_start = self.date_tomorrow
            self.classified_2_wbr.date_end = self.date_yesterday

            result = service.dispatch("search", params={})
            ids = {r["id"] for r in result["data"]}
            expected_ids = set((self.classified_1_misc | self.classified_2_misc).ids)
            self.assertEqual(ids, expected_ids)

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
        parameters = self._get_classified_vals()
        with self.classifieds_service() as service:
            params = {"file": None, "parameters": json.dumps(parameters)}
            result = service.dispatch("create_new", params=params)
            self.assertEqual(result["size"], 1)
            _id = result["data"][0]["id"]
            classified = service.model.browse(_id)
            self.assertEqual(result["data"][0]["name"], parameters["name"])
            self.assertEqual(result["data"][0]["name"], classified.name)
            self.assertEqual(result["data"][0]["state"], "draft")
            self.assertEqual(result["data"][0]["file"], None)

            service.dispatch("submit", _id)
            self.assertEqual(classified.state, "pending")

            parameters_update = {"name": "updated fancy name"}
            params_update = {"file": None, "parameters": json.dumps(parameters_update)}
            service.dispatch("update_set_to_draft", _id, params=params_update)
            self.assertEqual(classified.name, params_update["parameters"]["name"])
            self.assertEqual(classified.state, "draft")

            reason = "we don't like you"
            classified.reject(reason)

            result = service.dispatch("get", classified.id)
            self.assertEqual(result["data"][0]["rejection_reason"], reason)
            self.assertEqual(classified.state, "cancel")

            parameters_update = {"name": "corrected fancy name"}
            params_update = {"file": None, "parameters": json.dumps(parameters_update)}
            service.dispatch("update_set_to_pending", _id, params=params_update)
            self.assertEqual(classified.name, params_update["parameters"]["name"])
            self.assertEqual(classified.state, "pending")

            service.dispatch("delete", _id)
            self.assertFalse(classified.exists())

    def test_creation_without_file_parameter(self):
        """Check we can create a classified without passing a file."""
        parameters = self._get_classified_vals()
        with self.classifieds_service() as service:
            params = {"parameters": json.dumps(parameters)}
            result = service.dispatch("create_new", params=params)
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["file"], None)

    def test_file_flow(self):
        """Test binary flow."""
        filename = os.path.join(os.path.dirname(__file__), "handbook.pdf")
        parameters = self._get_classified_vals()
        with self.classifieds_service() as service:
            params = {
                "file": open(filename, "rb"),
                "parameters": json.dumps(parameters),
            }
            result = service.dispatch("create_new", params=params)
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["file"]["mimetype"], "application/pdf")
            self.assertEqual(result["data"][0]["file"]["name"], "fancy-name.pdf")

            _id = result["data"][0]["id"]
            classified = service.model.browse(_id)
            file_id_old = classified.file_id

            # replace the file with a new one
            params_update = {"file": open(filename, "rb"), "parameters": json.dumps({})}
            result = service.dispatch(
                "update_set_to_pending", _id, params=params_update
            )
            self.assertEqual(result["data"][0]["file"]["mimetype"], "application/pdf")
            self.assertTrue(file_id_old.to_delete)  # we removed the old file
            file_id_new = classified.file_id
            self.assertFalse(file_id_new.to_delete)  # and added a new one

            params_update = {"parameters": json.dumps({"file_delete": True})}
            result = service.dispatch(
                "update_set_to_pending", _id, params=params_update
            )
            self.assertEqual(result["data"][0]["file"], None)
            self.assertTrue(file_id_new.to_delete)  # we removed the file
