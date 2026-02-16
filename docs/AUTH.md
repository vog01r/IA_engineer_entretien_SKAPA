# Authentification JWT - Documentation

Documentation technique de l'implémentation JWT pour le projet SKAPA.

---

## 🎯 Objectif

Remplacer l'authentification par clé API exposée dans le bundle frontend par un système JWT production-ready avec httpOnly cookies.

**Problème critique résolu :** Une clé API était exposée dans le bundle JavaScript frontend (visible via DevTools), permettant à n'importe qui d'appeler l'API sans restriction. La clé a été invalidée et remplacée.

---

## 🏗️ Architecture

```
Frontend (React) → httpOnly cookies → Backend (FastAPI) → SQLite
                                            ↓
                                    Services (Bot/MCP) → X-API-Key
```

### Dual Auth

| Service | Auth Method | Pourquoi |
|---------|-------------|----------|
| **Frontend Web** | JWT (httpOnly cookies) | Utilisateurs humains, sessions, révocable |
| **Bot Telegram** | X-API-Key header | Service-to-service, backward compatible |
| **MCP Server** | X-API-Key header | Service-to-service, backward compatible |

---

## 📦 Implémentation (10 commits)

### Backend (Commits 1-6)

**1. Dependencies & Config**
- `pyjwt[crypto]>=2.8.0`, `passlib[bcrypt]>=1.7.4`, `python-multipart>=0.0.6`, `slowapi>=0.1.9`
- Configuration JWT : SECRET (256 bits), ALGORITHM (HS256), EXPIRATION (60min access, 7j refresh)
- Cookie config : httpOnly, SameSite=lax, Secure=false (dev) / true (prod)

**2. Users Table & CRUD**
- Table `users` : id, email (UNIQUE), hashed_password, is_active, created_at, updated_at
- CRUD : `create_user()`, `get_user_by_email()`, `get_user_by_id()`, `update_user_password()`, `deactivate_user()`
- Email normalisé (lowercase), soft delete (is_active=0)

**3. JWT & Password Utils**
- `app/core/security.py` : Fonctions cryptographiques
- `hash_password()` : Bcrypt cost=12 (~250ms/hash), auto-salt
- `verify_password()` : Vérification constant-time
- `create_access_token()` : JWT HS256, durée 1h
- `create_refresh_token()` : JWT HS256, durée 7j
- `decode_token()` : Vérifie signature + expiration

**4. Auth Endpoints**
- `POST /auth/register` : Crée compte, retourne JWT dans httpOnly cookies
- `POST /auth/login` : Authentifie, retourne JWT dans httpOnly cookies
- `GET /auth/me` : Retourne profil user (protégé)
- `POST /auth/refresh` : Renouvelle access token
- `POST /auth/logout` : Supprime cookies

**5. Middleware get_current_user**
- `app/core/dependencies.py` : Dependency injection FastAPI
- Dual auth : JWT cookie OU X-API-Key header
- Priorité 1 : JWT → query DB → vérifie is_active
- Priorité 2 : X-API-Key → service account fictif (id=-1)
- Bypass OPTIONS : Preflight CORS

**6. Migration Routes**
- Routes `/weather/*` et `/agent/*` : `Depends(get_current_user)`
- Dual auth maintenue (pas de breaking change pour bot/MCP)

### Frontend (Commits 7-9)

**7. AuthContext**
- `frontend/src/contexts/AuthContext.jsx` : Context React
- `register()`, `login()`, `logout()`, `checkAuth()` : credentials: "include"
- Auto-refresh : Renouvelle token toutes les 55min

**8. LoginForm & RegisterForm**
- `frontend/src/components/auth/LoginForm.jsx` : Formulaire email + password
- `frontend/src/components/auth/RegisterForm.jsx` : Formulaire + confirmation
- Validation côté client, design SKAPA (teal accent)

**9. ProtectedRoute & API Update**
- `frontend/src/components/ProtectedRoute.jsx` : Wrapper pour routes protégées
- `frontend/src/App.jsx` : Wrapped avec AuthProvider + ProtectedRoute
- `frontend/src/services/api.js` : credentials: "include", suppression X-API-Key

### Cleanup (Commit 10)

**10. Suppression VITE_API_KEY**
- Suppression `VITE_API_KEY` de `.env`, `Dockerfile`
- Rotation API_KEY : Ancienne clé compromise invalidée → Nouvelle clé 256 bits générée
- Nouvelle clé stockée dans .env local (non commité)
- Clé utilisée uniquement par bot/MCP (X-API-Key header)

---

## 🔐 Sécurité

### Protections implémentées

