# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from odoo import api

from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas import (
    Content,
    ContentLang,
    ContentList,
    ContentSearchParams,
    ContentType,
)

cms_router = APIRouter(tags=["cms"])

_content_models = [
    "alc.eshop.cms.news",
    "alc.eshop.cms.snippet",
    "alc.eshop.cms.page",
]


@cms_router.get("/cms/content")
def get_content(
    env: Annotated[api.Environment, Depends(odoo_env)],
    params: Annotated[ContentSearchParams, Depends()] = None,
) -> ContentList:
    """Get all cms content."""
    models = _content_models
    if params.type:
        models = ["alc.eshop.cms." + params.type.value]
    lang_ids = None
    if params.lang:
        lang_ids = _get_lang_from_lang_prefix(env, params.lang.value)
    res = []
    for model_name in models:
        records = env[model_name].sudo()._get_contents_published()
        for record in records._iter_by_lang(lang_ids=lang_ids):
            res.append(Content.from_odoo_record(record))
    return ContentList(data=res, size=len(res))


@cms_router.get("/cms/content/{lang}/{content_type}/{url}")
def get_content_lang_content_type_url(
    env: Annotated[api.Environment, Depends(odoo_env)],
    lang: ContentLang,
    content_type: ContentType,
    url: str,
) -> Content:
    """Get specific cms content."""
    content_key = "/".join([lang.value, content_type.value, url])
    for model_name in _content_models:
        model = env[model_name].sudo()
        if model._content_type != content_type.value:
            continue
        record = model._get_from_url(url)
        if record:
            res_lang = _get_lang_from_lang_prefix(env, lang.value)
            record = record.with_context(lang=res_lang.code)
            return Content.from_odoo_record(record)
    raise HTTPException(status_code=404, detail=content_key)


def _get_lang_from_lang_prefix(env, lang_prefix):
    all_lang = env["res.lang"].get_installed()
    for lang in all_lang:
        lang_code = lang[0]
        if lang_code.startswith(lang_prefix):
            return env["res.lang"]._lang_get(lang_code)
    return None
