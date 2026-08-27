from abc import ABC, abstractmethod
from typing import Any
from app.data_ingestion.schemas.normalized_event import NormalizedTelemetryEvent

class BaseNormalizer(ABC):
    """
    Abstract base class for all telemetry normalizers.
    """
    
    @abstractmethod
    def normalize(self, raw_event: dict[str, Any], **kwargs) -> NormalizedTelemetryEvent:
        """
        Convert a raw event dictionary into a NormalizedTelemetryEvent.
        """
        pass
