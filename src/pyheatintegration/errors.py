class PyHeatIntegrationError(Exception):
    """ヒートインテグレーションに由来するエラー"""


class InvalidStreamError(PyHeatIntegrationError):
    """流体に関するエラー"""
