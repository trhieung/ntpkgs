import logging
from abc import ABC, abstractmethod

class Helper(ABC):
    @staticmethod
    @abstractmethod
    def get_default() -> logging.Logger:
        pass