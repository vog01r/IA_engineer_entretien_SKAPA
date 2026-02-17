"""Module de cache intelligent avec TTL pour optimiser les performances.

Architecture :
- Cache en mémoire (dict) avec TTL
- Thread-safe (pour usage concurrent)
- Éviction automatique des entrées expirées
- Métriques de hit/miss pour monitoring

Usage :
    from backend.shared.cache import cache_with_ttl

    @cache_with_ttl(ttl_seconds=600)  # 10 minutes
    def fetch_weather(lat: float, lon: float):
        return expensive_api_call(lat, lon)
"""
import functools
import logging
import threading
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

# Type hints pour le décorateur
F = TypeVar("F", bound=Callable[..., Any])


class CacheEntry:
    """Entrée de cache avec TTL."""

    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée."""
        return time.time() > self.expires_at


class TTLCache:
    """Cache thread-safe avec TTL et métriques."""

    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """Récupère une valeur du cache (None si absente ou expirée)."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                logger.debug(f"🗑️ [CACHE] Expired: {key}")
                return None

            self._hits += 1
            logger.debug(f"✅ [CACHE] Hit: {key}")
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int):
        """Stocke une valeur dans le cache avec TTL."""
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl_seconds)
            logger.debug(f"💾 [CACHE] Set: {key} (TTL={ttl_seconds}s)")

    def clear(self):
        """Vide le cache."""
        with self._lock:
            self._cache.clear()
            logger.info("🗑️ [CACHE] Cleared")

    def stats(self) -> dict[str, int]:
        """Retourne les statistiques du cache."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                "hits": self._hits,
                "misses": self._misses,
                "total": total,
                "hit_rate": hit_rate,
                "size": len(self._cache),
            }

    def cleanup_expired(self):
        """Nettoie les entrées expirées (à appeler périodiquement)."""
        with self._lock:
            expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
            for key in expired_keys:
                del self._cache[key]
            if expired_keys:
                logger.info(f"🗑️ [CACHE] Cleaned {len(expired_keys)} expired entries")


# Instance globale du cache
_global_cache = TTLCache()


def cache_with_ttl(ttl_seconds: int) -> Callable[[F], F]:
    """Décorateur pour cacher le résultat d'une fonction avec TTL.

    Args:
        ttl_seconds: Durée de vie du cache en secondes

    Example:
        @cache_with_ttl(ttl_seconds=600)  # 10 minutes
        def fetch_weather(lat: float, lon: float):
            return expensive_api_call(lat, lon)
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Créer une clé unique basée sur func + args + kwargs
            cache_key = f"{func.__module__}.{func.__name__}:{args}:{sorted(kwargs.items())}"

            # Vérifier le cache
            cached_value = _global_cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Cache miss : appeler la fonction
            result = func(*args, **kwargs)

            # Stocker dans le cache
            _global_cache.set(cache_key, result, ttl_seconds)

            return result

        return wrapper  # type: ignore

    return decorator


def get_cache_stats() -> dict[str, int]:
    """Retourne les statistiques du cache global."""
    return _global_cache.stats()


def clear_cache():
    """Vide le cache global."""
    _global_cache.clear()


def cleanup_cache():
    """Nettoie les entrées expirées du cache global."""
    _global_cache.cleanup_expired()
