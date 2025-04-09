import sys

from freezegun.config import configure


def pytest_configure(config):
    print(
        ">>> [PLUGIN] Configuring freezegun to work next to the sentence_transformers package...",
        file=sys.stderr,
    )
    configure(extend_ignore_list=["transformers", "sentencepiece"])
