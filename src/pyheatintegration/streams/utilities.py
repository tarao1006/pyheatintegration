from .streams import Stream, StreamType, StreamState


# Some streams are provided as default on process design contest.
# See http://scejcontest.chem-eng.kyushu-u.ac.jp/2021/download/processsim2021_v2.pdf.

# Hot streams.
HPStream = Stream(254, 254, 0, StreamType.EXTERNAL_HOT, StreamState.GAS_CONDENSATION, id_="HPStream")
MPStream = Stream(186, 186, 0, StreamType.EXTERNAL_HOT, StreamState.GAS_CONDENSATION, id_="MPStream")
LPStream = Stream(160, 160, 0, StreamType.EXTERNAL_HOT, StreamState.GAS_CONDENSATION, id_="LPStream")

# Cold streams.
RefrigerantWater = Stream(30, 40, 0, StreamType.EXTERNAL_COLD, StreamState.LIQUID, id_="RefrigerantWater")
RefrigerantMinus33 = Stream(-33, -33, 0, StreamType.EXTERNAL_COLD, StreamState.LIQUID_EVAPORATION, id_="RefrigerantMinus33")
RefrigerantMinus18 = Stream(-18, -18, 0, StreamType.EXTERNAL_COLD, StreamState.LIQUID_EVAPORATION, id_="RefrigerantMinus18")
Refrigerant0 = Stream(0, 0, 0, StreamType.EXTERNAL_COLD, StreamState.LIQUID_EVAPORATION, id_="Refrigerant0")
Refrigerant18 = Stream(21, 21, 0, StreamType.EXTERNAL_COLD, StreamState.LIQUID_EVAPORATION, id_="Refrigerant18")
