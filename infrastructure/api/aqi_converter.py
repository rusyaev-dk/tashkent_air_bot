from typing import Optional


class AqiConverter:
    @staticmethod
    def convert_to_ppb(concentration: float, molar_mass: float) -> float:
        """
        Converts concentration from µg/m³ to ppb.

        :param concentration: Concentration in µg/m³.
        :param molar_mass: Molar mass of the gas in g/mol.
        :return: Concentration in ppb.
        """
        return concentration * 24.45 / molar_mass

    @classmethod
    def convert_to_usa_aqi(cls, pollutants: dict[str, float]) -> tuple[int, dict]:
        """
        Convert pollutants from µg/m³ to AQI based on USA EPA standards.

        :param pollutants: Dictionary with pollutant concentrations in µg/m³.
        :return: Overall AQI and individual AQI values for pollutants.
        """
        # Molar masses for gases
        molar_masses = {"co": 28.01, "so2": 64.07, "no2": 46.01, "o3": 48.00}
        aqi_values = {}
        for pollutant, concentration in pollutants.items():

            if pollutant in cls.__aqi_breakpoints:
                if pollutant in molar_masses:
                    if pollutant == "o3":
                        concentration = cls.convert_to_ppb(concentration, molar_masses[pollutant])

                aqi = cls.__calculate_individual_aqi(concentration, cls.__aqi_breakpoints[pollutant])
                if aqi is not None:
                    aqi_values[pollutant] = aqi

        overall_aqi = max(aqi_values.values(), default=0)
        return overall_aqi, aqi_values

    @staticmethod
    def __calculate_individual_aqi(concentration, breakpoints):
        """
        Calculate AQI for a specific pollutant using breakpoints.
        """
        for c_low, c_high, i_low, i_high in breakpoints:
            if c_low <= concentration <= c_high:
                return round((i_high - i_low) / (c_high - c_low) * (concentration - c_low) + i_low)
        return None

    @staticmethod
    def __calculate_concentration(aqi: int, breakpoints: list[tuple[float, float, int, int]]) -> Optional[float]:
        """
        Calculate pollutant concentration from AQI using breakpoints.

        :param aqi: AQI value to convert.
        :param breakpoints: List of breakpoints for the pollutant.
        :return: The calculated concentration in µg/m³ or None if AQI is out of range.
        """
        for c_low, c_high, i_low, i_high in breakpoints:
            if i_low <= aqi <= i_high:
                # Reverse linear interpolation
                return c_low + (aqi - i_low) * (c_high - c_low) / (i_high - i_low)
        return None

    @classmethod
    def get_pm25_concentration(cls, aqi: int) -> Optional[float]:
        """
        Calculate PM2.5 concentration (µg/m³) from AQI.

        :param aqi: AQI value for PM2.5.
        :return: Concentration in µg/m³.
        """
        return cls.__calculate_concentration(aqi, cls.__breakpoints_pm25)

    @classmethod
    def get_pm10_concentration(cls, aqi: int) -> Optional[float]:
        """
        Calculate PM10 concentration (µg/m³) from AQI.

        :param aqi: AQI value for PM10.
        :return: Concentration in µg/m³.
        """
        return cls.__calculate_concentration(aqi, cls.__breakpoints_pm10)

    @classmethod
    def get_o3_concentration(cls, aqi: int) -> Optional[float]:
        """
        Calculate O3 concentration (ppb, 8-hour average) from AQI.

        :param aqi: AQI value for O3.
        :return: Concentration in ppb.
        """
        return cls.__calculate_concentration(aqi, cls.__breakpoints_o3)

    __breakpoints_pm25 = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.0, 401, 500)
    ]

    __breakpoints_pm10 = [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 504, 301, 400),
        (505, 604, 401, 500)
    ]

    __breakpoints_o3 = [
        # 8-hour average
        (0, 54, 0, 50),
        (55, 70, 51, 100),
        (71, 85, 101, 150),
        (86, 105, 151, 200),
        (106, 200, 201, 300),
        (201, 300, 301, 400),
        (301, 500, 401, 500)
    ]

    __aqi_breakpoints = {
        "pm2_5": [(0, 12.0, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
                  (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300)],
        "pm10": [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150),
                 (255, 354, 151, 200), (355, 424, 201, 300)],
        "co": [(0, 4.4, 0, 50), (4.5, 9.4, 51, 100), (9.5, 12.4, 101, 150),
               (12.5, 15.4, 151, 200), (15.5, 30.4, 201, 300)],
        "so2": [(0, 35, 0, 50), (36, 75, 51, 100), (76, 185, 101, 150),
                (186, 304, 151, 200), (305, 604, 201, 300)],
        "no2": [(0, 53, 0, 50), (54, 100, 51, 100), (101, 360, 101, 150),
                (361, 649, 151, 200), (650, 1249, 201, 300)],
        "o3": [(0, 54, 0, 50), (55, 70, 51, 100), (71, 85, 101, 150),
               (86, 105, 151, 200), (106, 200, 201, 300)]
    }
