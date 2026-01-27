# Plan d'intégration - Table Transactions

## Contexte métier (info dev)

- `bookings.transaction_id` → FK vers `transactions`
- Prix conducteur : `trips.driver_price`
- Prix passager (réel payé) : `transactions.amount`
- **Marge Klando** = `transactions.amount` - `trips.driver_price` (inclut 15% TVA)
- **Cash flow** (logique Intech inversée) :
  - `XXXXX_CASH_IN` dans `code_service` → argent qui **SORT** pour Klando
  - `XXXXX_CASH_OUT` dans `code_service` → argent qui **RENTRE** pour Klando

---

## Étape 1 : Types et Queries

### 1.1 Mettre à jour `types/transaction.ts`
- Ajouter `TransactionWithBooking` (join booking + trip pour calcul marge)
- Ajouter type `CashFlowStats` (entrées, sorties, solde)

### 1.2 Mettre à jour `lib/queries/transactions.ts`
- `getTransactionsWithUser()` — déjà fait, garder tel quel
- `getTransactionsWithBooking()` — join transactions → bookings → trips pour avoir `driver_price`
- `getCashFlowStats()` — agrégation par `code_service` (CASH_IN = sortie, CASH_OUT = entrée)
- `getRevenueStats()` — marge Klando réelle (amount - driver_price par booking)
- `getTransactionsForUser(userId)` — déjà fait

### 1.3 Mettre à jour `lib/queries/stats.ts`
- Ajouter section `transactions` dans `DashboardStats`
- Remplacer le calcul `revenue` actuel (basé sur trips) par les vrais montants depuis transactions
- Ajouter cash flow (total CASH_IN, total CASH_OUT, solde)

---

## Étape 2 : Page `/transactions`

### 2.1 Structure (même pattern que `/trips`)
```
app/transactions/
├── page.tsx                 # Server component (fetch data)
└── transactions-client.tsx  # Client component (state, layout)

components/transactions/
├── transaction-table.tsx    # Tableau avec filtres
└── transaction-details.tsx  # Panel détail
```

### 2.2 Tableau (`transaction-table.tsx`)
- Colonnes : Utilisateur, Montant (XOF), Type, Service, Statut, Date
- Filtres : statut, type, code_service (CASH_IN/CASH_OUT)
- Pagination 10/page
- Deep linking `?selected=id`

### 2.3 Panel détail (`transaction-details.tsx`)
- Infos transaction complètes
- Lien vers profil utilisateur (comme trips → driver)
- Lien vers booking/trajet associé (via bookings.transaction_id)
- Calcul marge Klando affiché si booking lié

### 2.4 Stats badges en haut
- Total transactions
- Montant total
- Cash in / Cash out

---

## Étape 3 : Intégration page `/users`

### 3.1 Onglet Transactions dans le détail utilisateur
- Ajouter un système d'onglets (Trajets | Transactions) dans `user-details.tsx`
- Sous-tableau transactions similaire à `user-trips-table.tsx`
- Colonnes : Montant, Type, Statut, Date
- Pagination 5/page

---

## Étape 4 : Intégration page `/stats`

### 4.1 Nouvelle row "Transactions"
- Total transactions
- Montant total encaissé
- Répartition par statut
- Répartition par type

### 4.2 Mise à jour row "Revenus"
- Remplacer calcul basé sur trips par calcul réel depuis transactions
- Total passagers (sum transactions.amount)
- Total conducteurs (sum trips.driver_price via bookings)
- Marge Klando (différence)
- Cash flow : entrées (CASH_OUT) vs sorties (CASH_IN) vs solde

---

## Étape 5 : Navigation

### 5.1 Sidebar
- Ajouter lien "Transactions" (icône Banknote) → `/transactions`
- Visible pour rôles `admin` (et potentiellement `support`)

---

## Règles métier & edge cases

### Booking optionnel
- Certaines transactions n'ont PAS de booking (top-up, pénalité, remboursement…)
- `TransactionWithBooking` → `booking?: null`
- UI : afficher "Transaction hors trajet" quand pas de booking lié
- Marge Klando calculée uniquement quand booking existe

### Filtrage stats vs UI
- **UI (tableau)** : afficher toutes les transactions (tous statuts)
- **Stats (agrégations)** : compter uniquement `status = 'SUCCESS'`

### Signatures avec période (prévu)
- `getCashFlowStats({ from?: string, to?: string })`
- `getRevenueStats({ from?: string, to?: string })`
- Pas implémenté au lancement, mais signatures prêtes

### Indicateurs visuels
- Badge directionnel dans le tableau : ↗️ CASH_IN (sortie) / ↙️ CASH_OUT (entrée)
- Warning : transaction SUCCESS sans booking / booking sans transaction

### Export CSV (optionnel, post-lancement)
- Bouton export depuis `/transactions` pour la compta

---

## Ordre d'exécution

1. Types + queries (fondation)
2. Stats mise à jour (revenus réels)
3. Page `/transactions` (UI)
4. Onglet transactions dans `/users`
5. Sidebar navigation
