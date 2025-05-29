from .trips_display import TripsDisplay
from .trips_table import TripsTableManager
from .trips_map import TripsMapManager
from .trips_route import TripsRouteManager
from .trips_finance import TripsFinanceManager
from .trips_metrics import TripsMetrics
from .trips_people import TripsPeople
from .trips_chat import TripsChat
from .trips_occupation import TripsOccupationManager
from src.data_processing.processors.trip_processor import TripProcessor

# Importer toutes les fonctions du nouveau module
from .trip_components import (
    get_trip_data,
    display_trips_table,
    display_map,
    display_multiple_map,
    display_route_info,
    display_financial_info,
    display_distance_info,
    display_fuel_info,
    display_CO2_info,
    display_all_metrics,
    display_time_metrics,
    display_seat_occupation_info,
    display_people_info,
    display_chat_popup
)

__all__ = [
    # Classes pour usage avancé si nécessaire
    "TripsDisplay",
    "TripsTableManager",
    "TripsMapManager",
    "TripsRouteManager",
    "TripsFinanceManager",
    "TripsMetrics",
    "TripsPeople",
    "TripsChat",
    "TripsOccupationManager",
    "TripProcessor",
    # Fonctions principales pour l'interface utilisateur
    "get_trip_data",
    "display_trips_table",
    "display_map",
    "display_multiple_map",
    "display_route_info",
    "display_financial_info",
    "display_distance_info",
    "display_fuel_info",
    "display_CO2_info",
    "display_all_metrics",
    "display_time_metrics",
    "display_seat_occupation_info",
    "display_people_info",
    "display_chat_popup"
]