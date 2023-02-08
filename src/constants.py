from dataclasses import dataclass

from astropy import constants as const
from astropy import units as u
from astropy.units import Quantity


@dataclass(frozen=True)
class Constants:
    q = const.si.e
    T_deep_space: Quantity = 3 * u.Kelvin


@dataclass(frozen=True)
class Characteristics_HgCdZnTe:
    E_g = 0.218 * u.electronvolt  # bandgap of semiconductor [eV]
