# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from slugify import slugify

from odoo.addons.alc_elasticsearch_security_vt_groups.models import veterinary_group


class VeterinaryGroup(veterinary_group.VeterinaryGroup):
    def _get_old_role_name(self):
        name = self.with_context(lang=False).name
        return slugify(f"vtgroup_{name}_{self.id}")
