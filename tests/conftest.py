from typing import Callable, Hashable
from unittest.mock import MagicMock

import pytest

from matchescu.typing._references import EntityReference, EntityReferenceIdentifier


@pytest.fixture(scope="session")
def ref_id() -> Callable[[Hashable, str], EntityReferenceIdentifier]:
    return lambda lbl, src: EntityReferenceIdentifier(lbl, src)


@pytest.fixture(scope="session")
def ref(ref_id):
    def _(lbl, src):
        ref = MagicMock(spec=EntityReference)
        ref.id = EntityReferenceIdentifier(lbl, src)
        ref.__getitem__.return_value = {"name": f"{lbl}-{src}"}
        return ref

    return _
