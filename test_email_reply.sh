#!/bin/bash
# Script de test pour simuler une réponse email client

echo "🧪 Test de réception d'email client"
echo "=================================="

# Données de test avec un vrai ticket ID de votre base
curl -X POST http://localhost:8050/api/email/test \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Re: Réponse à votre ticket de support - TEST DE TICKET",
    "from": "achilletsak@gmail.com",
    "body": "Bonjour,\n\nMerci pour votre réponse. J'\''ai une question supplémentaire concernant mon problème...\n\nCordialement,\nAchille\n\n---\nTicket ID: 4e4745ab-9aff-4025-b003-16a2f99ff300"
  }'

echo -e "\n\n✅ Test envoyé. Vérifiez votre interface support pour voir le nouveau commentaire."
