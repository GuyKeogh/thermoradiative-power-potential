from src.calculators.total_power_output import TotalPowerOutput
from src.constants import Characteristics_HgCdZnTe


class TestTotalPowerOutput:
    def test_get_energy_dependent_emissivity_follows_assumptions(self):
        power_output_obj = TotalPowerOutput(E_g=Characteristics_HgCdZnTe.E_g)
        assert power_output_obj.get_energy_dependent_emissivity(E=0.1) == 0
        assert power_output_obj.get_energy_dependent_emissivity(E=0.3) == 1
