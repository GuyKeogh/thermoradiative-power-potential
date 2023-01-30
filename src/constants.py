from dataclasses import dataclass

from astropy import units as u
from astropy.units import Quantity
from astropy import constants as const

@dataclass(frozen=True)
class Constants:
    wavelength = 1863*10**(-9) * u.meter  # wavelength of infrared radiation
    frequency = const.c / wavelength
    q: Quantity = (const.h * frequency).to(u.joule)

    """
    q: float = (
        1.60217653 * 10 ** (-19) * u.coulomb
    )  # magnitude of electrical charge on electron [C]
    """

    T_deep_space: Quantity = 3 * u.Kelvin  # temperature of deep space [K]
    T_earth: Quantity = (
        300
        * u.Kelvin  # example temperature of the Earth [K]. In reality, T_surf ranges from 220K to 320K.
    )


@dataclass(frozen=True)
class Characteristics_HgCdZnTe:
    E_g = 0.218 * u.electronvolt  # bandgap of semiconductor [eV]
