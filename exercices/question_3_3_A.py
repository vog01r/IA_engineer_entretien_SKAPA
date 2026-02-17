# Question 3.3.A — System Prompt amélioré & injection de contexte
#
# Objectif :
# 1. Écrire un system prompt professionnel pour l'agent Q&A
# 2. Modifier la méthode ask() pour injecter le contexte RAG dans les messages
#
# Le prompt doit :
# - Instruire le LLM à utiliser UNIQUEMENT le contexte fourni
# - Demander de citer les sources (nom du document)
# - Gérer le cas "information non disponible"
# - Définir un format de réponse structuré
#
# Livrables :
# - SYSTEM_PROMPT (str)
# - Fonction ask_with_context(agent, question) qui corrige le bug d'injection
