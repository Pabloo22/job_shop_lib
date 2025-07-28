import random
import logging
from typing import Optional, List

try:
    from simanneal import Annealer
except ImportError:
    raise ImportError(
        "simanneal library is required for SimulatedAnnealingSolver. "
        "Install with: pip install simanneal"
    )


class JobShopAnnealer:

    def __init__(self):
        pass
