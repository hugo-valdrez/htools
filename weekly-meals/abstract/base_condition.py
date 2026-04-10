from abc import ABC, abstractmethod

class BaseCondition(ABC):
    @abstractmethod
    def satisfies_condition(self, **kwargs) -> bool:
        pass