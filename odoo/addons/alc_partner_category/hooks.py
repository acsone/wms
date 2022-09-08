# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo

db_category_maping = [
    (34, u"A archiver", "toarchive"),
    (24, u"Alpha-R\xe9partition", "alpharepartition"),
    (36, u"Attest n\xb0d\xe9p\xf4t ok", "took"),
    (14, u"Autres", "autres"),
    (4, u"Clinique petits animaux", "clinique"),
    (15, u"Divers", "divers"),
    (9, u"Enseignant Universit\xe9", "enseignant"),
    (17, u"Ep\xe9c\xe9", "epece"),
    (3, u"Equins", "equins"),
    (2, u"Grands animaux", "grands_animaux"),
    (7, u"Inseminateur", "inseminateur"),
    (21, u"Lif\xe9", "life"),
    (22, u"Multipharma", "multipharma"),
    (5, u"NAC", "nac"),
    (35, u"N\xb0d\xe9p\xf4t en attente", "depotattente"),
    (10, u"Organisme sous resp. v\xe9to", "sous_veto"),
    (44, u"Palette delivery", "palette_delivery"),
    (16, u"Petit grossiste", "petit_grossiste"),
    (1, u"Petits animaux", "petits_animaux"),
    (19, u"Pharma Belge", "pharma_belge"),
    (18, u"Pharma Sant\xe9", "pharma_sante"),
    (43, u"TOP2000", "top_2000"),
    (37, u"TOP400", "top_400"),
    (42, u"TOP800", "top_800"),
    (29, u"TVA en attente", "tvaattente"),
    (11, u"Universit\xe9", "universite"),
    (25, u"V Pharma", "vpharma"),
    (33, u"actionnaire", "actionnaire"),
    (30, u"cl\xe9 dispo", "cledispo"),
    (8, u"comportementaliste", "comportementaliste"),
    (28, u"non-assujetti", "nonassujetti"),
    (45, u"QV", "qv"),
]


def pre_init_hook(cr):
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    vals_default = {"module": "alc_par  tner_category", "model": "res.partner.category"}
    for res_id, record_name, xmlid in db_category_maping:
        record = env["res.partner.category"].browse(res_id)
        if record.exists() and record.name == record_name:
            vals = dict(vals_default, res_id=res_id, name=xmlid)
            env["ir.model.data"].create(vals)
