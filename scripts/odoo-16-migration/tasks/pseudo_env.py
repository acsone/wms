from contextlib import contextmanager

from .dbtools import cursor


class PseudoEnv:
    def __init__(self, cr):
        self.cr = cr


@contextmanager
def pseudo_env(dbname):
    with cursor(dbname) as cr:
        yield PseudoEnv(cr)
