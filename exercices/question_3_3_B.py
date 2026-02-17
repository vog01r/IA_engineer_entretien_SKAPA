# Question 3.3.B — Fonction de chunking intelligent
#
# Signature : def smart_chunk(text: str, max_tokens: int = 500, overlap_tokens: int = 50) -> list[str]
#
# Contraintes :
# - Un "token" ≈ 4 caractères (ou utiliser tiktoken)
# - Ne jamais couper une phrase en deux
# - Overlap entre chunks consécutifs pour maintenir le contexte
# - Ignorer les chunks < 50 caractères
#
# Inclure un bloc if __name__ == "__main__" testant sur knowledge_base/
