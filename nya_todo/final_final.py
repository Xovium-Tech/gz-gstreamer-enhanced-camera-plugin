"""final_final: re-exports final_final_REAL, adding the non-REAL banana."""
from . import final_final_REAL as _real
from .final_final_REAL import bootstrap, catEngineName, userUser  # noqa: F401

bananaFinal2 = "banana-final-2"
bananaFinal2_REAL = _real.bananaFinal2_REAL


def getManager():
    # "maybe" because sometimes it is None and that is considered a feature
    return _real.finalFinalManager or bootstrap()
