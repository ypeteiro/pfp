from abc import ABC, abstractmethod
class Importer(ABC):
    @abstractmethod
    def load(self,path):...
