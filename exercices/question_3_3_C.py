# Question 3.3.C — Endpoint d'évaluation de l'agent
#
# POST /agent/evaluate
#
# Body : {"test_cases": [{"question": "...", "expected_keywords": ["mot1", "mot2"]}, ...]}
#
# Retour : {"score": 0.75, "total": 4, "passed": 3, "details": [...]}
#
# Le endpoint interroge l'agent pour chaque question, vérifie la présence
# des mots-clés dans la réponse, et calcule un score global.
