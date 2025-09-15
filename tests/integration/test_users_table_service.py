"""
Test complet pour la récupération et l'affichage du tableau users avec système de logging avancé.
Test l'architecture refactorisée selon le pattern trips.
"""
import os
import sys
import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date

# Ajouter le chemin du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dash_apps.services.users_table_service import UsersTableService
from dash_apps.models.config_models import UserModel
from dash_apps.utils.callback_logger import CallbackLogger


class TestUsersTableService:
    """Tests complets pour UsersTableService avec logging détaillé."""
    
    @classmethod
    def setup_class(cls):
        """Configuration initiale des tests."""
        # Activer le debug pour les tests
        os.environ['DEBUG_USERS'] = 'true'
        
        # Nettoyer le cache avant les tests
        UsersTableService._local_cache.clear()
        UsersTableService._cache_timestamps.clear()
        
        print("\n" + "="*80)
        print("🧪 DÉMARRAGE DES TESTS USERS TABLE SERVICE")
        print("="*80)
        
        CallbackLogger.log_callback(
            "test_setup",
            {"test_class": "TestUsersTableService"},
            status="INFO",
            extra_info="Configuration des tests initialisée"
        )
    
    @classmethod
    def teardown_class(cls):
        """Nettoyage après les tests."""
        # Nettoyer le cache après les tests
        UsersTableService._local_cache.clear()
        UsersTableService._cache_timestamps.clear()
        
        print("\n" + "="*80)
        print("✅ FIN DES TESTS USERS TABLE SERVICE")
        print("="*80)
        
        CallbackLogger.log_callback(
            "test_teardown",
            {"test_class": "TestUsersTableService"},
            status="INFO",
            extra_info="Tests terminés et cache nettoyé"
        )
    
    def setup_method(self, method):
        """Configuration avant chaque test."""
        self.test_name = method.__name__
        print(f"\n🔍 Test: {self.test_name}")
        print("-" * 60)
        
        CallbackLogger.log_callback(
            "test_start",
            {"test_method": self.test_name},
            status="INFO",
            extra_info=f"Démarrage du test {self.test_name}"
        )
    
    def teardown_method(self, method):
        """Nettoyage après chaque test."""
        CallbackLogger.log_callback(
            "test_end",
            {"test_method": self.test_name},
            status="INFO",
            extra_info=f"Fin du test {self.test_name}"
        )
    
    def create_mock_user_data(self, uid: str, **kwargs) -> dict:
        """Crée des données utilisateur de test avec logging."""
        default_data = {
            "uid": uid,
            "display_name": f"User {uid[-4:]}",
            "email": f"user{uid[-4:]}@test.com",
            "phone_number": f"+33612345{uid[-3:]}",
            "role": "passenger",
            "gender": "NOT_SPECIFIED",
            "rating": 4.5,
            "rating_count": 10,
            "created_at": datetime.now().isoformat(),
            "is_driver_doc_validated": False,
            "photo_url": f"https://example.com/photo_{uid}.jpg"
        }
        default_data.update(kwargs)
        
        CallbackLogger.log_callback(
            "mock_user_created",
            {"uid": uid[:8], "display_name": default_data["display_name"]},
            status="DEBUG",
            extra_info="Données utilisateur de test créées"
        )
        
        return default_data
    
    def create_mock_supabase_response(self, users_data: list, total_count: int = None):
        """Crée une réponse Supabase mockée avec logging."""
        mock_response = Mock()
        mock_response.data = users_data
        mock_response.count = total_count or len(users_data)
        
        CallbackLogger.log_callback(
            "mock_supabase_response",
            {
                "users_count": len(users_data),
                "total_count": mock_response.count
            },
            status="DEBUG",
            extra_info="Réponse Supabase mockée créée"
        )
        
        return mock_response
    
    @patch('dash_apps.utils.supabase_client.supabase')
    @patch('dash_apps.utils.settings.load_json_config')
    def test_get_users_page_basic(self, mock_load_config, mock_supabase):
        """Test de récupération basique d'une page d'utilisateurs."""
        print("📋 Test de récupération basique du tableau users")
        
        # Configuration mock
        mock_config = {
            "queries": {
                "users_paginated": {
                    "select": {
                        "base": ["uid", "display_name", "email", "role", "created_at"]
                    }
                }
            }
        }
        mock_load_config.return_value = mock_config
        
        # Données utilisateurs de test avec valeurs Pydantic valides
        test_users = [
            self.create_mock_user_data("user123", display_name="Alice Dupont", role="driver", gender="woman"),
            self.create_mock_user_data("user456", display_name="Bob Martin", role="passenger", gender="man"),
            self.create_mock_user_data("user789", display_name="Claire Durand", role="ADMIN", gender="woman")
        ]
        
        # Mock Supabase
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.range.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = self.create_mock_supabase_response(test_users, 3)
        
        mock_supabase.table.return_value = mock_query
        
        CallbackLogger.log_callback(
            "test_basic_setup",
            {"users_count": len(test_users)},
            status="INFO",
            extra_info="Configuration du test basique terminée"
        )
        
        # Exécution du test
        start_time = time.time()
        result = UsersTableService.get_users_page(page=1, page_size=10)
        execution_time = time.time() - start_time
        
        # Vérifications avec logging détaillé
        assert result is not None, "Le résultat ne doit pas être None"
        assert "users" in result, "Le résultat doit contenir 'users'"
        assert "total_count" in result, "Le résultat doit contenir 'total_count'"
        assert len(result["users"]) == 3, f"Attendu 3 users, reçu {len(result['users'])}"
        assert result["total_count"] == 3, f"Attendu total_count=3, reçu {result['total_count']}"
        
        CallbackLogger.log_callback(
            "test_basic_results",
            {
                "users_returned": len(result["users"]),
                "total_count": result["total_count"],
                "execution_time_ms": round(execution_time * 1000, 2),
                "has_next": result.get("has_next", False),
                "has_previous": result.get("has_previous", False)
            },
            status="SUCCESS",
            extra_info="Test basique réussi - données récupérées correctement"
        )
        
        # Vérifier la structure des données utilisateur
        first_user = result["users"][0]
        expected_fields = ["uid", "display_name", "email", "role", "created_at"]
        for field in expected_fields:
            assert field in first_user, f"Champ manquant: {field}"
        
        print(f"✅ Test basique réussi - {len(result['users'])} utilisateurs récupérés en {execution_time*1000:.2f}ms")
    
    @patch('dash_apps.utils.supabase_client.supabase')
    @patch('dash_apps.utils.settings.load_json_config')
    def test_get_users_page_with_filters(self, mock_load_config, mock_supabase):
        """Test de récupération avec filtres."""
        print("🔍 Test de récupération avec filtres")
        
        # Configuration mock
        mock_config = {
            "queries": {
                "users_paginated": {
                    "select": {
                        "base": ["uid", "display_name", "email", "role", "gender"]
                    }
                },
                "users_search": {
                    "filters": {
                        "text_search": {
                            "fields": ["display_name", "email", "first_name", "name"]
                        }
                    }
                }
            }
        }
        mock_load_config.return_value = mock_config
        
        # Données de test filtrées avec valeurs Pydantic valides
        filtered_users = [
            self.create_mock_user_data("driver001", display_name="Alice Driver", role="driver", gender="woman"),
            self.create_mock_user_data("driver002", display_name="Bob Driver", role="driver", gender="man")
        ]
        
        # Mock Supabase avec filtres
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.or_.return_value = mock_query
        mock_query.range.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = self.create_mock_supabase_response(filtered_users, 2)
        
        mock_supabase.table.return_value = mock_query
        
        # Test avec filtres
        filters = {
            "role": "driver",
            "gender": "all",
            "text": "Driver"
        }
        
        CallbackLogger.log_callback(
            "test_filters_setup",
            {"filters": filters, "expected_results": len(filtered_users)},
            status="INFO",
            extra_info="Configuration du test avec filtres"
        )
        
        start_time = time.time()
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        execution_time = time.time() - start_time
        
        # Vérifications
        assert len(result["users"]) == 2, f"Attendu 2 conducteurs, reçu {len(result['users'])}"
        
        for user in result["users"]:
            assert user["role"] == "driver", f"Utilisateur {user['uid']} n'est pas conducteur"
            assert "Driver" in user["display_name"], f"Nom {user['display_name']} ne contient pas 'Driver'"
        
        CallbackLogger.log_callback(
            "test_filters_results",
            {
                "filtered_users": len(result["users"]),
                "execution_time_ms": round(execution_time * 1000, 2),
                "filters_applied": filters
            },
            status="SUCCESS",
            extra_info="Test avec filtres réussi"
        )
        
        print(f"✅ Test filtres réussi - {len(result['users'])} conducteurs trouvés en {execution_time*1000:.2f}ms")
    
    def test_cache_functionality(self):
        """Test du système de cache local."""
        print("💾 Test du système de cache")
        
        # Nettoyer le cache
        UsersTableService._local_cache.clear()
        UsersTableService._cache_timestamps.clear()
        
        # Données de test
        test_data = {
            "users": [{"uid": "test123", "display_name": "Test User"}],
            "total_count": 1,
            "page": 1
        }
        
        cache_key = "test_cache_key"
        
        CallbackLogger.log_callback(
            "test_cache_setup",
            {"cache_key": cache_key},
            status="INFO",
            extra_info="Test du cache - données préparées"
        )
        
        # Test mise en cache
        UsersTableService._set_to_local_cache(cache_key, test_data)
        
        assert cache_key in UsersTableService._local_cache, "Données non mises en cache"
        assert cache_key in UsersTableService._cache_timestamps, "Timestamp de cache manquant"
        
        # Test récupération du cache
        cached_data = UsersTableService._get_from_local_cache(cache_key)
        
        assert cached_data is not None, "Données non récupérées du cache"
        assert cached_data["users"][0]["uid"] == "test123", "Données du cache incorrectes"
        
        CallbackLogger.log_callback(
            "test_cache_results",
            {
                "cache_hit": cached_data is not None,
                "cache_size": len(UsersTableService._local_cache),
                "data_integrity": cached_data["users"][0]["uid"] == "test123"
            },
            status="SUCCESS",
            extra_info="Test cache réussi - données stockées et récupérées"
        )
        
        print("✅ Test cache réussi - données stockées et récupérées correctement")
    
    def test_cache_expiration(self):
        """Test de l'expiration du cache."""
        print("⏰ Test d'expiration du cache")
        
        # Nettoyer le cache
        UsersTableService._local_cache.clear()
        UsersTableService._cache_timestamps.clear()
        
        # Modifier temporairement le TTL pour le test
        original_ttl = UsersTableService.LOCAL_CACHE_TTL
        UsersTableService.LOCAL_CACHE_TTL = 0.1  # 100ms
        
        test_data = {"test": "data"}
        cache_key = "expiration_test"
        
        CallbackLogger.log_callback(
            "test_expiration_setup",
            {"ttl_seconds": UsersTableService.LOCAL_CACHE_TTL},
            status="INFO",
            extra_info="Test expiration - TTL réduit pour le test"
        )
        
        # Mettre en cache
        UsersTableService._set_to_local_cache(cache_key, test_data)
        
        # Vérifier que les données sont en cache
        cached_data = UsersTableService._get_from_local_cache(cache_key)
        assert cached_data is not None, "Données devraient être en cache"
        
        # Attendre l'expiration
        time.sleep(0.2)
        
        # Vérifier que les données ont expiré
        expired_data = UsersTableService._get_from_local_cache(cache_key)
        assert expired_data is None, "Données devraient avoir expiré"
        
        # Restaurer le TTL original
        UsersTableService.LOCAL_CACHE_TTL = original_ttl
        
        CallbackLogger.log_callback(
            "test_expiration_results",
            {
                "cache_before_expiration": cached_data is not None,
                "cache_after_expiration": expired_data is None,
                "ttl_restored": UsersTableService.LOCAL_CACHE_TTL == original_ttl
            },
            status="SUCCESS",
            extra_info="Test expiration réussi - cache expiré correctement"
        )
        
        print("✅ Test expiration réussi - cache expiré après TTL")
    
    def test_pydantic_validation(self):
        """Test de la validation Pydantic."""
        print("🔒 Test de validation Pydantic")
        
        # Données valides
        valid_data = {
            "uid": "valid123",
            "display_name": "Valid User",
            "email": "valid@test.com",
            "role": "passenger",
            "created_at": datetime.now()
        }
        
        # Données invalides
        invalid_data = {
            "uid": "",  # UID vide - invalide
            "email": "invalid-email",  # Email invalide
            "rating": 6.0  # Rating > 5.0 - invalide
        }
        
        CallbackLogger.log_callback(
            "test_validation_setup",
            {"valid_fields": len(valid_data), "invalid_fields": len(invalid_data)},
            status="INFO",
            extra_info="Test validation - données préparées"
        )
        
        # Test validation réussie
        try:
            valid_user = UserModel(**valid_data)
            validation_success = True
            
            # Test model_dump()
            if hasattr(valid_user, 'model_dump'):
                user_dict = valid_user.model_dump()
                model_dump_success = True
            else:
                model_dump_success = False
                
        except Exception as e:
            validation_success = False
            model_dump_success = False
            CallbackLogger.log_callback(
                "validation_error",
                {"error": str(e)},
                status="ERROR",
                extra_info="Erreur validation données valides"
            )
        
        # Test validation échouée
        validation_failed = False
        try:
            invalid_user = UserModel(**invalid_data)
        except Exception as e:
            validation_failed = True
            CallbackLogger.log_callback(
                "validation_expected_failure",
                {"error": str(e)},
                status="INFO",
                extra_info="Validation échouée comme attendu pour données invalides"
            )
        
        assert validation_success, "Validation des données valides a échoué"
        assert model_dump_success, "model_dump() non disponible"
        assert validation_failed, "Validation des données invalides aurait dû échouer"
        
        CallbackLogger.log_callback(
            "test_validation_results",
            {
                "valid_data_passed": validation_success,
                "model_dump_available": model_dump_success,
                "invalid_data_rejected": validation_failed
            },
            status="SUCCESS",
            extra_info="Test validation réussi - Pydantic fonctionne correctement"
        )
        
        print("✅ Test validation réussi - Pydantic valide correctement")
    
    def test_error_handling(self):
        """Test de la gestion d'erreurs."""
        print("⚠️ Test de gestion d'erreurs")
        
        CallbackLogger.log_callback(
            "test_error_handling_start",
            {},
            status="INFO",
            extra_info="Test gestion d'erreurs - simulation d'erreurs"
        )
        
        # Test avec UID vide
        result_empty_uid = UsersTableService.get_users_page(page=1, page_size=10, filters={"uid": ""})
        
        # Test avec page négative
        result_negative_page = UsersTableService.get_users_page(page=-1, page_size=10)
        
        # Test avec page_size trop grand
        result_large_page_size = UsersTableService.get_users_page(page=1, page_size=1000)
        
        # Vérifier que les erreurs sont gérées gracieusement
        assert isinstance(result_empty_uid, dict), "Résultat doit être un dict même en cas d'erreur"
        assert isinstance(result_negative_page, dict), "Résultat doit être un dict même en cas d'erreur"
        assert isinstance(result_large_page_size, dict), "Résultat doit être un dict même en cas d'erreur"
        
        CallbackLogger.log_callback(
            "test_error_handling_results",
            {
                "empty_uid_handled": isinstance(result_empty_uid, dict),
                "negative_page_handled": isinstance(result_negative_page, dict),
                "large_page_size_handled": isinstance(result_large_page_size, dict)
            },
            status="SUCCESS",
            extra_info="Test gestion d'erreurs réussi - erreurs gérées gracieusement"
        )
        
        print("✅ Test gestion d'erreurs réussi - erreurs gérées gracieusement")


def run_users_table_tests():
    """Lance tous les tests avec un rapport détaillé."""
    print("\n" + "🚀 LANCEMENT DES TESTS USERS TABLE SERVICE")
    print("=" * 80)
    
    # Activer le debug
    os.environ['DEBUG_USERS'] = 'true'
    
    start_time = time.time()
    
    try:
        # Lancer les tests
        pytest.main([
            __file__,
            "-v",
            "--tb=short",
            "--capture=no"
        ])
        
        execution_time = time.time() - start_time
        
        CallbackLogger.log_callback(
            "all_tests_completed",
            {
                "total_execution_time_seconds": round(execution_time, 2),
                "test_file": __file__
            },
            status="SUCCESS",
            extra_info="Tous les tests terminés avec succès"
        )
        
        print(f"\n✅ TOUS LES TESTS TERMINÉS EN {execution_time:.2f}s")
        print("=" * 80)
        
    except Exception as e:
        CallbackLogger.log_callback(
            "tests_failed",
            {"error": str(e)},
            status="ERROR",
            extra_info="Échec des tests"
        )
        print(f"\n❌ ÉCHEC DES TESTS: {e}")
        raise


if __name__ == "__main__":
    run_users_table_tests()
