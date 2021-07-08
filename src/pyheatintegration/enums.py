from enum import Enum


class StreamType(Enum):
    """流体の種類"""

    COLD = 1
    HOT = 2
    EXTERNAL_COLD = 3
    EXTERNAL_HOT = 4

    def describe(self) -> str:
        return STREAMTYPE_STR[self.name]


STREAMTYPE_STR: dict[str, str] = {
    'COLD': 'cold',
    'HOT': 'hot',
    'EXTERNAL_COLD': 'external cold',
    'EXTERNAL_HOT': 'external hot',
}
