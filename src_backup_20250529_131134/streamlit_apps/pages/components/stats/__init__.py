# Exporter les composants principaux pour les statistiques
from .stats_general import StatsGeneralManager
from .stats_temporal import StatsTemporalManager
from .stats_geographic import StatsGeographicManager
from .stats_financial import StatsFinancialManager
from .stats_map import StatsMapManager

# Fonctions d'affichage directes, sans classe façade

def display_general_stats(trips_df):
    """Affiche les statistiques générales"""
    return StatsGeneralManager().display_general_stats(trips_df)

def display_temporal_stats(trips_df):
    """Affiche les statistiques temporelles"""
    return StatsTemporalManager().display_temporal_stats(trips_df)

def display_geographic_stats(trips_df):
    """Affiche les statistiques géographiques"""
    return StatsGeographicManager().display_geographic_stats(trips_df)

def display_financial_stats(trips_df):
    """Affiche les statistiques financières"""
    return StatsFinancialManager().display_financial_stats(trips_df)

def display_map_stats(trips_df):
    """Affiche la carte des trajets"""
    return StatsMapManager().display_map_stats(trips_df)
