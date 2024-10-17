# inspired by odoo.addons.website.tools.MockRequest
import contextlib
from unittest.mock import MagicMock, Mock, patch

from werkzeug.exceptions import NotFound
from werkzeug.test import EnvironBuilder

import odoo
from odoo.tests.common import HOST, HttpCase
from odoo.tools.misc import DotDict, frozendict


@contextlib.contextmanager
def MockRequest(
    env,
    *,
    path="/mockrequest",
    routing=True,
    multilang=True,
    context=None,
    cookies=None,
    remote_addr=HOST,
    environ_base=None,
    session_info: dict | None = None,
    json=None,
    params=None,
):
    context = context or frozendict()
    cookies = cookies or frozendict()
    session_info = session_info or {}
    session = odoo.http.get_default_session()
    session.update(session_info)
    lang_code = context.get("lang", env.context.get("lang", "en_US"))
    env = env(context=dict(context, lang=lang_code))
    request = Mock(
        # request
        httprequest=Mock(
            host="localhost",
            path=path,
            app=odoo.http.root,
            environ=dict(
                EnvironBuilder(
                    path=path,
                    base_url=HttpCase.base_url(),
                    environ_base=environ_base,
                ).get_environ(),
                REMOTE_ADDR=remote_addr,
            ),
            cookies=cookies,
            referrer="",
            remote_addr=remote_addr,
        ),
        type="http",
        future_response=odoo.http.FutureResponse(),
        redirect=env["ir.http"]._redirect,
        session=DotDict(session),
        params=params or {},
        geoip={},
        db=env.registry.db_name,
        env=env,
        registry=env.registry,
        cr=env.cr,
        uid=env.uid,
        context=env.context,
        lang=env["res.lang"]._lang_get(lang_code),
        render=lambda *a, **kw: "<MockResponse>",
        get_json_data=lambda: json or {},
    )
    # The following code mocks match() to return a fake rule with a fake
    # 'routing' attribute (routing=True) or to raise a NotFound
    # exception (routing=False).
    #
    #   router = odoo.http.root.get_db_router()
    #   rule, args = router.bind(...).match(path)
    #   # arg routing is True => rule.endpoint.routing == {...}
    #   # arg routing is False => NotFound exception
    router = MagicMock()
    match = router.return_value.bind.return_value.match
    if routing:
        match.return_value[0].routing = {
            "type": "http",
            "website": True,
            "multilang": multilang,
        }
    else:
        match.side_effect = NotFound

    def update_context(**overrides):
        request.context = dict(request.context, **overrides)

    request.update_context = update_context

    with contextlib.ExitStack() as s:
        odoo.http._request_stack.push(request)
        s.callback(odoo.http._request_stack.pop)
        s.enter_context(patch("odoo.http.root.get_db_router", router))

        yield request
