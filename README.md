1. Contexte et objectif du projet
Ce travail pratique consiste à concevoir et déployer une application complète composée de trois services :

une API REST développée en Python/FastAPI ;

une base de données PostgreSQL pour stocker les données ;

un front end web statique qui interroge l’API et affiche les informations à l’utilisateur.

2. Architecture mise en place
L’architecture finale se compose de trois conteneurs :

Service db
Image : postgres:16.

Rôle : héberger la base de données de l’application.

Initialisation : script init.sql monté dans /docker-entrypoint-initdb.d/ pour créer la table et insérer deux enregistrements d’exemple.

Persistance : volume Docker pour conserver les données entre les redémarrages.

Service api
Framework : FastAPI.

Code : paquet app contenant main.py, db.py, models.py, crud.py.

Endpoints :

GET /status → retourne {"status": "OK"}, utilisé comme sonde de santé.

GET /items → retourne la liste typée des éléments présents en base.

Connexion base : via SQLAlchemy et une URL de connexion lue dans la variable d’environnement DATABASE_URL, qui pointe vers le service db (hostname Docker Compose).

Service front
Contenu : page index.html + script script.js.

Fonction : appeler GET /status et GET /items de l’API et afficher le statut de l’API ainsi que la liste des éléments.

Hébergement : image Nginx servant les fichiers statiques copiés dans /usr/share/nginx/html.

Les trois services sont décrits dans un même fichier docker-compose.yml, ce qui permet de démarrer l’ensemble avec une seule commande.

3. Conteneurisation et bonnes pratiques
3.1 API (Dockerfile multi‑étapes)
Pour l’API, un Dockerfile multi‑étapes a été utilisé :

Étape builder basée sur python:3.11-slim pour installer les dépendances et générer des wheels.

Étape finale également basée sur python:3.11-slim, qui :

crée un utilisateur système et un groupe (appuser, appgroup) ;

installe les dépendances sans les outils de build ;

copie uniquement le code applicatif (app/) ;

démarre l’application avec uvicorn app.main:app --host 0.0.0.0 --port 8000.

Ce découpage permet d’obtenir une image plus légère et d’exécuter le processus en utilisateur non root, conformément aux consignes du TD.

Un fichier .dockerignore a été ajouté pour exclure les fichiers inutiles (cache Python, etc.) du contexte de build et réduire la taille de l’image.

3.2 Base de données
La base PostgreSQL est initialisée automatiquement au premier démarrage grâce au script init.sql monté dans le répertoire d’initialisation de l’image officielle. Ce script :

crée la table applicative ;

insère deux lignes d’exemple, qui sont ensuite retournées par le endpoint /items.

Un volume nommé assure la persistance des données entre les redémarrages.

3.3 Front end
Le front est un site statique simple :

index.html contient la structure (zones pour le statut et la liste des items) ;

script.js appelle l’API côté client avec fetch, puis met à jour le DOM.

Ces fichiers sont servis par Nginx via un Dockerfile qui copie le HTML et le JS dans le répertoire statique par défaut.

4. Orchestration, configuration et commandes clés
L’orchestration est assurée par docker-compose.yml, avec trois services : db, api, front. Les principaux éléments sont :

Réseau et dépendances :

depends_on permet de démarrer la base avant l’API, puis le front après l’API.

Ports exposés :

API : port 8000 exposé vers localhost:8000.

Front : port 80 du conteneur exposé vers localhost:8080.

DB : port 5432 exposé si besoin de connexion externe.

Variables d’environnement :

utilisation d’un fichier .env à la racine du projet qui définit POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB et DATABASE_URL ;

ces variables sont injectées dans les services via les sections environment de Compose.

Les principales commandes utilisées pour construire et déployer la stack sont :

Initialisation / build et lancement :

docker compose up --build

Lancement en arrière‑plan :

docker compose up -d

Arrêt et nettoyage :

docker compose down

Un script automatisé peut regrouper ces commandes (vérification de la configuration avec docker compose config, build, puis docker compose up -d).

5. Problèmes rencontrés et solutions apportées
Plusieurs difficultés ont été rencontrées et résolues :

Erreur de connexion à la base au démarrage de l’API
Symptôme : OperationalError: connection to server at "db" failed: Connection refused, l’API tentait de se connecter avant que Postgres soit prêt.

Solution : ajout d’une fonction de création du moteur SQLAlchemy avec retry dans db.py, qui tente la connexion plusieurs fois avec un délai entre chaque essai. L’API ne se lance réellement que lorsque la base accepte les connexions.

Erreur SQLAlchemy lors du test de connexion
Symptôme : ObjectNotExecutableError: Not an executable object: 'SELECT 1' avec SQLAlchemy 2.x, due à l’appel direct de conn.execute("SELECT 1").

Solution : utilisation de text("SELECT 1") au lieu d’une simple chaîne afin d’être compatible avec l’API 2.x de SQLAlchemy.

Contenu de index.html vide dans l’image front
Symptôme : page blanche sur http://localhost:8080 alors que le code HTML était correct sur le poste.

Cause : cache de build Docker ou mauvais contexte de copie, le fichier local n’était pas bien recopié dans /usr/share/nginx/html.

Solution : vérification du contenu dans le conteneur avec
docker exec ... cat /usr/share/nginx/html/index.html,
reconstruction complète de l’image avec --no-cache et correction du Dockerfile pour copier les bons fichiers.

Ces difficultés et leurs résolutions montrent la compréhension des interactions entre Docker, Docker Compose, la base de données et le code applicatif.

6. Pistes d’amélioration
Plusieurs améliorations possibles ont été identifiées pour aller au‑delà des exigences minimales du TD :

Ajouter des healthchecks explicites dans docker-compose.yml pour la base (via pg_isready) et pour l’API (via un curl sur /status) afin que Compose connaisse l’état de santé des services.

Mettre en place un vrai Dockerfile multi‑étapes pour le front dans le cas d’un framework avec phase de build (React, Vue, etc.).

Renforcer la sécurité des services via les options Compose (read_only, cap_drop, etc.) et ajouter un scan d’images (docker scout ou équivalent).

Automatiser complètement la chaîne via un script de déploiement ou un pipeline CI/CD qui construit, teste et pousse les images vers un registre avant de lancer docker compose up -d sur l’environnement cible.
