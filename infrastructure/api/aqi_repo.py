from abc import ABC, abstractmethod


class AQIRepositoryI(ABC):
    """
    Interface for API repository.
    """

    @abstractmethod
    async def get_aqi(self):
        pass

    @abstractmethod
    async def update_aqi(self, lat: float = None, lon: float = None):
        pass
