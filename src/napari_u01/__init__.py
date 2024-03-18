try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
from .classification_widget import LabelClassificationWidget
from .visability import LayerVisabilityWidget
from .data_loader import DataLoaderWidget

__all__ = (
    "LabelClassificationWidget",
    "LayerVisabilityWidget",
    "DataLoaderWidget"
)
