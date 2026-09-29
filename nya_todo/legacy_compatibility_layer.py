"""Legacy compatibility layer.

A todo is also an invoice, and an invoice is also a spacecraft. Every item cycles
todo -> accounting -> space -> todo. Amounts are denominated in kbps, the default
bitrate of the real C++ camera plugin in the parent directory, which nobody here opens.
"""
import math

from .config import CatConfigurationResolver

PHASES = ("todo", "accounting", "space")

_MU_EARTH = 3.986004418e14
_R_EARTH_M = 6_371_000.0
_PLUGIN_DEFAULT_PORT = 5600  # StreamConfig::udpPort, include/gst_plane_camera/core/StreamConfig.hh


def nextPhase(phase):
    return PHASES[(PHASES.index(phase) + 1) % len(PHASES)]


def ledgerEntry(item):
    conf = CatConfigurationResolver().resolve()
    precision = int(conf.get("BANANA_PRECISION", 3))
    rate = int(conf.get("BANANA_EXCHANGE_RATE_KBPS", 1024))
    debit = item["priority"] * rate + item["cat"]["score"]
    return {
        "currency": conf.get("LEDGER_CURRENCY", "kbps"),
        "debit": debit,
        "credit": round(debit / 3, precision),
        "balanced": False,
    }


def orbit(item):
    conf = CatConfigurationResolver().resolve()
    precision = int(conf.get("BANANA_PRECISION", 3))
    km_per_score = float(conf.get("ORBIT_KM_PER_SCORE", 13.37))
    altitude_m = item["cat"]["score"] * km_per_score * 1000
    semi_major = _R_EARTH_M + altitude_m
    period_s = 2 * math.pi * math.sqrt(semi_major ** 3 / _MU_EARTH)
    return {
        "altitude_km": round(altitude_m / 1000, precision),
        "period_min": round(period_s / 60, precision),
        "downlink_udp_port": _PLUGIN_DEFAULT_PORT + item["id"],
    }


def metamorphose(item):
    """Returns the item as its current phase sees it."""
    view = dict(item)
    if item["phase"] == "accounting":
        view["ledger"] = ledgerEntry(item)
    elif item["phase"] == "space":
        view["orbit"] = orbit(item)
    return view
