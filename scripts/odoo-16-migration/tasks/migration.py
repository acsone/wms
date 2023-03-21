import glob
import importlib
import os
from collections import namedtuple

from odoo.tools import parse_version

CallableDef = namedtuple("CallableDef", "version,stage,callable,module,spec")


class MigrationScriptsManager:
    """Manage the migration scripts available for the given database."""

    def __init__(self, stage, version, path="migrations"):
        self.stage = stage
        self.version = version
        self.parsed_version = parse_version(version)
        self.path = path
        self.callable_defs = self._get_callable_defs()

    def _get_files(self):
        """Return the list of migration scripts for the given stage and version.

        The list is sorted by version number and includes all the scripts
        for the given stage and version equal or lower than the given version.
        """
        # The directory structure is:
        #   migrations/
        #       16.0.1.0.0/
        #           pre-
        #           post-
        #       16.0.1.0.1/
        #           pre-
        #           ...

        scripts_by_version = {
            version: glob.glob(os.path.join(self.path, version, f"{self.stage}*.py"))
            for version in sorted(os.listdir(self.path), key=parse_version)
            if parse_version(version) > self.parsed_version
        }
        return scripts_by_version

    def _get_callable_defs(self):
        """Return a dictionary of callables by name for the migration scripts."""
        callables = {}
        files = self._get_files()
        for version, scripts in files.items():
            scripts.sort()
            for script in scripts:
                name, ext = os.path.splitext(os.path.basename(script))
                if ext.lower() != ".py":
                    continue
                callables[f"{version}-{name}"] = self._get_callable_def(version, script)
        return callables

    def _get_callable_def(self, version, script):
        """Return a callable for the given script.

        The script is loaded and we return the migrate method of the module.
        """
        name = os.path.splitext(os.path.basename(script))[0]
        full_path = os.path.abspath(script)
        spec = importlib.util.spec_from_file_location(name, full_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return CallableDef(
            version=version,
            stage=self.stage,
            callable=module.migrate,
            module=module,
            spec=spec,
        )
