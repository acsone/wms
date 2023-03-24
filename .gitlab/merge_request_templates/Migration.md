### Issues

- [ ] fixes #

### Tasks to do in the migration

- [ ] Bump module version to 16.0.1.0.0.
- [ ] Remove any possible migration script from previous version (in a nutshell, remove
      migrations folder inside the module if exists).
- [ ] Add data migration script if needed.
- [ ] Add tests to increase code coverage.
- [ ] If there's a test class using setUp to generate test records, move it to
      setUpClass as it's way more performant since it runs only once.
- [ ] Replace SavepointCase by TransactionCase in tests.

/label ~"needs review" /assign me /assign_reviewer @laurent.mignon /milestone %2.1
/target_branch master
