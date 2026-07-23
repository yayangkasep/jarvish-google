from abc import ABC, abstractmethod


class BaseConnector(ABC):
    def __init__(self):
        self.IsConnected = False
        self.PlatformType = "Base"

    @abstractmethod
    def Connect(self):
        pass

    @abstractmethod
    def ReceiveMessage(self, Payload):
        pass

    @abstractmethod
    def SendMessage(self, TargetId, MessageText):
        pass
