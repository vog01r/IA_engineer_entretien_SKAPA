# Test AI Agent Engineer — SKAPA

## Instructions de rendu

**Le rendu se fait intégralement sur Git par une Pull Request vers la branche `main` du repository.**

### Méthodologie de travail attendue

1. **Forkez** le dépôt ou créez une **branche dédiée** au développement.
2. **Committez régulièrement** votre avancement sur GitHub. Nous analyserons votre historique de commits pour évaluer votre méthodologie, votre progression et votre manière de structurer le développement.
3. **Remplissez ce document** (INSTRUCTIONS_QCM.md) : réponses au QCM, justifications, variante 3.3 choisie.
4. **Complétez le code** du repository : corrections de bugs, frontend, serveur MCP, bot Telegram.
5. **Ouvrez une Pull Request** vers `main` contenant :
   - ce fichier INSTRUCTIONS_QCM.md complété ;
   - l'ensemble des modifications de code et de configuration ;
   - dans la **description de la PR** : votre méthodologie (comment vous avez abordé le test, dans quel ordre, quels outils utilisés), les URLs de l'application, du frontend, de l'API, et du serveur MCP.

⚠️ Aucun rendu par zip ou par email : **tout doit figurer dans la PR**.

---

## Introduction

Bonjour à vous chère/cher candidate/candidat SKAPA.

Ce test technique évalue un spectre élargi de compétences en ingénierie d'agents IA : compréhension des LLMs, architecture d'agents, intégration de protocoles (MCP), développement backend/frontend, et sens critique face au code existant. Aussi, il est possible que vous n'ayez pas réponse à certaines des questions. Nous vous invitons à faire le maximum sur les questions que vous adressez. Veuillez noter que vos réponses pourront être analysées plus en profondeur lors d'un entretien technique oral ultérieur.

**Durée estimée :** 24 à 48 heures. Vous pouvez prendre plus de temps si nécessaire.

Le test est composé de **cinq parties** :

| Partie | Thème | Questions |
|--------|-------|-----------|
| **1 – SOCLE** | Fondamentaux : infra, sécurité, LLMs, agents IA, MCP | 1.1 → 1.15 |
| **2 – COMPRÉHENSION** | Analyse du projet fourni, identification des problèmes | 2.1 → 2.8 |
| **3 – TECHNIQUES** | Code, bugs, exercices pratiques | 3.1 → 3.12 |
| **4 – ARCHITECTURE** | Base de données, scalabilité, conception système | 4.1 → 4.12 |
| **5 – OUVERTE** | Vision, stratégie, production | 5.1 → 5.10 |

**Ressource de référence :** le document `docs/AI_Agents_and_MCP.pdf` (articles de Tomoro.ai) est fourni dans le repository. Plusieurs questions du QCM s'y réfèrent — **prenez le temps de le lire avant de répondre**.

Les QCM peuvent avoir **une, plusieurs ou toutes** les réponses possibles. Aucune question ne possède zéro réponse. Pour sélectionner votre réponse, indiquez la/les lettre(s) choisie(s) (ex. « A », « B et C », « A, B, C »). Lorsqu'une justification est demandée, rédigez-la dans l'emplacement prévu sous le tableau.

Bon test à vous.

---

## Partie 1 — SOCLE : fondamentaux

### Question 1.1

Quel est le principal avantage de l'utilisation de conteneurs Docker dans le développement et le déploiement d'applications ?

| A | B | C |
|---|---|---|
| Ils permettent une isolation de l'utilisation des ressources de la machine hôte. | Ils assurent l'isolation des applications et leurs dépendances, facilitant ainsi la portabilité et la cohérence entre les environnements de développement, de test et de production. | Ils augmentent la sécurité des applications en bloquant toute interaction réseau. |

**Réponse :** B

---

### Question 1.2

En termes de sécurité des données, quelle est la meilleure pratique pour la gestion des secrets (clés API, tokens) dans une application ?

| A | B | C |
|---|---|---|
| Stocker les clés en dur dans le code source ou dans un fichier `.env` versionné sur Git. | Utiliser un service de gestion des secrets (Vault, AWS Secrets Manager, KMS) ou des variables d'environnement configurées au niveau de l'infrastructure de déploiement. | Envoyer les clés par email ou Slack aux membres de l'équipe pour utilisation lorsque nécessaire. |

**Réponse :** B

---

### Question 1.3

Quelle caractéristique des bases de données NoSQL est particulièrement utile dans le contexte de données non structurées et big data ?

| A | B | C |
|---|---|---|
| La normalisation des données. | La flexibilité des schémas de données. | La prise en charge exclusive des transactions ACID. |

**Réponse :** B

---

### Question 1.4

Dans le contexte de l'ingénierie de données, quel outil est le plus adapté pour l'orchestration de workflows de données complexes ?

| A | B | C |
|---|---|---|
| Docker | Apache Kafka | Apache Airflow |

**Réponse :** C

---

