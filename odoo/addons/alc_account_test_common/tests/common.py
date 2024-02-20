# Copyright 2024 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests import tagged


@tagged("post_install")
class AlcCommonTestAccount:
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        if not chart_template_ref:
            # This line is ugly as we don't rely on l10n_be (and we shouldn't to
            # pull it on every submodule) but necessary as account module
            # does not load generic chart if another l10n_ is 'to install'
            chart_template_ref = "l10n_be.l10nbe_chart_template"
        super().setUpClass(chart_template_ref=chart_template_ref)
