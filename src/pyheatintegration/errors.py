class PyHeatIntegrationError(Exception):
    """ヒートインテグレーションに由来するエラー"""


class InvalidStreamError(PyHeatIntegrationError):
    """流体に関するエラー"""


class InvalidMinimumApproachTempDiffError(PyHeatIntegrationError):
    """Error related to minimum approach temperature difference."""