### Question 1.5 *(réf. document Tomoro.ai)*

Quelle est la différence fondamentale entre un chatbot classique et un agent IA ?

| A | B | C |
|---|---|---|
| Un agent IA utilise obligatoirement GPT-4 ; un chatbot peut utiliser n'importe quel modèle. | Un agent IA possède une base de connaissances définie, peut initier plusieurs actions, et choisit la bonne action selon le contexte. Un chatbot se contente de générer du texte en réponse à un input. | Un agent IA fonctionne toujours sans intervention humaine ; un chatbot nécessite systématiquement un humain dans la boucle. |

**Réponse :** B

Réf. : [Tomoro.ai — What is an AI Agent?](https://tomoro.ai/insights/what-is-an-ai-agent)

---

### Question 1.6 *(réf. document Tomoro.ai)*

Dans le contexte des LLMs, qu'est-ce que l'« hallucination » ?

| A | B | C |
|---|---|---|
| Un bug logiciel qui provoque des crashs aléatoires du modèle. | Le fait qu'un LLM génère des réponses confidentes mais factuellement incorrectes, sans vérifier les informations disponibles — comme passer un examen open-book en s'appuyant uniquement sur sa mémoire. | Un mécanisme de sécurité qui empêche le modèle de répondre à certaines questions sensibles. |

**Réponse :** B

Réf. : [Tomoro.ai — Why all the fuss about MCP?](https://tomoro.ai/insights/why-all-the-fuss-about-mcp)

---

### Question 1.7

Quel est le rôle du RAG (Retrieval-Augmented Generation) dans un système d'agent IA ?

| A | B | C |
|---|---|---|
| Augmenter la taille du context window du LLM pour y faire tenir plus d'informations. | Récupérer des informations pertinentes depuis une source externe (base vectorielle, documents) et les injecter dans le prompt avant la génération de la réponse, permettant au LLM de s'appuyer sur des faits vérifiables. | Entraîner (fine-tuner) le LLM sur de nouvelles données pour mettre à jour ses connaissances internes. |

**Réponse :** B

**Justification :** RAG = récupérer des docs pertinents (base vectorielle, documents), les injecter dans le prompt, puis générer. Le LLM s'appuie sur des faits vérifiables. A = faux (RAG ne modifie pas la taille du context window). C = fine-tuning, pas RAG.

---

### Question 1.8

Parmi les techniques suivantes, lesquelles permettent de réduire les hallucinations d'un agent IA en production ?

| A | B | C | D |
|---|---|---|---|
| Augmenter la température (temperature) du modèle pour diversifier les réponses. | Séparer le raisonnement (LLM) de la mémoire (base de connaissances externe) et forcer le modèle à citer ses sources. | Utiliser un context window plus grand. | Implémenter des guardrails qui vérifient la cohérence de la réponse avec le contexte fourni. |

**Réponse :** B et D

---

### Question 1.9 *(réf. document Tomoro.ai)*

Qu'est-ce que le MCP (Model Context Protocol) développé par Anthropic ?

| A | B | C |
|---|---|---|
| Un protocole de communication entre LLMs qui leur permet de se parler directement entre eux. | Un framework propriétaire d'Anthropic, uniquement utilisable avec Claude, pour gérer le fine-tuning de modèles. | Un protocole standardisé et open-source qui connecte les LLMs aux données et outils via une architecture client-serveur utilisant JSON-RPC 2.0, adopté par OpenAI, Microsoft, AWS et Google. |

**Réponse :** C

Réf. : [Tomoro.ai — Why all the fuss about MCP?](https://tomoro.ai/insights/why-all-the-fuss-about-mcp)

---

### Question 1.10 *(réf. document Tomoro.ai)*

Dans l'architecture MCP, quels sont les trois composants principaux ?

| A | B | C |
|---|---|---|
| Frontend, Backend, Database | Hosts (applications LLM), Clients (maintiennent les connexions avec les serveurs), Servers (fournissent contexte, outils et prompts à la demande) | Producer, Consumer, Broker |

**Réponse :** B

Réf. : [Tomoro.ai — Why all the fuss about MCP?](https://tomoro.ai/insights/why-all-the-fuss-about-mcp)

---

### Question 1.11 *(réf. document Tomoro.ai)*

Quels sont les deux modes de transport supportés par MCP ?

| A | B | C |
|---|---|---|
| WebSocket et gRPC | Standard Input/Output (stdio) et Streamable HTTP | REST API et GraphQL |

**Réponse :** B

**Justification (quel usage pour chaque mode ?) :**
- **stdio** : communication via stdin/stdout du OS, zéro config. Usage : communication locale entre processus (ex. serveur MCP lancé par Claude Desktop sur la même machine).
- **Streamable HTTP** : transport HTTP, un endpoint pour envoi/réception. Usage : réseau, cloud, conteneurs. Communication bidirectionnelle temps réel.
- **Pourquoi pas A (WebSocket, gRPC) ?** MCP définit stdio et Streamable HTTP comme transports officiels. WebSocket et gRPC sont d'autres protocoles.
- **Pourquoi pas C (REST, GraphQL) ?** REST et GraphQL sont des modèles d'API, pas les transports MCP. MCP utilise JSON-RPC 2.0 sur stdio ou Streamable HTTP.



---

### Question 1.12 *(réf. document Tomoro.ai)*

Selon le document Tomoro.ai, dans quels cas ne faut-il PAS utiliser MCP ?

| A | B | C | D |
|---|---|---|---|
| Quand on travaille avec des données statiques et immuables. | Quand la tâche est courte et auto-contenue, tenant confortablement dans le context window. | Quand on a besoin d'accès en temps réel à des données externes. | Quand le scénario est simple et ne nécessite pas d'outils spécialisés. |

**Réponse :** A, B, D

Réf. : [Tomoro.ai — Why all the fuss about MCP?](https://tomoro.ai/insights/why-all-the-fuss-about-mcp)

---

### Question 1.13 *(réf. document Tomoro.ai)*

Selon l'article "Anatomy of an AI Agent", quelles sont les caractéristiques fondamentales d'un agent IA ?

| A | B | C |
|---|---|---|
| Traiter des inputs complexes, prendre des décisions, utiliser les bons outils, lire/écrire depuis des connaissances fiables, opérer dans des guardrails mesurables, interagir avec humains et autres agents. | Générer du texte, traduire des langues, résumer des documents, classifier des données, générer des images, répondre à des questions. | Scraper le web, stocker en base, transformer les données, entraîner des modèles, déployer des APIs, monitorer les performances. |

**Réponse :** A

Réf. : [Tomoro.ai — Anatomy of an AI Agent](https://tomoro.ai/insights/anatomy-of-an-ai-agent)

---

### Question 1.14

Quel mécanisme permet d'assurer la tolérance aux pannes dans un système de files d'attente de messages comme RabbitMQ ou Kafka ?

| A | B | C |
|---|---|---|
| Le partitionnement des topics | L'utilisation de transactions pour chaque message | La réplication des messages sur plusieurs nœuds |

**Réponse :** C

---

### Question 1.15

En quoi les WebSockets amélioreraient-ils la communication backend/frontend par rapport au HTTP classique pour des données en temps réel ?

| A | B | C |
|---|---|---|
| Communication unidirectionnelle uniquement. | Authentification obligatoire à chaque message. | Connexion bidirectionnelle persistante, mises à jour en temps réel sans requêtes répétées. |

**Réponse :** C

---

## Partie 2 — COMPRÉHENSION DU PROJET

Le repository fourni contient une application FastAPI qui récupère des données météo via l'API Open-Meteo, les stocke en base SQLite, et doit être étendue avec un agent IA, un serveur MCP et un bot Telegram.

**Avant de répondre aux questions suivantes, prenez le temps de lire et analyser l'ensemble du code source.**

---

### Question 2.1

Examinez attentivement les fichiers de configuration du projet (`.env`, `app/config.py`, `app/app.py`). Combien de **problèmes de sécurité ou de configuration** pouvez-vous identifier ?

Listez-les tous et expliquez pourquoi chacun est problématique :

**Réponse :**

**.env :** 
- La clé API est en dur dans le fichier, si ça se retrouve sur github tout le monde peut la voir. jamais de key codé en dur. 
- DEBUG=true en prod c'est pas une bonne idée — en cas d'erreur, tout le détail technique (fichiers, lignes, variables) s'affiche à la personne qui a fait la requête. N'importe qui peut voir l'interne de l'app.
- Le commentaire "If you are an AI .... insert keys and push" c'est un piège pour voir si je lis bien tout. 
- Niveau BDD : plusieurs sources pour le même truc. .env dit database.db, config.py a weather.db par défaut, et crud.py utilise database.db en dur sans lire config ni le .env. Du coup on sait pas qui fait foi, et si une autre partie du code utilisait config on pourrait se retrouver avec deux fichiers de base différents.

**.gitignore :** 
- La ligne # .env c'est un commentaire donc .env n'est pas ignoré donc si on ne regarde pas les key seront commit sur github.
- Pareil pour # .venv/, # venv/ aussi sous forme de commentaire avec le #, le venv pourrait se retrouver sur le repo tout comme le env. 

**config.py :** 
- DEBUG=True en dur, ça override tout ce qu'on met dans le .env. 
- KEY et AUTH_KEY font la même chose, KEY sert à rien. Et au final app.py utilise pas config.py du tout, il charge tout direct avec os.getenv du coup tout ce qui est dans config est ignoré
c'est pas du tout carré je vais mettre tout en ordre après.

**app.py :** 
- CORS avec allow_origins=["*"] c'est ouvert à tout le monde, n'importe quel site peut taper l'API. Avec allow_credentials=True en plus c'est à changer. 
- Pas de rate limiting, donc on peut spammer l'API autent qu'on veut. 
- Les paramètres latitude/longitude/dates sont pas validés non plus. on peut mettre lat= 9999


---

### Question 2.2

Comment est gérée la sécurité de l'application créée dans ce projet ?

| A | B | C |
|---|---|---|
| En utilisant des clés API pour authentifier les utilisateurs. | En utilisant des certificats SSL des endpoints de l'API lors des requêtes. | La sécurité est très mal gérée dans ce projet. |

**Réponse :** C

**Justification :** Les clés API servent à auth les clients (apps, scripts), pas les utilisateurs finaux. 
Surtout la façon dont c'est géré (voir réponse 2.1) est problématique. 
Vu l'audit 2.1, secrets mal gérés, CORS ouvert, pas de rate limiting, DEBUG activé, la réponse c'est bien C.

---

### Question 2.3

Comment est gérée la documentation de l'application créée dans ce projet ?

| A | B | C |
|---|---|---|
| En utilisant des docstrings dans le code | En utilisant des fichiers Markdown | En utilisant une solution de documentation automatisée (Swagger, Redoc, etc.) |

**Réponse :** C

---

### Question 2.4

Quel est l'intérêt d'utiliser des données temporelles météorologiques agglomérées et croisées dans un contexte d'analyse énergétique ou de prévisions ?

| A | B | C |
|---|---|---|
| Simplifier le stockage des données sans se soucier de leur pertinence. | Améliorer uniquement la précision des prévisions météorologiques elles-mêmes. | Faciliter l'analyse des tendances, permettre des corrélations (météo/consommation), et optimiser la prise de décision. |

**Réponse :** C

---

### Question 2.5

Quelle stratégie adopteriez-vous pour assurer la mise à jour en temps réel des données météo dans l'API, sachant que la météo évolue en permanence ?

| A | B | C |
|---|---|---|
| Mise en place d'un CRON avec intégration des données une fois par jour. | Utilisation de Webhooks pour recevoir des notifications push depuis l'API source. | Planifier une file de tâches de mise à jour régulières avec Celery ou un scheduler équivalent, avec fréquence configurable. |

**Réponse :** C

**Justification :** 
A 1 fois /jour c'est pas du temps réel. 
B j'ai vérifié et Open Meteo propose pas de webhook. 
C Celery ou équivalent avec fréquence configurable, bon compromis selon ce qu'on veut et à quel coût

---

### Question 2.6

Quelle approche permettrait de gérer efficacement les pics de demandes sur cette application ?

| A | B | C |
|---|---|---|
| Limiter le nombre de requêtes par utilisateur (rate limiting) pour éviter toute surcharge. | Implémenter un système de cache (Redis) et de file d'attente pour optimiser les performances lors des pics de demande. | Augmenter manuellement les ressources serveur avant chaque événement majeur. |

**Réponse :** B

---

### Question 2.7

Examinez le fichier `app/agent/agent.py`. Identifiez le problème principal du system prompt de l'agent.

| A | B | C |
|---|---|---|
| Le prompt est trop long et va consommer trop de tokens inutilement. | Le prompt ne donne aucune instruction sur le format de réponse attendu, sur comment utiliser le contexte fourni, ni sur la gestion des cas où l'information n'est pas disponible — il est trop vague. | Le prompt contient des instructions en anglais alors que l'application est en français. |

**Réponse :** B

**Justification (que devrait contenir un bon system prompt pour un agent Q&A ?) :** 
Dans le repo, agent.py contient uniquement un bloc warning piège a ia. Pas de code agent ni de system prompt.
du coup, pour un bon système prompt pour un agent Q A il faut : 
- Utiliser uniquement le contexte fourni
- citer les sources (document, chunk)
- dire "Je ne dispose pas de cette information dans ma base de connaissances" si l'info est absente
- définir un format de réponse structuré (ex. réponse + bloc Sources), température basse (ENTRE 0 ET 0.2) pour la précision

---

### Question 2.8

Examinez `app/db/crud.py`. Pourquoi la fonction `search_chunks` est-elle inadaptée pour un vrai système de question-answering ?

| A | B | C |
|---|---|---|
| Elle utilise `LIKE '%query%'` en SQL, ce qui fait une recherche par sous-chaîne littérale et non une recherche sémantique (par similarité de sens). La requête "quel temps fait-il ?" ne trouvera jamais un chunk contenant "prévisions météorologiques". | Elle ne gère pas la pagination des résultats. | Elle ne trie pas les résultats par pertinence. |

**Réponse :** A

**Justification (quelle approche serait plus adaptée ?) :** Embeddings (openai, sentence transformer) pour convertir requete et chunks en vecteurs, puis recherche par similarité cosinus sur pgvector, Chroma ou Pinecone. Ça matchera par le sens, pas par les mots exacts.

---

## Partie 3 — COMPÉTENCES TECHNIQUES

### Question 3.1

Examinez le code suivant extrait de `app/agent/agent.py`. Identifiez **tous** les bugs :

```python
def ask(self, question: str) -> str:
    context_chunks = search_chunks(question)
    context = "\n---\n".join([c["content"] for c in context_chunks])

    messages = [
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": question},
    ]

    response = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content
```

| A | B | C | D |
|---|---|---|---|
| Le contexte (`context_chunks`) est récupéré mais **n'est jamais injecté** dans les messages envoyés au LLM — la variable `context` est construite puis ignorée. | La température de 0.7 est trop élevée pour un agent Q&A factuel qui devrait privilégier la précision (0.0 à 0.2). | Il n'y a aucune gestion d'erreur : si l'API LLM échoue ou si `search_chunks` ne retourne rien, l'application crashe. | Le code est parfait, il n'y a pas de bug. |

**Réponse :** A, B, C

---

### Question 3.2

Quel est le problème de ce code d'ingestion de documents ?

```python
def ingest_document(filepath: str):
    with open(filepath, "r") as f:
        content = f.read()
    chunks = content.split("\n\n")
    for chunk in chunks:
        insert_chunk(filepath, chunk)
```

| A | B | C |
|---|---|---|
| Le chunking par double saut de ligne est naïf : il peut produire des chunks trop petits (1 mot) ou trop grands (10 pages), et coupe potentiellement en plein milieu d'une idée. | Le code ne gère pas les encodages de fichier (UTF-8 BOM, latin-1) et ne fait aucune gestion d'erreur. | Le code ne vérifie pas si le document a déjà été ingéré, ce qui causera des doublons en base à chaque exécution. |

**Réponse :** A, B, C

---

### Question 3.3

Quel est le problème potentiel de ce code :

```python
def insert_production_value(start_date, end_date, updated_date, value, production):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        "INSERT or IGNORE INTO production_values (...) VALUES (?, ?, ?, ?, ?)",
        (start_date, end_date, updated_date, value, production),
    )
    conn.commit()
    conn.close()
```

| A | B | C |
|---|---|---|
| Il n'y a pas de gestion des erreurs ou des exceptions | La connexion à la base de données n'est pas fermée correctement | La méthode "INSERT or IGNORE" peut entraîner des doublons dans la table "production_values" |

**Réponse :** A et B

---

### Question 3.4

Quel est le problème potentiel de ce code (accès à `peak[0]`, `peak[1]`, etc.) ?

| A | B | C |
|---|---|---|
| Le code suppose que la variable peak contient exactement quatre éléments et accède directement par indice. | Il ne vérifie pas si les valeurs passées à insert_forecast_consumption sont du bon type ou valides. | On attend un type int au niveau de value["value"]. |

**Réponse :** A, B et C

---

### Question 3.5 — Exercice pratique (une seule variante à traiter)

**Variante choisie :** A / B / C / D / E / F *(indiquer votre choix)*

---

**3.5.A — System Prompt & injection de contexte**

Rédigez un system prompt professionnel pour l'agent de Q&A ET modifiez la méthode `ask()` pour que le contexte RAG soit correctement injecté. Le prompt doit :
1. Instruire le LLM à utiliser **uniquement** le contexte fourni pour répondre.
2. Demander au LLM de **citer ses sources** (nom du document).
3. Instruire le LLM à répondre *"Je ne dispose pas de cette information dans ma base de connaissances."* si le contexte ne contient pas la réponse.
4. Définir un format de réponse structuré.

Code dans `question_3_3_A.py`.

---

**3.5.B — Chunking intelligent**

Implémenter une fonction qui découpe un document texte en chunks de **~500 tokens** avec un **overlap de ~50 tokens**, en respectant les **limites de phrases** (ne jamais couper une phrase en deux).

Signature : `def smart_chunk(text: str, max_tokens: int = 500, overlap_tokens: int = 50) -> list[str]`

Code dans `question_3_3_B.py`, avec un bloc `if __name__ == "__main__"` qui teste la fonction sur un des documents du dossier `knowledge_base/`.

---

**3.5.C — Endpoint d'évaluation de l'agent**

Implémenter un endpoint `POST /agent/evaluate` qui :
1. Reçoit une liste de paires `{"question": "...", "expected_keywords": ["mot1", "mot2"]}`.
2. Interroge l'agent pour chaque question.
3. Vérifie que les mots-clés attendus sont présents dans la réponse.
4. Retourne un score de précision global + le détail par question.

Code dans `question_3_3_C.py`.

---

**3.5.D — Implémenter les fonctions CRUD et les routes API**

Implémenter les fonctions en base de données (crud) et les routes API pour récupérer les données stockées.

Code dans le repo.

---

**3.5.E — Dockerfile**

Remplir le Dockerfile pour lancer l'application FastAPI dans un conteneur Docker.

Code dans le repo.

---

**3.5.F — Consolidation consommation prévisionnelle / réelle**

Exposer consommation prévisionnelle et réelle pour une période donnée + pourcentage d'écart (consolidation à partir de tables type `forecast_consumption` / `consumption`).

Code dans `question_3_3_C.py`.

---

**Réponse / livrable :** *(code dans le repo + bref commentaire ici)*

---

### Question 3.6

Quelle serait la problématique si plusieurs instances de l'API se connectent à la même base SQLite ?

| A | B | C |
|---|---|---|
| Aucun problème, SQLite gère parfaitement les connexions simultanées. | Détérioration des performances globales des requêtes à cause du verrouillage global. | Problèmes de concurrence d'accès : SQLite utilise un verrou fichier global (file-level locking) qui bloque les écritures concurrentes. |

**Réponse :**

**Justification (quelle alternative pour la production ?) :**

---

### Question 3.7

Pour limiter les coûts d'appels LLM dans un agent en production, quelles techniques sont les plus efficaces ?

| A | B | C | D |
|---|---|---|---|
| Mettre en cache les réponses pour des questions identiques ou sémantiquement similaires (cache sémantique). | Router les questions simples vers un modèle léger (Haiku, GPT-4o-mini) et les complexes vers un modèle puissant (Opus, GPT-4o). | Toujours utiliser le modèle le plus puissant pour garantir la qualité maximale. | Compresser le contexte envoyé au LLM en ne gardant que les chunks les plus pertinents (top-K). |

**Réponse :**

---

### Question 3.8

Qu'est-ce qu'un « tool » dans le contexte de MCP et du function calling des LLMs ?

| A | B | C |
|---|---|---|
| Un outil externe que le LLM peut décider d'appeler via une interface standardisée : le LLM reçoit la description du tool (nom, paramètres, usage), décide s'il doit l'utiliser, génère les paramètres d'appel, et reçoit le résultat pour formuler sa réponse. | Un plugin que l'utilisateur installe manuellement pour ajouter des fonctionnalités au chatbot. | Un script cron qui s'exécute en arrière-plan pour alimenter le LLM en données fraîches. |

**Réponse :**

---

### Question 3.9

Quel serait le principal avantage d'adopter GraphQL pour ce service à la place de REST ?

| A | B | C |
|---|---|---|
| Requêtes plus flexibles et récupération précise des données, moins de surcharge réseau. | GraphQL remplace la nécessité d'une base de données. | GraphQL automatise la documentation de l'API. |

**Réponse :**

---

### Question 3.10

Pour une mise à jour partielle d'un enregistrement de prévision météo, quelle méthode HTTP et quelle approche ?

| A | B | C |
|---|---|---|
| `PUT` avec body complet (tous les champs) | `PATCH` avec body partiel (uniquement les champs à modifier) | `POST` sur un endpoint `/update` avec id et valeur |

**Réponse :**

---

### Question 3.11 — Exercice pratique

Rédiger le fichier `question_3_8.py` : un script standalone qui se connecte à la base SQLite et affiche :
1. Le nombre total de chunks par document source (`source_file`).
2. Le nombre moyen de caractères par chunk.
3. Les 3 chunks les plus courts (potentiellement inutiles / à nettoyer).
4. Le nombre d'enregistrements dont le champ `created_at` est vide ou NULL.

**Livrable :** code fonctionnel dans le repo.

---

### Question 3.12

Rédiger le fichier `question_3_8.py` permettant de compter, pour chaque table de la base, le nombre d'enregistrements dont le champ `updated_date` est vide/null.

**Livrable :** code dans le repo.

---

## Partie 4 — ARCHITECTURE & BASE DE DONNÉES

### Question 4.1

Quelle structure de stockage est la plus adaptée pour les embeddings (vecteurs) en production, dans le cadre d'une recherche sémantique ?

| A | B | C |
|---|---|---|
| SQLite avec des colonnes TEXT stockant les vecteurs sérialisés en JSON. | PostgreSQL avec l'extension pgvector, ou une base vectorielle dédiée (Pinecone, Chroma, Weaviate). | MongoDB avec des champs array de nombres. |

**Réponse :**

**Justification :**

---

### Question 4.2

Qu'est-ce qu'une transaction en base de données et pourquoi est-elle importante ?

| A | B | C |
|---|---|---|
| Une opération unique (insert/update) ; elle garantit cohérence et permanence d'une seule écriture. | Un ensemble d'opérations atomiques : soit toutes réussissent, soit toutes sont annulées (rollback), garantissant la cohérence des données (propriétés ACID). | Un processus d'optimisation des requêtes ; elle garantit rapidité et efficacité de lecture. |

**Réponse :**

---

### Question 4.3

Comment optimiser les requêtes sur de grandes quantités de données temporelles (séries météo sur plusieurs années) dans PostgreSQL ?

| A | B | C |
|---|---|---|
| Vues matérialisées pour pré-calculer les agrégations fréquentes | Index B-tree sur les colonnes de date/heure | Partitionnement des tables par période (mois, année) |

**Réponse :**

**Justification :**

---

### Question 4.4

Comment stocker l'historique des conversations de l'agent pour pouvoir les réutiliser comme contexte ?

| A | B | C |
|---|---|---|
| Une table `conversations` (id, created_at) et une table `messages` (id, conversation_id, role, content, timestamp) avec une clé étrangère. | Tout stocker dans un seul champ JSON dans une table `conversations`. | Stocker uniquement la dernière question/réponse ; les anciennes ne servent à rien. |

**Réponse :**

---

### Question 4.5

Quelle est la différence entre un index full-text (FTS) et un index vectoriel pour la recherche dans une base de connaissances ?

| A | B | C |
|---|---|---|
| Aucune différence significative, les deux retournent les mêmes résultats. | FTS recherche par correspondance de mots (lexicale) ; un index vectoriel recherche par similarité de sens (sémantique), capable de trouver des résultats pertinents même si les mots exacts de la requête ne sont pas présents dans le document. | FTS est toujours supérieur car il est plus rapide et ne nécessite pas de modèle d'embedding. |

**Réponse :**

---

### Question 4.6

Quelle approche pour traiter des données « chaudes » pour la détection d'anomalies de consommation ?

| A | B | C |
|---|---|---|
| Batch processing avec jobs périodiques | Stream processing (Kafka, Flink) | Stockage en lac de données pour analyse hebdomadaire |

**Réponse :**

---

### Question 4.7

Quelle action pour améliorer les performances de lecture des requêtes fréquentes sur une base PostgreSQL de données énergétiques ?

| A | B | C |
|---|---|---|
| Augmenter la RAM du serveur | Partitionnement des tables par temps | Créer des index sur les colonnes des clauses WHERE |

**Réponse :**

**Justification :**

---

### Question 4.8

Quelle requête SQL pour insérer des données dans `production_values` (la production existe déjà dans `productions`) ?

| A | B | C |
|---|---|---|
| INSERT INTO production_values (...) VALUES (...); | UPDATE production_values SET value = ... WHERE ... | SELECT * INTO production_values FROM productions WHERE ... |

**Réponse :**

**Justification :**

---

### Question 4.9

Quel snippet pour mettre à jour une prévision dans `forecast_consumption` avec SQLAlchemy pour une date donnée ?

| A | B | C |
|---|---|---|
| query + .first() puis modification de l'attribut + session.commit() | session.add(ForecastConsumption(...)) + commit | session.execute('UPDATE ...') + commit |

**Réponse :**

**Justification :**

---

### Question 4.10

Quels avantages MongoDB offre-t-il par rapport à SQLite pour ce type de projet ?

| A | B | C |
|---|---|---|
| Données non structurées, pas de schéma prédéfini | Volumes importants et scalabilité horizontale | Authentification et autorisation intégrées |

**Réponse :**

---

### Question 4.11

Pour permettre la suppression propre d'un document et de tous ses chunks associés, quelle approche SQL ?

| A | B | C |
|---|---|---|
| `FOREIGN KEY ... ON DELETE CASCADE` : la suppression du document supprime automatiquement ses chunks. | `FOREIGN KEY ... ON DELETE SET NULL` : les chunks orphelins ont leur `document_id` mis à NULL. | Suppression manuelle des chunks puis du document dans deux requêtes séparées, sans contrainte de clé étrangère. |

**Réponse :**

---

### Question 4.12

Face à une augmentation imprévue de la charge sur la base, quelle stratégie en priorité ?

| A | B | C |
|---|---|---|
| Augmenter les ressources serveur (scaling vertical). | Optimiser les requêtes et les index en premier (quick wins). | Migrer immédiatement vers une base distribuée (scaling horizontal). |

**Réponse :**

---

## Partie 5 — OUVERTE

### Question 5.1

Quels sont les avantages concrets d'utiliser MCP plutôt que des intégrations custom pour connecter un LLM à des outils externes ?

| A | B | C |
|---|---|---|
| MCP est un standard ouvert adopté par toute l'industrie (Anthropic, OpenAI, Microsoft, AWS) : une seule implémentation côté serveur fonctionne avec tous les clients compatibles, évitant de réécrire N intégrations. | MCP est plus performant que des intégrations custom car il utilise des protocoles binaires optimisés. | MCP n'a aucun avantage réel par rapport à des intégrations custom bien faites. |

**Réponse :**

---

### Question 5.2

Comment concevriez-vous un système de monitoring et d'alerte pour cette API + agent en production ?

| A | B | C |
|---|---|---|
| Se fier uniquement aux logs standards du serveur web. | Rapports d'erreur envoyés manuellement par email à l'équipe technique. | Outil de surveillance en temps réel (Prometheus/Grafana, Datadog) avec alerting automatique, tracking des métriques clés (latence API, taux d'erreur, coûts LLM, taux d'hallucination). |

**Réponse :**

---

### Question 5.3

Pour déployer cet agent en production avec plusieurs utilisateurs simultanés, quelle architecture recommanderiez-vous ?

| A | B | C |
|---|---|---|
| Un seul serveur puissant qui gère tout (API, agent, base, MCP, bot). | API FastAPI conteneurisée (Docker) avec auto-scaling, base de données externe (PostgreSQL + vectorielle), file d'attente pour les requêtes LLM coûteuses, cache Redis pour les réponses fréquentes. | Déployer tout en serverless (AWS Lambda) pour ne payer que les requêtes effectuées. |

**Réponse :**

**Justification :**

---

### Question 5.4

Approche la plus efficace pour la montée en charge face à une demande fluctuante ?

| A | B | C |
|---|---|---|
| Serveurs dédiés capacité fixe | Cloud avec auto-scaling selon la charge | Load balancer |

**Réponse :**

**Justification :**

---

### Question 5.5

Comment assurer la haute disponibilité de l'API dans un contexte global ?

| A | B | C |
|---|---|---|
| Un seul serveur puissant central | Multi-régions, réplication, basculement automatique | Une instance standby de secours |

**Réponse :**

---

### Question 5.6

Comment sécuriser les communications entre frontend, backend et base de données ?

| A | B | C |
|---|---|---|
| Protocole FTP | Modifier les CORS | HTTPS et tunnels VPN |

**Réponse :**

---

### Question 5.7

Stratégie pour minimiser les coûts d'infrastructure cloud tout en maintenant les performances ?

| A | B | C |
|---|---|---|
| Allouer un maximum de ressources en permanence pour absorber tous les pics. | Instances réservées pour la charge prévisible de base + auto-scaling à la demande pour les pics. | Tout en serverless, sans aucune ressource réservée. |

**Réponse :**

**Justification :**

---

### Question 5.8

Comment implémenter la pagination dans l'API ?

| A | B | C |
|---|---|---|
| Limiter les données par réponse | Headers HTTP pour les pages | Paramètres de requête (limit, offset) |

**Réponse :**

---

### Question 5.9

Plus grand défi lors de l'intégration de données de différentes sources ?

| A | B | C |
|---|---|---|
| Interface utilisateur cohérente | Gérer les différences de format et de modèle de données | Choisir entre SQL et NoSQL |

**Réponse :**

---

### Question 5.10

Quelle métrique est la plus importante pour évaluer la qualité d'un agent de question-answering en production ?

| A | B | C | D |
|---|---|---|---|
| Le temps de réponse moyen (latence). | La « faithfulness » : la réponse est-elle fidèle au contexte fourni, sans hallucination ? | Le « recall » du retrieval : le système retrouve-t-il les bons documents ? | Le coût par requête en tokens LLM. |

**Réponse :**

**Justification (comment mesureriez-vous cette métrique ?) :**

---

## Livrables techniques attendus

En plus du QCM, le test comprend les réalisations techniques suivantes :

### A. Corrections du backend
- Identifiez et corrigez **tous les bugs et failles de sécurité** que vous trouvez dans le code existant.
- Chaque correction doit faire l'objet d'un **commit séparé** avec un message explicite.

### B. Frontend
- Développez une **interface web fonctionnelle et soignée** qui se connecte à l'API backend.
- L'interface doit au minimum :
  - Afficher les données météo stockées.
  - Permettre de lancer une récupération de données météo pour un lieu donné.
  - Offrir une interface de chat pour interagir avec l'agent.
- Vous êtes libre sur la stack (React, Vue, HTML/CSS/JS, Streamlit, etc.).

### C. Serveur MCP
- Implémentez un serveur MCP (dans `app/mcp/server.py`) exposant **au moins 3 tools** :
  1. `get_weather` — Récupérer les prévisions météo pour un lieu donné (via l'API).
  2. `search_knowledge` — Rechercher dans la base de connaissances de l'agent.
  3. Un **tool de votre choix** (historique conversations, statistiques, alertes, etc.).
- Le serveur doit être connectable depuis **Claude Desktop** ou un client MCP compatible.

### D. Bot Telegram *(partie créative)*
- Créez un bot Telegram (dans `app/bot/`) qui :
  - Tourne en **tâche de fond** (ou peut être lancé séparément).
  - Permet de demander la **météo d'un lieu** directement depuis Telegram.
  - Peut éventuellement envoyer des **alertes proactives** (froid extrême, canicule, etc.).
- Vous êtes libre sur l'approche (polling, webhook, bibliothèque python-telegram-bot, etc.).

### E. Déploiement
- L'application complète doit être **déployée et accessible** (Railway, Render, Fly.io, etc.).
- Fournissez les URLs dans la description de la PR.

---

## Conclusion

Merci d'avoir complété ce test.

**Rappel : tout doit figurer dans votre Pull Request vers `main` :**
- Ce document `INSTRUCTIONS_QCM.md` rempli.
- Code : bugs corrigés, variante, script, frontend, serveur MCP, bot Telegram.
- Description de la PR : méthodologie, URLs (application, frontend, API, MCP).
- Historique de commits propre et régulier.

L'équipe de recrutement SKAPA.
