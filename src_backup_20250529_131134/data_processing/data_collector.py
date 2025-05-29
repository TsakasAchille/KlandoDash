#!/usr/bin/env python3
# data_collector.py
# Ce fichier combine les fonctionnalités de data_scheduler.py et run_data_collector.py

import os
import time
import logging
import schedule
import argparse
import signal
import sys
from datetime import datetime
from pathlib import Path

from src.data_processing.data_manager import DataManager
from src.core.settings import ensure_dir, PROJECT_DIR, OUTPUT_DIRS

# Ensure logs directory exists
ensure_dir(PROJECT_DIR / "logs")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_DIR / "logs" / "data_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DataCollector")


class DataCollector:
    """    
    Classe unifiée qui gère la collecte et la planification des données.
    
    Cette classe permet de:
    1. Configurer une tâche de collecte quotidienne des données
    2. Exécuter la collecte immédiatement ou la planifier à une heure donnée
    3. Collecter l'ensemble des données ou un type spécifique
    """
    
    def __init__(self):
        """Initialise le collecteur avec le gestionnaire de données"""
        # S'assurer que tous les répertoires de sortie existent
        for output_dir in OUTPUT_DIRS.values():
            ensure_dir(output_dir)
            
        self.data_manager = DataManager()
        self.scheduler = schedule.Scheduler()
        
        # Configurer les gestionnaires de signaux pour arrêt propre
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        logger.info("DataCollector initialisé")
    
    def _handle_signal(self, signum, frame):
        """Gestionnaire de signaux pour arrêt propre"""
        logger.info(f"Signal {signum} reçu, arrêt du collecteur")
        sys.exit(0)
    
    def collect_all_data(self):
        """Collecte tous les types de données supportés"""
        logger.info(f"Début de la collecte de toutes les données - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            result = self.data_manager.process_all_data(collect=True)
            
            # Log des résultats
            for data_type, data_dict in result.items():
                if data_dict is not None:
                    # Traiter chaque DataFrame dans le dictionnaire
                    for df_name, df in data_dict.items():
                        if df is not None:
                            logger.info(f"Collecte réussie pour {df_name}: {len(df)} entrées")
                            
                            # Sauvegarder en CSV
                            try:
                                csv_path = self.data_manager.save_dataframe(df, df_name)
                                if csv_path:
                                    logger.info(f"Données {df_name} sauvegardées en CSV: {csv_path}")
                            except Exception as csv_error:
                                logger.error(f"Erreur lors de la sauvegarde CSV des données {df_name}: {csv_error}", exc_info=True)
                else:
                    logger.warning(f"Aucune donnée collectée pour {data_type}")
            
            logger.info(f"Collecte terminée avec succès - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des données: {e}", exc_info=True)
            return False
    
    def collect_specific_data(self, data_type):
        """

        Collecte un type spécifique de données
        
        Args:
            data_type (str): Type de données à collecter ('trips', 'users' ou 'chats')
            
        Returns:
            bool: True si la collecte a réussi, False sinon
        """
        logger.info(f"Début de la collecte de données {data_type} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            data = self.data_manager.process_data_type(data_type, collect=True)
            
            if data is not None:
                if isinstance(data, dict) and 'chats' in data and 'messages' in data:
                    logger.info(f"Collecte réussie pour {data_type}: {len(data['chats'])} chats, {len(data['messages'])} messages")
                    # Sauvegarder en CSV
                    try:
                        chats_path = self.data_manager.save_dataframe(data['chats'], 'chats')
                        messages_path = self.data_manager.save_dataframe(data['messages'], 'messages')
                        if chats_path and messages_path:
                            logger.info(f"Données de chats sauvegardées: {chats_path}, {messages_path}")
                    except Exception as csv_error:
                        logger.error(f"Erreur lors de la sauvegarde CSV des données {data_type}: {csv_error}", exc_info=True)
                else:
                    logger.info(f"Collecte réussie pour {data_type}: {len(data)} entrées")
                    # Sauvegarder en CSV
                    try:
                        csv_path = self.data_manager.save_dataframe(data, data_type)
                        if csv_path:
                            logger.info(f"Données {data_type} sauvegardées en CSV: {csv_path}")
                    except Exception as csv_error:
                        logger.error(f"Erreur lors de la sauvegarde CSV des données {data_type}: {csv_error}", exc_info=True)
                
                return True
            else:
                logger.warning(f"Aucune donnée collectée pour {data_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des données {data_type}: {e}", exc_info=True)
            return False
    
    def schedule_daily_collection(self, time_str="00:00"):
        """
        Programme une collecte quotidienne des données à l'heure spécifiée
        
        Args:
            time_str (str): Heure de collecte au format "HH:MM"
        """
        logger.info(f"Programmation de la collecte quotidienne à {time_str}")
        self.scheduler.every().day.at(time_str).do(self.collect_all_data)
        logger.info(f"Tâche de collecte programmée pour s'exécuter tous les jours à {time_str}")
    
    def run_schedule(self, with_initial_collection=True):
        """
        Exécute le scheduler et maintient le programme en cours d'exécution
        
        Args:
            with_initial_collection (bool): Si True, exécute une collecte immédiatement
        """
        logger.info("Démarrage du scheduler")
        
        try:
            # Exécuter immédiatement si demandé
            if with_initial_collection:
                logger.info("Exécution de la première collecte au démarrage")
                self.collect_all_data()
            
            # Boucle principale
            logger.info("Démarrage de la boucle de vérification des tâches programmées")
            while True:
                n = self.scheduler.idle_seconds()
                if n > 0:
                    # Afficher le temps restant avant la prochaine exécution uniquement si > 1 heure
                    if n > 3600:
                        hours = n // 3600
                        mins = (n % 3600) // 60
                        logger.info(f"Prochaine exécution dans {hours}h {mins}min")
                    time.sleep(min(n, 3600))  # Dormir jusqu'à la prochaine tâche ou max 1h
                self.scheduler.run_pending()

        except KeyboardInterrupt:
            logger.info("Arrêt du scheduler par l'utilisateur (Ctrl+C)")
        except Exception as e:
            logger.critical(f"Erreur inattendue dans la boucle principale du scheduler: {e}", exc_info=True)
            raise
        finally:
            logger.info("Arrêt du scheduler")


def run_data_collection(data_type=None, schedule_time=None, no_run=False):
    """
    Fonction principale pour exécuter la collecte de données
    
    Args:
        data_type (str, optional): Type de données à collecter ('all', 'trips', 'users', 'chats')
        schedule_time (str, optional): Heure de collecte programmée au format "HH:MM"
        no_run (bool, optional): Ne pas exécuter la collecte immédiatement
    """
    collector = DataCollector()
    
    # Mode de collecte unique
    if data_type:
        logger.info(f"Démarrage collecte de données - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if data_type == "all":
            result = collector.collect_all_data()
        else:
            result = collector.collect_specific_data(data_type)
            
        status = "réussie" if result else "échouée"
        logger.info(f"Collecte {status} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return result
    
    # Mode de programmation
    if schedule_time:
        # Programmer la collecte quotidienne
        collector.schedule_daily_collection(schedule_time)
        
        if no_run:
            # Programmer la collecte sans l'exécuter maintenant
            logger.info(f"Collecte programmée à {schedule_time} sans exécution immédiate")
            collector.run_schedule(with_initial_collection=False)
        else:
            # Exécuter immédiatement puis programmer
            logger.info(f"Exécution immédiate puis programmation à {schedule_time}")
            collector.run_schedule(with_initial_collection=True)
    else:
        # Exécuter immédiatement seulement
        logger.info("Exécution immédiate de la collecte")
        return collector.collect_all_data()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KlandoDash Data Collector")
    parser.add_argument("--type", "--collect", dest="data_type", 
                        choices=["all", "trips", "users", "chats"], 
                        help="Type de données à collecter")
    parser.add_argument("--schedule", "--time", dest="schedule_time", 
                        help="Programmer la collecte quotidienne (format HH:MM)")
    parser.add_argument("--no-run", action="store_true", 
                        help="Ne pas exécuter la collecte immédiatement (seulement avec --schedule)")
    
    args = parser.parse_args()
    
    run_data_collection(
        data_type=args.data_type,
        schedule_time=args.schedule_time,
        no_run=args.no_run
    )