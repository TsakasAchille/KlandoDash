# Notes Techniques - KlandoDash

## Emails (Resend) - Limitation Wix

### Probleme
Resend requiert un enregistrement MX sur un sous-domaine (`send.klando-sn.com`) pour verifier le domaine.
**Wix ne supporte pas les MX sur sous-domaines.**

### Configuration actuelle (workaround)
```env
RESEND_API_KEY=re_xxx
RESEND_FROM_EMAIL=KlandoDash <onboarding@resend.dev>
```

- Les emails fonctionnent via le domaine de test Resend
- L'expediteur affiche `onboarding@resend.dev` au lieu de `no-reply@klando-sn.com`
- **Important :** `onboarding@resend.dev` ne fonctionne que pour l'email inscrit sur Resend
- C'est cosmétique, les emails arrivent correctement

### Pour utiliser `@klando-sn.com` - BLOQUE

**Pourquoi c'est bloque :**
1. Resend exige un record MX sur sous-domaine (`send.klando-sn.com`)
2. Wix ne supporte PAS les MX sur sous-domaines
3. Wix bloque aussi le changement de nameservers

**Pourquoi Wix → Cloudflare est IMPOSSIBLE :**
- Cloudflare exige de changer les nameservers AVANT le transfert
- Wix bloque le changement de nameservers
- C'est un cercle vicieux : pas de changement NS = pas de transfert


**Solution recommandée :**
```
Wix → Namecheap → Configurer Resend immédiatement
```
1. Transférer de Wix vers Namecheap (.com supporté)
2. Configurer les records MX sur Namecheap (pas d'attente)
3. Vérifier sur Resend
4. Optionnel : plus tard transférer vers Cloudflare (gratuit)

**Records DNS requis par Resend :**
- TXT `resend._domainkey` (DKIM)
- MX `send` -> `feedback-smtp.eu-west-1.amazonses.com` (priorité 10)
- TXT `send` -> `v=spf1 include:amazonses.com ~all`
- TXT `_dmarc` -> `v=DMARC1; p=none;`

**Conclusion :** Transfert vers Namecheap pour débloquer Resend.

**Sources :**
- https://community.cloudflare.com/t/transfer-domain-wix-to-cloudflare/328976
- https://easycloudsupport.zendesk.com/hc/en-us/articles/25977603447693

### Records DNS actuels (Wix)

| Type | Nom | Valeur |
|------|-----|--------|
| TXT | `resend._domainkey` | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC9wS/pezFkReaXh+eA6LUm7HB8ZfEnd4fOjhKhCuFXkY3WPejqk8ijCoibl08lnN7QOXFtX5H7TF3ZeE/WqdGw1UtalvVeeDTDXqP5fVtc+G0e6tzN6CLa8Nl4q/KXELwjqkWeFIvDRXD7zxuVOkgCvrIlTNUxztKpjUwuFMz+2wIDAQAB` |
| TXT | `send` | `v=spf1 include:amazonses.com ~all` |
| TXT | `_dmarc` | `v=DMARC1; p=none;` |
| MX | `send` | **Impossible sur Wix** |

### Statut Resend
- Domain: `klando-sn.com`
- Status: **Non verifie** (MX manquant)
- Workaround: Utilisation de `onboarding@resend.dev`

---

*Dernière mise à jour : 26 janvier 2026*

## Prochaines étapes - Transfert Namecheap

1. ✅ **Déverrouiller le domaine** chez Wix
2. ✅ **Obtenir le code EPP** (code d'autorisation) - achille.tsakas@gmail.com
3. **Créer compte Namecheap**
4. **Initier le transfert** vers Namecheap (~$9.99)
5. **Configurer les records MX** une fois transféré
6. **Vérifier le domaine** sur Resend
7. **Mettre à jour** `RESEND_FROM_EMAIL` dans `.env`

**Coût estimé :** ~$10 pour le transfert + renouvellement annuel
