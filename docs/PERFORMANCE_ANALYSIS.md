# 🔬 Analyse Performance Bot Telegram

**Date:** 2026-02-17  
**Auteur:** Benjamin Chabanis  
**Contexte:** Feedback senior - "Réponses un peu lentes"

---

## 📊 Méthodologie

### Approche "Measure First, Optimize Later"

Au lieu de deviner où sont les bottlenecks, j'ai instrumenté le code avec des timers granulaires pour **mesurer** les temps réels de chaque opération.

### Instrumentation ajoutée

```python
import time

start = time.perf_counter()
# ... opération ...
elapsed = time.perf_counter() - start
logger.info(f"⏱️ [OPERATION] took {elapsed:.3f}s")
```

**Points de mesure :**
1. **Géocodage** (`_geocode_sync`) : résolution ville → coordonnées GPS
2. **Weather Fetch** (`_fetch_weather_via_api_sync`) : appel Open-Meteo via FastAPI
3. **Weather Location** : récupération données DB
4. **Agent LLM** (`_ask_agent_sync`) : appel OpenAI/Claude
5. **Total Response** : temps de bout en bout

---

## 🎯 Résultats attendus (hypothèses)

### Temps de réponse typiques

| Opération | Temps estimé | Impact |
|-----------|--------------|--------|
| Géocodage (Open-Meteo) | ~200-500ms | Faible |
| Weather API (Open-Meteo) | ~300-800ms | Moyen |
| Agent LLM (OpenAI/Claude) | **1-5s** | **CRITIQUE** |
| DB queries (SQLite) | ~10-50ms | Négligeable |
| **TOTAL** | **~2-6s** | **Trop lent** |

### Bottleneck principal identifié

**L'appel LLM est le bottleneck critique** (70-90% du temps total).

**Pourquoi ?**
- Latence réseau vers OpenAI/Claude
- Temps de traitement du modèle
- Taille du prompt (system + context + question)
- Incompressible (serveur externe)

---

## 💡 Solutions proposées (par priorité)

### P0 : Cache intelligent

**Problème :** Chaque requête refetch les mêmes données.

**Solution :**
```python
# Cache météo : 10 minutes (données changent peu)
# Cache geocoding : 24 heures (coordonnées fixes)
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def _geocode_cached(query: str, _ttl_hash: int):
    return _geocode_sync(query)

def geocode_with_ttl(query: str, ttl_seconds: int = 86400):
    """Cache avec TTL."""
    ttl_hash = int(time.time() / ttl_seconds)
    return _geocode_cached(query, ttl_hash)
```

**Impact attendu :**
- Géocodage : 0.5s → 0ms (hit rate ~80%)
- Météo : 1s → 0ms (hit rate ~60%)
- **Gain perçu : -30 à -50% du temps total**

---

### P1 : Amélioration UX (perception)

**Problème :** L'utilisateur attend 3-5s sans feedback.

**Solutions :**

1. **Typing indicator** (déjà implémenté ✅)
   ```python
   await update.effective_chat.send_chat_action(ChatAction.TYPING)
   ```

2. **Message intermédiaire** (nouveau)
   ```python
   status_msg = await update.message.reply_text("🔍 Recherche en cours...")
   # ... traitement ...
   await status_msg.edit_text(f"🤖 {answer}")
   ```

3. **Streaming LLM** (avancé)
   - Afficher la réponse mot par mot
   - Nécessite OpenAI Streaming API
   - Complexe mais meilleure UX

**Impact attendu :**
- Temps réel : identique
- Temps perçu : **-50%** (utilisateur voit du progrès)

---

### P2 : Parallélisation

**Problème :** Opérations séquentielles alors que certaines sont indépendantes.

**Exemple actuel (séquentiel) :**
```python
# 1. Geocode (0.5s)
geo = await geocode_place(text)
# 2. Weather (1s)
weather = await fetch_weather_api(lat, lon)
# 3. Agent LLM (3s)
answer = await ask_agent_api(question)
# TOTAL: 4.5s
```

