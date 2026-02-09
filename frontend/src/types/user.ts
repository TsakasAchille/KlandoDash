// Type pour la liste des utilisateurs
export interface UserListItem {
  uid: string;
  display_name: string | null;
  email: string | null;
  phone_number: string | null;
  photo_url: string | null;
  rating: number | null;
  rating_count: number | null;
  role: string | null;
  gender: string | null;
  birth: string | null;
  created_at: string | null;
  is_driver_doc_validated?: boolean | null;
  bio?: string | null;
}

// Type détaillé avec stats
export interface UserDetail extends UserListItem {
  first_name: string | null;
  name: string | null;
  birth: string | null;
  bio: string | null;
  gender: string | null;
  driver_license_url: string | null;
  id_card_url: string | null;
  is_driver_doc_validated: boolean | null;
  updated_at: string | null;
  // Stats calculées
  trips_as_driver: number;
  trips_as_passenger: number;
}

// Stats globales utilisateurs
export interface UserStats {
  total_users: number;
  verified_drivers: number;
  avg_rating: number;
  new_this_month: number;
}
