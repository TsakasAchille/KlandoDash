"""
Test du nouveau système de validation moderne avec Pydantic
"""
import json
import os
from dash_apps.services.config_validator import ConfigValidator
from dash_apps.models.config_models import MainConfig
from dash_apps.utils.validation_utils import validate_json_file


def test_config_validation():
    """Test de validation d'une configuration existante"""
    print("🧪 TEST DU SYSTÈME DE VALIDATION MODERNE")
    print("=" * 60)
    
    # Chemin vers la configuration existante
    config_path = "/home/achille.tsakas/Klando/KlandoDash2/KlandoDash/dash_apps/config/trip_details_config.json"
    
    if not os.path.exists(config_path):
        print(f"❌ Fichier de configuration non trouvé: {config_path}")
        return False
    
    print(f"📁 Configuration testée: {config_path}")
    print()
    
    # Test 1: Validation Pydantic de base
    print("1️⃣ VALIDATION PYDANTIC DE BASE")
    result = validate_json_file(MainConfig, config_path)
    
    if result.success:
        print("✅ Configuration valide selon les modèles Pydantic")
    else:
        print("❌ Erreurs de validation Pydantic:")
        for error in result.errors:
            print(f"   • {error.get('field', 'unknown')}: {error.get('message', 'Erreur inconnue')}")
    print()
    
    # Test 2: Validation complète avec schéma DB
    print("2️⃣ VALIDATION COMPLÈTE (PYDANTIC + SCHÉMA DB)")
    full_result = ConfigValidator.validate_config_file(config_path)
    
    if full_result.success:
        print("✅ Configuration complètement valide")
    else:
        print("❌ Erreurs détectées:")
        for error in full_result.errors:
            print(f"   • {error.get('field', 'unknown')}: {error.get('message', 'Erreur inconnue')}")
    print()
    
    # Test 3: Rapport détaillé
    print("3️⃣ RAPPORT DÉTAILLÉ")
    report = ConfigValidator.get_validation_report(config_path)
    print(report)
    print()
    
    # Test 4: Résumé du schéma
    print("4️⃣ RÉSUMÉ DU SCHÉMA")
    schema_summary = ConfigValidator.get_schema_summary()
    if 'error' not in schema_summary:
        print(f"📊 Total colonnes: {schema_summary['total_columns']}")
        print(f"📊 Colonnes obligatoires: {len(schema_summary['required_columns'])}")
        print(f"📊 Colonnes datetime: {len(schema_summary['datetime_columns'])}")
        print(f"📊 Colonnes text: {len(schema_summary['text_columns'])}")
    else:
        print(f"❌ {schema_summary['error']}")
    
    return full_result.success


def create_test_config():
    """Crée une configuration de test pour valider le système"""
    test_config = {
        "trip_details": {
            "cache": {
                "enabled": True,
                "ttl_seconds": 300,
                "key_prefix": "trip_details"
            },
            "data_source": {
                "primary": "rest_api",
                "fallback": "sql",
                "timeout_seconds": 30
            },
            "validation": {
                "enabled": True,
                "schema_file": "trips_scheme.json",
                "strict_mode": False,
                "auto_fix": True
            },
            "rendering": {
                "sections": {
                    "basic_info": {
                        "title": "Informations de base",
                        "collapsible": False,
                        "default_collapsed": False,
                        "fields": {
                            "trip_id": {
                                "type": "integer",
                                "label": "ID du trajet",
                                "required": True
                            },
                            "start_time": {
                                "type": "datetime",
                                "label": "Heure de début",
                                "required": True,
                                "format": "iso"
                            },
                            "end_time": {
                                "type": "datetime",
                                "label": "Heure de fin",
                                "required": False,
                                "format": "iso"
                            }
                        }
                    },
                    "location_info": {
                        "title": "Informations de localisation",
                        "collapsible": True,
                        "default_collapsed": False,
                        "fields": {
                            "start_latitude": {
                                "type": "float",
                                "label": "Latitude de départ",
                                "required": False
                            },
                            "start_longitude": {
                                "type": "float",
                                "label": "Longitude de départ",
                                "required": False
                            }
                        }
                    }
                }
            }
        }
    }
    
    test_path = "/tmp/test_config.json"
    with open(test_path, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2, ensure_ascii=False)
    
    return test_path


def test_with_sample_config():
    """Test avec une configuration d'exemple"""
    print("\n🧪 TEST AVEC CONFIGURATION D'EXEMPLE")
    print("=" * 60)
    
    test_path = create_test_config()
    print(f"📁 Configuration de test créée: {test_path}")
    
    # Validation de la configuration de test
    result = ConfigValidator.validate_config_file(test_path)
    
    if result.success:
        print("✅ Configuration de test valide")
    else:
        print("❌ Erreurs dans la configuration de test:")
        for error in result.errors:
            print(f"   • {error.get('field', 'unknown')}: {error.get('message', 'Erreur inconnue')}")
    
    # Nettoyage
    os.unlink(test_path)
    
    return result.success


if __name__ == "__main__":
    print("🚀 DÉMARRAGE DES TESTS DE VALIDATION MODERNE")
    print()
    
    # Test avec la configuration existante
    success1 = test_config_validation()
    
    # Test avec une configuration d'exemple
    success2 = test_with_sample_config()
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Configuration existante: {'✅ SUCCÈS' if success1 else '❌ ÉCHEC'}")
    print(f"Configuration de test: {'✅ SUCCÈS' if success2 else '❌ ÉCHEC'}")
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS - Le système de validation moderne fonctionne parfaitement!")
    else:
        print("\n⚠️ Certains tests ont échoué - Vérifiez les erreurs ci-dessus")
