users.created_time -> created_at
users.short_description -> bio


Erreur lors de la vérification de l'autorisation dans la base de données: (psycopg2.OperationalError) connection to server at "aws-0-eu-west-3.pooler.supabase.com" (13.39.246.141), port 5432 failed: FATAL:  MaxClientsInSessionMode: max clients reached - in Session mode max clients are limited to pool_size



SELECT count(*) FROM pg_stat_activity;

[
  {
    "count": 29
  }
]