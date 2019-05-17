# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def load_translations(ctx, modules_list, overwrite=False):
    """Reload translations.

    :param modules_list: List of modules to reload (optional) default : all
    :param overwrite: Overwrite existing terms
    """
    # context: odoo base (and other modules) defines some default contents
    # like `res.partner.title`. These records HAVE translations
    # but they are not loaded until you load the translations
    # AFTER they are created.
    # I guess it has to do w/ the fact that translations in these cases
    # are linked via XID. Eg:
    # https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/i18n/fr.po#L16129
    # Basically the song `pre.load_res_lang` has no effect on translations
    # of records even if we add them before installing modules.
    lang = 'fr_BE'
    if not isinstance(modules_list, list):
        message = 'Bad arg `modules_list` provided to load_translations.'
        raise Exception(message)

    domain = [('name', 'in', modules_list)]
    msg = modules_list
    mods = ctx.env['ir.module.module'].search(domain)
    ctx.log_line('Reloading translations for %s' % str(msg))
    mods.with_context(overwrite=overwrite).update_translations(lang)
