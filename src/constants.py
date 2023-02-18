from dataclasses import dataclass

from astropy import constants as const
from astropy import units as u
from astropy.units import Quantity


@dataclass(frozen=True)
class Characteristics_HgCdZnTe:
    E_g = 0.218 * u.electronvolt  # bandgap of semiconductor [eV]
