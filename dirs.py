import os
from pathlib import Path


ROOT = Path(__file__).parent
DATA = ROOT / "data"
TEMP = DATA / "temp"


os.makedirs(DATA, exist_ok=True)
os.makedirs(TEMP, exist_ok=True)