- ✅ Passwords hashés avec bcrypt (jamais en clair)
- ✅ Tokens signés avec JWT_SECRET (HS256, 256 bits)
- ✅ httpOnly cookies (pas accessibles JS)
- ✅ SameSite=lax (protection CSRF basique)
- ✅ Vérification constant-time (bcrypt.verify)
- ✅ is_active vérifié (soft delete)
- ✅ Query DB à chaque requête (données fraîches)

### Attaques mitigées

| Attaque | Mitigation |
|---------|------------|
| XSS | httpOnly cookies (pas accessibles JS) |
| CSRF | SameSite=lax (compatible OAuth) |
| Brute-force | bcrypt cost=12 (~250ms = max ~3 tentatives/sec) |
| Timing attacks | bcrypt.verify constant-time |
| Token replay | Expiration courte (1h) |
| Rainbow tables | bcrypt auto-salt (unique par hash) |

---

## ⚡ Performance

| Opération | Temps | Impact |
|-----------|-------|--------|
| hash_password | ~250ms | Acceptable (register/login uniquement) |
| verify_password | ~250ms | Acceptable (login uniquement) |
| decode_token | <1ms | Négligeable |
| Query DB | ~1ms | Négligeable |
| **Total overhead/requête** | **~2ms** | **Négligeable** |

---

## 🔧 Configuration

### Variables d'environnement

**Backend (.env) :**
```bash
# JWT Configuration
JWT_SECRET=<générer avec openssl rand -hex 64>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Cookie Configuration
COOKIE_SECURE=false  # true en prod (HTTPS requis)
COOKIE_SAMESITE=lax
COOKIE_DOMAIN=  # vide = même domaine uniquement

# API Key (services uniquement)
API_KEY=<générer avec openssl rand -hex 32>
```

**Frontend (.env) :**
```bash
VITE_API_URL=http://localhost:8000
# VITE_API_KEY supprimée (plus utilisée)
```

### Railway

Variables à configurer :
- `JWT_SECRET` : Générer avec `openssl rand -hex 64`
- `COOKIE_SECURE` : true (HTTPS requis)
- `API_KEY` : Nouvelle clé 256 bits (bot/MCP uniquement)
- Supprimer `VITE_API_KEY` (plus utilisée)

---

## 🧪 Tests

### Test local

1. **Register** : `POST /auth/register` avec `{"email": "test@example.com", "password": "password123"}`
2. **Login** : `POST /auth/login` avec mêmes credentials
3. **Vérifier cookie** : DevTools → Application → Cookies → `skapa_access_token` (httpOnly)
4. **Appeler API** : `GET /weather/` (doit fonctionner avec cookie)
5. **Logout** : `POST /auth/logout` (cookie supprimé)

### Test bot Telegram

1. Mettre à jour `API_KEY` dans `.env`
2. Redémarrer bot : `python -m app.bot.telegram_bot`
3. Envoyer `/start` sur Telegram
4. Vérifier que le bot répond (X-API-Key header fonctionne)

---

## 💡 Trade-offs

| Aspect | Choix | Avantage | Inconvénient |
|--------|-------|----------|--------------|
| httpOnly cookies | ✅ | Protection XSS | Complexité CSRF |
| JWT HS256 | ✅ | Simple, rapide | Secret partagé, rotation complexe |
| Bcrypt cost=12 | ✅ | Résistant brute-force | Lent (~250ms) |
| Tokens courts (1h) | ✅ | Limite exploitation | Refresh fréquent |
| Dual auth | ✅ | Backward compat | Complexité code |
| Query DB par requête | ✅ | Données fraîches | +1 query (~1ms) |

---

## ❓ FAQ

**Q : Pourquoi JWT et pas sessions serveur ?**
- JWT = stateless, scalable horizontalement (pas de session store partagée)
- Adapté à Railway (services éphémères, pas de Redis)

**Q : Comment gérer la révocation des JWT ?**
- Tokens courts (1h) + refresh tokens (7j)
- Blacklist des refresh tokens en base si compromis
- Pour révocation immédiate : table `revoked_tokens` (trade-off performance)

**Q : Pourquoi pas OAuth (Google, GitHub) ?**
- Scope du test : démontrer implémentation auth from scratch
- OAuth = dépendance externe, complexité supplémentaire
- Peut être ajouté en complément (social login)

**Q : Impact sur le bot Telegram et MCP ?**
- Aucun : Ils gardent l'authentification par X-API-Key
- Deux modes d'auth cohabitent : JWT (web) + API Key (services)

**Q : Performance de bcrypt ?**
- Cost factor 12 = ~250ms par hash (acceptable pour login)
- Pas d'impact sur les requêtes normales (JWT vérifié en <1ms)

---

## 📚 Références

- [JWT.io](https://jwt.io/) : Décodeur JWT en ligne
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/) : Documentation officielle
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html) : Best practices sécurité
- [Bcrypt](https://en.wikipedia.org/wiki/Bcrypt) : Algorithme de hashing
