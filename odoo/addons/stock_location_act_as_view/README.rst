.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Stock location act as view
==========================

The 'view' usage on the locations does not work as we would like
to expect. For instance, it might create situations where we
have a positive quant in a location and no negative counterpart anywhere,
because odoo checks ``usage == internal`` in some parts of code.

Although, some addons in Alcyon need to know which locations "act" as views (we
cannot have stock in them, but they have children locations).

With this module, we'll still have the 'internal' usage on these views,
but a boolean field ``act_as_view`` will identify them as views-like.
