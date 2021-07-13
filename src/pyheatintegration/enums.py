from enum import Enum


class StreamType(Enum):
    """流体の種類"""

    COLD = 1
    HOT = 2
    EXTERNAL_COLD = 3
    EXTERNAL_HOT = 4
    AUTO = 5

    def describe(self) -> str:
        return STREAMTYPE_STR[self.name]


STREAMTYPE_STR: dict[str, str] = {
    'COLD': 'cold',
    'HOT': 'hot',
    'EXTERNAL_COLD': 'external cold',
    'EXTERNAL_HOT': 'external hot',
    'AUTO': 'auto'
}


class StreamState(Enum):
    """流体の状態"""

    LIQUID = 1
    GAS = 2
    LIQUID_EVAPORATION = 3
    GAS_CONDENSATION = 4
    UNKNOWN = 5

    def describe(self) -> str:
        return STREAMSTATE_STR[self.name]


STREAMSTATE_STR = {
    'LIQUID': 'liquid',
    'GAS': 'gas',
    'LIQUID_EVAPORATION': 'liquid (evaporation)',
    'GAS_CONDENSATION': 'gas (condensation)',
    'UNKNOWN': 'unknown'
}
