from astropy import units as u

from src.calculators.maximum_power_point_tracker import MaximumPowerPointTracker


class TestMaximumPowerPointTracker:
    def test_get_max_power(self):
        """for a 270 K effective sky temperature ... At an operating temperature of 443 K ... InSb, with E_g = 0.17 ...
        could directly produce 40 W/m^2. (DOI: 10.1021/acsphotonics.9b00679)"""
        max_power = MaximumPowerPointTracker(
            t_cell=443 * u.Kelvin, t_sky=270 * u.Kelvin, E_g=0.17 * u.eV
        ).get_max_power()
        assert round(max_power.value, 1) == 40.8
        assert max_power.unit == (u.watt / (u.meter**2))
