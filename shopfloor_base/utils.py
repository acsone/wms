# -*- coding: utf-8 -*-
# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# @author Simone Orsi <simahawk@gmail.com>
import os
from functools import wraps

from odoo.modules.module import load_information_from_description_file


# pylint: disable=dangerous-default-value
def _get_app_version(module_name=None, module_path=None, APP_VERSIONS={}):  # noqa
    """Return module version straight from manifest."""
    # APP_VERSIONS is a memo to cache the result
    module_name = module_name or "shopfloor_base"
    if APP_VERSIONS.get(module_name):
        return APP_VERSIONS[module_name]
    try:
        if not module_path:
            tmp_path = os.path.dirname(os.path.realpath(__file__))
            module_path = os.path.split(tmp_path)[0]
        version = load_information_from_description_file(
            module_name, mod_path=module_path
        )["version"]
    except Exception:
        version = "dev"
    APP_VERSIONS[module_name] = version
    return APP_VERSIONS[module_name]


def ensure_model(model_name):
    """Decorator to ensure data method is called w/ the right recordset."""

    def _ensure_model(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            # 1st arg is `self`
            record = args[1]
            if record is not None:
                assert record._name == model_name, "Expected model: {}. Got: {}".format(
                    model_name, record._name
                )
            return func(*args, **kwargs)

        return wrapped

    return _ensure_model


class DotDict(dict):
    """Helper for dot.notation access to dictionary attributes

    E.g.
      foo = DotDict({'bar': False})
      return foo.bar
    """

    def __getattr__(self, attrib):
        val = self.get(attrib)
        return DotDict(val) if type(val) is dict else val