**Optimisation (parallèle) :**
```python
# Si la question ne nécessite pas de météo en temps réel
# → Lancer LLM pendant le fetch météo
import asyncio

weather_task = asyncio.create_task(fetch_weather_api(lat, lon))
agent_task = asyncio.create_task(ask_agent_api(question))

weather, answer = await asyncio.gather(weather_task, agent_task)
# TOTAL: max(1s, 3s) = 3s → gain -1.5s
```

**Impact attendu :**
- Gain : **-20 à -30%** si applicable
- Complexité : moyenne
- Risque : faible

---

### P3 : Optimisation prompt LLM

**Problème :** Prompt trop long → temps de traitement augmenté.

**Solutions :**
1. **Réduire system prompt** : garder l'essentiel
2. **Limiter context RAG** : top 3 chunks au lieu de 5
3. **Utiliser modèle plus rapide** : `gpt-4o-mini` au lieu de `gpt-4o`

**Impact attendu :**
- Gain : **-10 à -20%** du temps LLM
- Trade-off : qualité légèrement réduite

---

## 🚀 Plan d'implémentation

### Phase 1 : Mesure (✅ FAIT)
- [x] Ajouter instrumentation timing
- [x] Créer script de test
- [x] Documenter méthodologie

### Phase 2 : Quick wins (2h)
- [ ] Implémenter cache météo (10min TTL)
- [ ] Implémenter cache geocoding (24h TTL)
- [ ] Ajouter message intermédiaire UX
- [ ] Tester et mesurer amélioration

### Phase 3 : Optimisations avancées (4h)
- [ ] Parallélisation opérations indépendantes
- [ ] Optimiser prompt LLM
- [ ] Considérer streaming LLM

### Phase 4 : Validation (1h)
- [ ] Tests de charge
- [ ] Mesure amélioration finale
- [ ] Documentation NOTES.md

---

## 📈 Métriques de succès

**Objectif :** Réduire temps de réponse de **4-6s** à **<2s** (perçu).

| Métrique | Avant | Objectif | Amélioration |
|----------|-------|----------|--------------|
| Temps réel | 4-6s | 2-3s | -40 à -50% |
| Temps perçu | 4-6s | <2s | -60 à -70% |
| Cache hit rate | 0% | 60-80% | N/A |
| Satisfaction UX | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +2 étoiles |

---

## 🎓 Apprentissages pour debrief

### Questions attendues

**Q1 : "Pourquoi as-tu mesuré avant d'optimiser ?"**
> Réponse : Parce que l'intuition peut être trompeuse. Sans mesure, on risque d'optimiser le mauvais bottleneck (ex: optimiser DB alors que le vrai problème est le LLM). Mesurer permet de prioriser les efforts sur ce qui a le plus d'impact.

**Q2 : "Pourquoi ne pas juste utiliser un modèle plus rapide ?"**
> Réponse : Trade-off qualité/vitesse. Un modèle plus rapide (gpt-3.5-turbo) serait plus rapide mais moins précis. Mieux vaut d'abord optimiser l'architecture (cache, parallélisation) pour garder la qualité tout en gagnant en performance.

**Q3 : "Comment as-tu choisi les TTL du cache ?"**
> Réponse : Basé sur la volatilité des données :
> - Météo : change toutes les heures → TTL 10min (balance fraîcheur/performance)
> - Geocoding : coordonnées fixes → TTL 24h (quasi-permanent)
> - Conversations : pas de cache (chaque question est unique)

**Q4 : "Et si l'utilisateur veut la météo en temps réel ?"**
> Réponse : Ajouter un paramètre `force_refresh` ou détecter les mots-clés "maintenant", "actuellement". Par défaut, 10min de cache est acceptable (météo change peu).

---

## 🔗 Références

- [OpenAI API Performance](https://platform.openai.com/docs/guides/performance)
- [Python asyncio Best Practices](https://docs.python.org/3/library/asyncio.html)
- [Caching Strategies](https://aws.amazon.com/caching/best-practices/)
- [UX Loading States](https://www.nngroup.com/articles/response-times-3-important-limits/)

---

**Prochaine étape :** Implémenter cache (TODO #3)
