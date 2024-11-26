

class AqiConverter:
    @classmethod
    def convert_to_usa_aqi(cls, pollutants: dict[str, float]) -> tuple[int, dict]:
        aqi_values = {}
        for pollutant, concentration in pollutants.items():
            if pollutant in cls.__aqi_breakpoints:
                aqi = cls.__calculate_individual_aqi(concentration, cls.__aqi_breakpoints[pollutant])
                if aqi is not None:
                    aqi_values[pollutant] = aqi

        overall_aqi = max(aqi_values.values(), default=0)
        return overall_aqi, aqi_values

    @staticmethod
    def __calculate_individual_aqi(concentration, breakpoints):
        for bp in breakpoints:
            c_low, c_high, i_low, i_high = bp
            if c_low <= concentration <= c_high:
                return round((i_high - i_low) / (c_high - c_low) * (concentration - c_low) + i_low)
        return None

    # Таблицы диапазонов для каждого загрязнителя (по стандартам EPA)
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
