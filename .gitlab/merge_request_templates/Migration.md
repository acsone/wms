### Issues

- [ ] fixes #

### Tasks to do in the migration

- [ ] Bump module version to 16.0.1.0.0.
- [ ] Replace the usage of \_inherit and \_inherits with Python inheritance. Choose the
      superclass that includes the most essential attributes and methods required for
      your implementation.

      `class ResPartner(BaseResPartner):`

- [ ] use type annotations for x2x fields and methods.

      `partner_id = fields.Many2one[ResOartner]()`

- [ ] Remove any possible migration script from previous version (in a nutshell, remove
      migrations folder inside the module if exists).
- [ ] Add data migration script if needed.
- [ ] Add tests to increase code coverage.
- [ ] If there's a test class using setUp to generate test records, move it to
      setUpClass as it's way more performant since it runs only once.
- [ ] Replace SavepointCase by TransactionCase in tests.

/label ~"needs review" /assign me /assign_reviewer @laurent.mignon /milestone %1.95
/target_branch master
