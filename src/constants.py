from dataclasses import dataclass


@dataclass(frozen=True)
class Constants:
    k_B: float = 1.380649 * 10 ** (-23)  # Boltzmann constant [J*K^{-1}]
    c: float = 299792458  # speed of light [ms^{-1}]
    h: float = 6.6260693 * 10 ** (-34)  # Planck constant [J*s]
    q: float = 1.60217653 * 10 ** (
        -19
    )  # magnitude of electrical charge on electron [C]

    T_deep_space: int = 3  # temperature of deep space [K]
    T_earth: int = (
        300  # example temperature of the Earth [K]. In reality, T_surf ranges from 220K to 320K.
    )


@dataclass(frozen=True)
class Characteristics_HgCdZnTe:
    E_g = 0.218  # bandgap of semiconductor [eV]
