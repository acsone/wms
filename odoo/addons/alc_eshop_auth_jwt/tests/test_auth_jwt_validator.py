# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import contextlib
import time
from unittest.mock import Mock

from jose import jwt

import odoo.http
from odoo.tests.common import TransactionCase

from odoo.addons.auth_jwt.exceptions import UnauthorizedPartnerNotFound


class DotDict(dict):
    """Helper for dot.notation access to dictionary attributes.

    E.g.
      foo = DotDict({'bar': False})
      return foo.bar
    """

    def __getattr__(self, attrib):
        val = self.get(attrib)
        return DotDict(val) if isinstance(val, dict) else val


class TestAuthJwtValidator(TransactionCase):
    @contextlib.contextmanager
    def _mock_request(self, authorization):
        environ = {}
        if authorization:
            environ["HTTP_AUTHORIZATION"] = authorization
        request = Mock(
            context={},
            db=self.env.cr.dbname,
            uid=None,
            httprequest=Mock(environ=environ),
            session=DotDict(),
            env=self.env,
            cr=self.env.cr,
        )
        # These attributes are added upon successful auth, so make sure
        # calling hasattr on the mock when they are not yet set returns False.
        del request.jwt_payload
        del request.jwt_partner_id

        with contextlib.ExitStack() as s:
            odoo.http._request_stack.push(request)
            s.callback(odoo.http._request_stack.pop)
            yield request

    def _create_token(
        self,
        key="thesecret",
        audience="me",
        issuer="http://the.issuer",
        exp_delta=100,
        nbf=None,
        username=None,
    ):
        payload = {"aud": audience, "iss": issuer, "exp": time.time() + exp_delta}
        if username:
            payload["preferred_username"] = username
        if nbf:
            payload["nbf"] = nbf
        return jwt.encode(payload, key=key, algorithm="HS256")

    def _create_validator(self, name, audience="me", partner_id_required=False):
        return self.env["auth.jwt.validator"].create(
            {
                "name": name,
                "signature_type": "secret",
                "secret_algorithm": "HS256",
                "secret_key": "thesecret",
                "audience": audience,
                "issuer": "http://the.issuer",
                "user_id_strategy": "static",
                "partner_id_strategy": "keycloak_pref_user",
                "partner_id_required": partner_id_required,
            }
        )

    @contextlib.contextmanager
    def _validator_and_keycloak_user(
        self, name, audience="me", partner_id_required=False, username=None
    ):
        validator = self._create_validator(
            name=name,
            audience=audience,
            partner_id_required=partner_id_required,
        )
        jobs = self.env["queue.job"].search([])
        self.keycloak_backend = self.env.ref("connector_keycloak.keycloak_backend")
        partner_vals = {
            "email": "email@provider.com",
            "name": "Firstname Lastname",
        }
        self.partner = self.env["res.partner"].create(partner_vals)
        # normal flow would be to create the user through the wizard.
        # however we want to skip the creation on the backend
        self.vals_user = {
            "keycloak_id": "ecf8ea6d-c490",
            # would normally be given by the backend
            "keycloak_backend_id": self.keycloak_backend.id,
            "partner_id": self.partner.id,
            "username": username,
            "enabled": True,
        }
        self.keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        try:
            yield validator
        finally:
            validator.unlink()
            self.keycloak_user.unlink()
            self.partner.unlink()
            (self.env["queue.job"].search([]) - jobs).unlink()

    def test_partner_id_strategy_username_found(self):
        with self._validator_and_keycloak_user("validator6", username="username"):
            authorization = "Bearer " + self._create_token(
                username=self.keycloak_user.username
            )
            with self._mock_request(authorization=authorization) as request:
                self.env["ir.http"]._auth_method_jwt_validator6()
                self.assertEqual(request.jwt_partner_id, self.partner.id)

    def test_partner_id_strategy_username_not_found(self):
        with self._validator_and_keycloak_user("validator6", username="username"):
            authorization = "Bearer " + self._create_token(username="notfound")
            with self._mock_request(authorization=authorization) as request:
                self.env["ir.http"]._auth_method_jwt_validator6()
                self.assertFalse(request.jwt_partner_id)

    def test_partner_id_strategy_username_not_found_partner_required(self):
        with self._validator_and_keycloak_user(
            "validator6", partner_id_required=True, username="username"
        ):
            authorization = "Bearer " + self._create_token(username="notfound")
            with self._mock_request(authorization=authorization):
                with self.assertRaises(UnauthorizedPartnerNotFound):
                    self.env["ir.http"]._auth_method_jwt_validator6()
