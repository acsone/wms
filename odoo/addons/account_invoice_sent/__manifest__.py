# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Invoice Sent",
    "version": "16.0.1.0.0",
    "author": "BCIM, ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": [
        "alc_account_test_common",
        "account_move_sent_usability",
        "account_invoice_transmit_method",
        "web_notify",
        "queue_job",
    ],
    "data": [
        "security/security.xml",
        "views/account_invoice_print_views.xml",
        "views/res_partner.xml",
        "wizards/account_invoice_sent_view.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_functions.xml",
    ],
    "installable": True,
}
