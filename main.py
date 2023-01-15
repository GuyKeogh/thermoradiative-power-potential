from src.calculators.total_power_output import TotalPowerOutput
from src.constants import Characteristics_HgCdZnTe

if __name__ == "__main__":
    power_output_obj = TotalPowerOutput(E_g=Characteristics_HgCdZnTe.E_g)
    result = power_output_obj.get_photon_flux_emitted_from_semiconductor(
        T=300, voltage=-0.05
    )
    print(result)
