# Radar Layout Debug - Post-Mortem

## Le Probleme

La carte Leaflet dans l'onglet Radar (Pilotage) ne s'affichait pas ou s'ecrasait a 0px de hauteur.

Deux IA (Gemini + Claude) ont galere dessus. Voici l'analyse finale.

---

## Cause Racine : 3 problemes combines

### 1. Leaflet + Radix Tabs = `display: none`

Radix `TabsContent` cache les onglets inactifs avec `display: none`. Quand Leaflet s'initialise dans un conteneur cache, il calcule `width: 0, height: 0` et ne rend rien.

**Fix :** `forceMount` sur le TabsContent Radar + `hidden` CSS quand inactif.

```tsx
// pilotage-client.tsx
<TabsContent value="radar" forceMount className={activeTab !== "radar" ? "hidden" : ""}>
  <RadarTab ... />
</TabsContent>
```

`forceMount` = le composant reste monte en memoire (Leaflet ne se reinitialise pas).
`hidden` = cache avec CSS sans detruire le DOM.

### 2. Tailwind responsive breakpoints vs Grid fixe

Les classes `grid-cols-1 lg:grid-cols-[400px_1fr]` faisaient que la sidebar passait AU-DESSUS de la carte sur les ecrans < `lg` (1024px). Et meme sur desktop, les classes Tailwind entraient en conflit avec le layout parent (`max-w-[1600px]`, `overflow-auto` sur main, `space-y-8`).

**Fix :** Inline styles sur le grid container pour forcer le layout.

```tsx
<div style={{
  display: 'grid',
  gridTemplateColumns: '380px 1fr',
  gap: '24px',
  height: '75vh',
  marginTop: '24px'
}}>
```

Pourquoi inline et pas Tailwind ? Parce que les inline styles ont la priorite CSS la plus haute et ne peuvent pas etre overrides par les parents. C'est la seule facon de garantir que le grid reste cote-a-cote quelles que soient les contraintes du layout parent.

### 3. `overflow-auto` sur le `<main>` parent

Dans `layout-content.tsx`, le `<main>` a `overflow-auto`. Ca cree un nouveau contexte de stacking et peut empecher les enfants de prendre la bonne hauteur. Le `h-[calc(100vh-320px)]` en Tailwind etait override par la cascade CSS.

**Fix :** `height: '75vh'` en inline style sur le grid = le navigateur ne peut pas ignorer cette valeur.

---

## Architecture Finale

```
pilotage-client.tsx
  └── TabsContent[forceMount] ← Leaflet reste monte
        └── RadarTab.tsx
              ├── RadarControls (radar-controls.tsx)
              └── div[inline grid: 380px | 1fr, h:75vh]
                    ├── Sidebar Card
                    │     └── RadarSidebar (radar-sidebar.tsx)
                    │           ├── Section: Corridors Klando (indigo)
                    │           ├── Section: Facebook (bleu)
                    │           ├── Section: Site Web (emerald)
                    │           ├── Section: WhatsApp (vert)
                    │           └── Section: Matchs Trouves (gold)
                    └── Map Card
                          └── TripMap (w-full h-full + ResizeObserver)
```

## Fichiers modifies

| Fichier | Changement |
|---------|-----------|
| `pilotage-client.tsx` | `forceMount` + `hidden` sur TabsContent radar |
| `RadarTab.tsx` | Inline styles grid, suppression `key` sur TripMap |
| `radar-controls.tsx` | Suppression toggle Flux Klando |
| `radar-sidebar.tsx` | Sections collapsibles par source + matchs |

## Regles a retenir pour Leaflet dans des Tabs

1. **Toujours `forceMount`** le TabsContent qui contient une carte Leaflet
2. **Jamais de `key` dynamique** sur le composant carte (force un remount = tiles disparaissent)
3. **Inline styles pour le sizing critique** quand le composant est imbrique dans des layouts complexes
4. Le composant TripMap a deja un `ResizeObserver` + `invalidateSize()` qui gere le redimensionnement
5. `rounded-3xl` max sur le conteneur carte (pas `rounded-[2.5rem]` qui clip les controls Leaflet)
