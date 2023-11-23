# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import contextlib
import logging
from datetime import datetime, timedelta

import mock
from freezegun import freeze_time

from odoo import fields

from odoo.addons.shopinvader.tests.common import CommonCase


class MailRecorder(object):
    def __init__(self, env):
        self.env = env
        self.Mail = self.env["mail.mail"]
        self.created_mails = self.Mail

    @contextlib.contextmanager
    def record_created_mails(self):
        self.created_mails = self.Mail
        mails = self.Mail.search([])
        # disable mail sending to be sure that the email
        # is not auto deleted
        with mock.patch.object(mails.__class__, "send"):
            yield
        self.created_mails = self.Mail.search([]) - mails


class TestMailingGenerator(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestMailingGenerator, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.date_start = fields.Date.to_string(datetime.now() - timedelta(days=3))
        cls.date_end = fields.Date.to_string(datetime.now() + timedelta(days=3))
        cls.product_1 = cls.env.ref("product.product_product_4b")
        cls.supplierinfo1 = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "discount_sale": 10,
                "date_start": cls.date_start,
                "date_end": cls.date_end,
                "product_tmpl_id": cls.product_1.product_tmpl_id.id,
            }
        )
        cls.product_2 = cls.env.ref("product.product_product_13")
        cls.product_2.seller_ids.unlink()
        cls.supplierinfo2 = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "discount_sale": 10,
                "date_start": cls.date_start,
                "date_end": cls.date_end,
                "product_tmpl_id": cls.product_2.product_tmpl_id.id,
            }
        )
        cls.parther_1 = cls.env["res.partner"].create(
            {"name": "partner_1", "email": "partner1@test.com"}
        )
        cls.parther_2 = cls.env["res.partner"].create(
            {"name": "partner_2", "email": "partner2@test.com"}
        )
        cls.PromoSubscription = cls.env["alc.product.promotion.subscription"]
        cls.PromoGenerator = cls.env["product.promotion.mailing.generator"]
        cls.mail_recorder = MailRecorder(cls.env)

    def setUp(self):
        super(TestMailingGenerator, self).setUp()
        # mute logger
        loggers = ["odoo.addons.queue_job.models.base"]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        # pylint: disable=unused-variable
        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    def filter(self, record):
        # required to mute logger
        return 0

    def test_generator(self):
        self.PromoSubscription.subscribe(self.parther_1, self.product_1)
        with self.mail_recorder.record_created_mails():
            self.PromoGenerator._generate_promotion_mailing()
        new_mail = self.mail_recorder.created_mails
        self.assertEqual(1, len(new_mail))
        self.assertEqual(self.parther_1.email, new_mail.email_to)
        # at next run, nom mail is generated
        with self.mail_recorder.record_created_mails():
            self.PromoGenerator._generate_promotion_mailing()
        new_mail = self.mail_recorder.created_mails
        self.assertEqual(0, len(new_mail))

    def test_generator_multi_recipient(self):
        self.PromoSubscription.subscribe(self.parther_1, self.product_1)
        self.PromoSubscription.subscribe(self.parther_2, self.product_1)
        with self.mail_recorder.record_created_mails():
            self.PromoGenerator._generate_promotion_mailing()
        new_mail = self.mail_recorder.created_mails
        self.assertEqual(2, len(new_mail))

    def test_generator_multi_recipient_multi_product(self):
        self.PromoSubscription.subscribe(self.parther_1, self.product_1)
        self.PromoSubscription.subscribe(self.parther_1, self.product_2)
        self.PromoSubscription.subscribe(self.parther_2, self.product_1)
        self.PromoSubscription.subscribe(self.parther_2, self.product_2)
        with self.mail_recorder.record_created_mails():
            self.PromoGenerator._generate_promotion_mailing()
        new_mail = self.mail_recorder.created_mails
        self.assertEqual(2, len(new_mail))

    @freeze_time("2020-11-01 07:10:00")
    def test_no_mail_sent_future_promotion(self):
        self.PromoSubscription.subscribe(self.parther_1, self.product_1)
        with self.mail_recorder.record_created_mails():
            self.PromoGenerator._generate_promotion_mailing()
        new_mail = self.mail_recorder.created_mails
        self.assertEqual(0, len(new_mail))

    @freeze_time("2060-11-01 07:10:00")
    def test_no_mail_sent_past_promotion(self):
        self.PromoSubscription.subscribe(self.parther_1, self.product_1)
        with self.mail_recorder.record_created_mails():
            self.PromoGenerator._generate_promotion_mailing()
        new_mail = self.mail_recorder.created_mails
        self.assertEqual(0, len(new_mail))
