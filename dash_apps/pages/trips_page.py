import importlib.util
import sys
import os

# Chargement dynamique du layout depuis 02_trips.py
spec = importlib.util.spec_from_file_location(
    "trips_module",
    os.path.join(os.path.dirname(__file__), "02_trips.py")
)
trips_module = importlib.util.module_from_spec(spec)
sys.modules["trips_module"] = trips_module
spec.loader.exec_module(trips_module)
layout = trips_module.layout

# Les callbacks sont définis dans 02_trips.py pour l'instant
