# Guide d'Intégration WhatsApp Business (Klando)

Ce document explique comment utiliser et faire évoluer l'intégration WhatsApp dans KlandoDash.

## 1. État Actuel : Partage Manuel (wa.me)
Actuellement, KlandoDash permet de générer des messages optimisés par IA pour WhatsApp.
*   **Fonctionnement** : Un bouton "Envoyer via WhatsApp" ouvre un lien `https://wa.me/` avec le texte pré-rempli.
*   **Avantages** : Gratuit, aucune configuration API requise, utilise votre compte WhatsApp habituel ou Business.
*   **Limites** : Nécessite une action manuelle pour chaque message, pas de gestion de groupes automatisée.

---

## 2. Intégration WhatsApp Business API (Officielle)
Pour automatiser l'envoi de messages et gérer des groupes à grande échelle, vous devez utiliser la **Meta Cloud API**.

### Étapes de configuration :
1.  **Compte Meta Business** : Créez une application sur le [Portail Développeur Meta](https://developers.facebook.com/).
2.  **Configuration WhatsApp** : Ajoutez un numéro de téléphone valide à votre application.
3.  **Variables d'environnement** : Ajoutez les clés suivantes à votre `.env.local` :
    ```bash
    WHATSAPP_ACCESS_TOKEN=votre_token_permanent
    WHATSAPP_PHONE_NUMBER_ID=votre_id_numero
    ```
4.  **Envoi Automatisé** : Utilisez un `action.ts` pour appeler l'API Meta :
    ```typescript
    fetch(`https://graph.facebook.com/v17.0/${process.env.WHATSAPP_PHONE_NUMBER_ID}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.WHATSAPP_ACCESS_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        messaging_product: "whatsapp",
        to: recipient_phone,
        type: "template",
        template: { name: "welcome_message", language: { code: "fr" } }
      })
    });
    ```

---

## 3. Gestion des Groupes
La gestion des groupes via l'API officielle est restreinte aux comptes Business vérifiés et nécessite souvent l'utilisation de **Templates**.

**Alternative recommandée pour les groupes (via Twilio/360dialog)** :
Si votre objectif principal est de créer dynamiquement des groupes par trajet :
1.  Utilisez un fournisseur comme **Twilio** (via leur API WhatsApp).
2.  Twilio permet de créer des "Conversations" qui peuvent agir comme des groupes de diffusion.

---

## 4. Prochaines Étapes suggérées pour Klando
1.  **Table dédiée** : Créer une table `dash_marketing_whatsapp` pour suivre les messages envoyés (similaire à `dash_marketing_emails`).
2.  **Webhooks** : Configurer un endpoint `/api/webhooks/whatsapp` pour recevoir les confirmations de lecture et les réponses des clients.
3.  **Onglet dédié** : Ajouter un onglet "WhatsApp Hub" dans le Centre Éditorial pour séparer les réseaux sociaux du messaging direct.
