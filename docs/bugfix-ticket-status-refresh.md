# Correction de Rafraîchissement du Statut des Tickets

## Problème

Lorsqu'un administrateur change le statut d'un ticket de support (par exemple, de `OPEN` à `CLOSED`), puis filtre la liste des tickets pour afficher les tickets fermés et sélectionne à nouveau ce ticket, l'interface utilisateur n'affiche pas le bouton d'action correct (`Rouvrir` au lieu de `Marquer Fermé`). Pour que l'interface utilisateur se mette à jour, il est nécessaire de sélectionner un autre ticket puis de revenir au ticket affecté.

## Cause du Problème

Le problème réside dans la gestion de l'état local du composant `SupportPageClient` (`frontend/src/app/support/support-client.tsx`). Bien que la Server Action `updateTicketStatusAction` (dans `frontend/src/app/support/actions.ts`) utilise correctement `revalidatePath('/support')` pour invalider le cache de la page serveur, les états `selectedTicketId` et `selectedTicket` du `SupportPageClient` ne sont pas mis à jour automatiquement lorsque les props `initialSelectedId` et `initialSelectedTicket` (provenant du Server Component `frontend/src/app/support/page.tsx`) changent.

Les hooks `useState` en React n'initialisent leur valeur qu'une seule fois, lors du premier rendu du composant. Les mises à jour subséquentes des props passées à un composant client n'entraînent pas la mise à jour automatique des états locaux initialisés avec ces props, à moins qu'un `useEffect` ne soit spécifiquement mis en place pour cela.

## Solution

Pour corriger ce comportement, nous devons ajouter un hook `useEffect` dans le composant `SupportPageClient` qui écoute les changements des props `initialSelectedId` et `initialSelectedTicket`. Lorsque ces props changent (suite à la revalidation du chemin par la Server Action et le re-rendu du Server Component), le `useEffect` mettra à jour les états locaux correspondants, forçant ainsi le `TicketDetails` à se rafraîchir avec les données les plus récentes.

## Étapes de Correction

1.  **Modifier `frontend/src/app/support/support-client.tsx`**

    Ajoutez le `useEffect` suivant dans le composant `SupportPageClient` :

    ```typescript
    // frontend/src/app/support/support-client.tsx

    import { useState, useCallback, useEffect } from "react"; // Assurez-vous d'importer useEffect
    import { useRouter, useSearchParams } from "next/navigation";
    import type {
      SupportTicketWithUser,
      TicketDetail,
    } from "@/types/support";
    import { TicketTable } from "@/components/support/ticket-table";
    import { TicketDetails } from "@/components/support/ticket-details";

    interface SupportPageClientProps {
      tickets: SupportTicketWithUser[];
      initialSelectedId: string | null;
      initialSelectedTicket: TicketDetail | null;
    }

    export function SupportPageClient({
      tickets,
      initialSelectedId,
      initialSelectedTicket,
    }: SupportPageClientProps) {
      const router = useRouter();
      const searchParams = useSearchParams();

      const [selectedTicketId, setSelectedTicketId] = useState<string | null>(
        initialSelectedId
      );
      const [selectedTicket, setSelectedTicket] = useState<TicketDetail | null>(
        initialSelectedTicket
      );
      const [isLoading, setIsLoading] = useState(false);
      const [error, setError] = useState<string | null>(null);

      // --- NOUVEAU CODE ---
      useEffect(() => {
        setSelectedTicketId(initialSelectedId);
        setSelectedTicket(initialSelectedTicket);
      }, [initialSelectedId, initialSelectedTicket]);
      // --------------------

      // ... le reste du composant (handleSelectTicket, handleAddComment, return JSX)
    }
    ```

## Vérification

Après avoir appliqué cette modification, redémarrez votre serveur de développement. Lorsque vous changerez le statut d'un ticket, l'interface utilisateur devrait maintenant se mettre à jour correctement pour afficher les actions appropriées (`Rouvrir`, `Marquer Fermé`, etc.) sans nécessiter de re-sélectionner le ticket.
