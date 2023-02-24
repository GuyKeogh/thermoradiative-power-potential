from dataclasses import dataclass

from astropy import units as u


@dataclass(frozen=True)
class Characteristics_HgCdZnTe:
    E_g = 0.218 * u.electronvolt  # bandgap of semiconductor [eV]
