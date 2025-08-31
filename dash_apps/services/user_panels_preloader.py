import datetime as _dt
from typing import Dict, Any, Optional

import pandas as pd

from dash_apps.utils.data_schema import get_trips_for_user


class UserPanelsPreloader:
    """
    Construit un bundle JSON compact pour les panneaux (profil, stats, aperçus trajets)
    des utilisateurs visibles sur la page courante.

    Méthode principale:
      build(page_userdata: dict, current_page: int, existing_store: Optional[dict]) -> dict
    """

    MAX_TRIPS_PREVIEW = 5

    @staticmethod
    def _to_jsonable(obj: Any) -> Any:
        import datetime as _dt2
        import decimal as _dec2

        # Déballer pydantic-like
        if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
            try:
                obj = obj.model_dump()
            except Exception:
                obj = dict(obj)
        elif hasattr(obj, "dict") and callable(getattr(obj, "dict")) and not isinstance(obj, dict):
            try:
                obj = obj.dict()
            except Exception:
                try:
                    obj = dict(obj)
                except Exception:
                    obj = str(obj)

        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj

        try:
            if isinstance(obj, (_dt2.datetime, _dt2.date)):
                return obj.isoformat()
        except Exception:
            pass

        try:
            if isinstance(obj, _dec2.Decimal):
                return float(obj)
        except Exception:
            pass

        if isinstance(obj, (list, tuple, set)):
            return [UserPanelsPreloader._to_jsonable(v) for v in list(obj)]

        if isinstance(obj, dict):
            return {k: UserPanelsPreloader._to_jsonable(v) for k, v in obj.items()}

        try:
            return str(obj)
        except Exception:
            return None

    @staticmethod
    def build(page_userdata: Dict[str, Any], current_page: Any, existing_store: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Validation
        if not isinstance(page_userdata, dict) or not page_userdata:
            return existing_store or {}

        by_uid: Dict[str, Any] = {}

        for uid, profile in page_userdata.items():
            if not uid:
                continue

            profile_data = profile or {}
            # Normaliser les champs obligatoires pour les panneaux
            REQUIRED = [
                "uid", "display_name", "email", "first_name", "name", "phone_number",
                "birth", "photo_url", "bio", "driver_license_url", "gender", "id_card_url",
                "rating", "rating_count", "role", "updated_at", "created_at", "is_driver_doc_validated",
            ]
            normalized: Dict[str, Any] = {k: profile_data.get(k) for k in REQUIRED}
            # Fallbacks
            if normalized.get("phone_number") is None and profile_data.get("phone") is not None:
                normalized["phone_number"] = profile_data.get("phone")
            if normalized.get("created_at") is None and profile_data.get("created_time") is not None:
                normalized["created_at"] = profile_data.get("created_time")
            if normalized.get("updated_at") is None and profile_data.get("updated_time") is not None:
                normalized["updated_at"] = profile_data.get("updated_time")
            # Casts doux
            try:
                if normalized.get("rating") is not None:
                    normalized["rating"] = float(normalized["rating"])  # Numeric -> float
            except Exception:
                pass
            try:
                if normalized.get("rating_count") is not None:
                    normalized["rating_count"] = int(normalized["rating_count"])  # -> int
            except Exception:
                pass

            # Récupérer les trajets pour stats et aperçu
            try:
                driver_df = get_trips_for_user(str(uid), as_driver=True, as_passenger=False)
            except Exception:
                driver_df = pd.DataFrame()
            try:
                passenger_df = get_trips_for_user(str(uid), as_driver=False, as_passenger=True)
            except Exception:
                passenger_df = pd.DataFrame()

            # Stats
            try:
                driver_count = len(driver_df)
                passenger_count = len(passenger_df)
                total_trips = driver_count + passenger_count
                driver_distance = driver_df['distance'].sum() if (not driver_df.empty and 'distance' in driver_df.columns) else 0
                passenger_distance = passenger_df['distance'].sum() if (not passenger_df.empty and 'distance' in passenger_df.columns) else 0
                total_distance = float(driver_distance + passenger_distance)
            except Exception:
                driver_count = passenger_count = total_trips = 0
                total_distance = 0.0

            stats = {
                "total_trips": int(total_trips),
                "driver_trips": int(driver_count),
                "passenger_trips": int(passenger_count),
                "total_distance": total_distance,
            }

            # Aperçu trajets
            try:
                if not driver_df.empty:
                    driver_df = driver_df.copy()
                    driver_df['__role__'] = 'driver'
                if not passenger_df.empty:
                    passenger_df = passenger_df.copy()
                    passenger_df['__role__'] = 'passenger'
                combined = pd.concat([df for df in [driver_df, passenger_df] if not df.empty], ignore_index=True)
                if not combined.empty:
                    if 'departure_schedule' in combined.columns:
                        combined = combined.sort_values(by='departure_schedule', ascending=False)
                    preview_rows = combined.head(UserPanelsPreloader.MAX_TRIPS_PREVIEW)
                    trips_preview = []
                    for _, row in preview_rows.iterrows():
                        row_dict = row.to_dict()
                        trips_preview.append({
                            "trip_id": str(row_dict.get('trip_id') or row_dict.get('id') or ''),
                            "role": row_dict.get('__role__') or '-',
                            "departure_schedule": str(row_dict.get('departure_schedule') or ''),
                            "origin": row_dict.get('origin') or row_dict.get('start') or row_dict.get('from') or '-',
                            "destination": row_dict.get('destination') or row_dict.get('end') or row_dict.get('to') or '-',
                            "status": row_dict.get('status') or '-',
                        })
                else:
                    trips_preview = []
            except Exception:
                trips_preview = []

            by_uid[str(uid)] = {
                "profile": UserPanelsPreloader._to_jsonable(normalized),
                "stats": UserPanelsPreloader._to_jsonable(stats),
                "trips_preview": UserPanelsPreloader._to_jsonable(trips_preview),
            }

        try:
            generated_at = _dt.datetime.utcnow().isoformat()
        except Exception:
            generated_at = None

        store = {
            "page": int(current_page) if isinstance(current_page, (int, float)) else None,
            "by_uid": by_uid,
            "generated_at": generated_at,
        }
        return store
