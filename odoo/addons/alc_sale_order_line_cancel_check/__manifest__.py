# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Acl Sale Cancel Remaining Check",
    "description": """
        This addon prevent users from canceling remaining quantity of printed picking""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_sale_order_line_cancel_available_to_promise_release",
        # OCA
        "sale_order_line_cancel",
        # fmt: on
    ],
}
