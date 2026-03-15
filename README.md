# TaskBoard

Plateforme de gestion de tâches collaborative en temps réel, construite avec FastAPI, Vue 3 et PostgreSQL.

> **[CAPTURE : page d'accueil du dashboard avec plusieurs projets affichés]**

---

## Aperçu

TaskBoard permet à des équipes de gérer leurs projets sous forme de tableaux Kanban. Les membres voient les modifications en temps réel sans recharger la page, grâce à une connexion WebSocket persistante.

Le projet couvre l'ensemble du cycle d'une application en production : authentification sécurisée, contrôle d'accès par rôles, API REST documentée, communication temps réel, base de données relationnelle, conteneurisation Docker et pipeline CI/CD automatisé.

---

## Captures d'écran

### Connexion
> **[CAPTURE : page de login]**

### Tableau de bord
> **[CAPTURE : liste des projets sur le dashboard]**

### Tableau Kanban
> **[CAPTURE : vue Kanban d'un projet avec des tâches dans plusieurs colonnes]**

### Gestion des membres
> **[CAPTURE : onglet Membres avec la liste et le formulaire d'invitation]**

### Création de tâche
> **[CAPTURE : modal de création de tâche ouvert avec les champs remplis]**

### Temps réel
> **[CAPTURE : deux fenêtres côte à côte montrant une tâche mise à jour en direct]**

---

## Fonctionnalités

- **Authentification JWT** — inscription, connexion, refresh token avec rotation automatique
- **Gestion de projets** — création, modification, suppression, liste personnelle par utilisateur
- **Contrôle d'accès par rôle** — trois rôles par projet : Admin, Membre, Lecteur
- **Gestion des membres** — invitation par nom d'utilisateur, changement de rôle, retrait
- **Tableau Kanban** — cinq colonnes : Backlog, À faire, En cours, En revue, Terminé
- **Priorités et assignation** — quatre niveaux de priorité, assignation de tâches aux membres
- **Temps réel** — toutes les modifications de tâches sont propagées instantanément via WebSocket
- **Pipeline CI/CD** — tests automatisés, build Docker et déploiement déclenchés à chaque push sur `main`

---

## Stack technique

| Couche | Technologie |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic |
| Base de données | PostgreSQL 16 |
| Cache / temps réel | Redis 7 (pub/sub WebSocket) |
| Frontend | Vue 3, TypeScript, Vite, Pinia, Vue Router |
| Conteneurisation | Docker, Docker Compose |
| CI/CD | GitHub Actions → Render |

---

## Architecture
```
┌─────────────────┐        HTTP / WebSocket        ┌─────────────────────┐
│   Vue 3 + Vite  │ ──────────────────────────────▶ │   FastAPI (Python)  │
│   (port 5173)   │                                  │   (port 8000)       │
└─────────────────┘                                  └──────────┬──────────┘
                                                                │
                                              ┌─────────────────┴─────────────────┐
                                              │                                   │
                                   ┌──────────▼──────────┐           ┌────────────▼────────────┐
                                   │   PostgreSQL 16      │           │        Redis 7           │
                                   │   (données)          │           │   (sessions WebSocket)   │
                                   └─────────────────────┘           └─────────────────────────┘
```

Le frontend communique avec le backend via deux canaux :
- **REST API** pour toutes les opérations CRUD
- **WebSocket** pour recevoir les événements en temps réel (`task.created`, `task.updated`, `task.deleted`)

Lorsqu'un utilisateur modifie une tâche, le backend publie l'événement sur un canal Redis. Tous les serveurs backend abonnés reçoivent l'événement et le transmettent aux clients WebSocket connectés à ce projet. Cette architecture permet de scaler horizontalement le backend sans perdre les messages.

---

## Démarrage rapide

### Prérequis

- Docker ≥ 24 et Docker Compose v2
- Git

### Installation
```bash
# 1. Cloner le dépôt
git clone https://github.com/<votre-username>/taskboard.git
cd taskboard

# 2. Créer le fichier d'environnement
cp backend/.env.example backend/.env

# 3. Générer une clé secrète et la renseigner dans backend/.env
openssl rand -hex 32
# Remplacer la valeur de SECRET_KEY dans backend/.env

# 4. Lancer tous les services
docker compose up --build
```

L'application est accessible sur :
- **Frontend** → `http://localhost:5173`
- **Documentation API** → `http://localhost:8000/api/v1/docs`

---

## Structure du projet
```
taskboard/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # Routes : auth, projects, tasks, ws
│   │   ├── core/               # Configuration, sécurité, dépendances
│   │   ├── db/                 # Session SQLAlchemy, base déclarative
│   │   ├── models/             # Modèles ORM : User, Project, Task, Membership
│   │   ├── repositories/       # Couche d'accès aux données
│   │   ├── schemas/            # Schémas Pydantic requête / réponse
│   │   ├── services/           # Gestionnaire WebSocket avec Redis pub/sub
│   │   └── tests/              # Tests d'intégration pytest
│   ├── alembic/                # Migrations de base de données
│   ├── Dockerfile              # Build multi-stage
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── common/         # Navigation
│       │   ├── projects/       # Panneau de gestion des membres
│       │   └── tasks/          # Kanban, carte de tâche, modal
│       ├── router/             # Vue Router avec guards d'auth
│       ├── services/           # Client Axios, service WebSocket
│       ├── stores/             # Pinia : auth, projects, tasks, members
│       └── views/              # Login, Register, Dashboard, Project
│
├── .github/workflows/ci.yml    # Pipeline CI/CD
└── docker-compose.yml
```

---

## API

La documentation interactive complète est disponible sur `/api/v1/docs` lorsque le projet tourne localement.

### Authentification

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Créer un compte |
| `POST` | `/api/v1/auth/login` | Obtenir une paire de tokens |
| `POST` | `/api/v1/auth/refresh` | Renouveler les tokens |
| `GET` | `/api/v1/auth/me` | Profil de l'utilisateur connecté |

### Projets et membres

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/projects/` | Lister ses projets |
| `POST` | `/api/v1/projects/` | Créer un projet |
| `PATCH` | `/api/v1/projects/{id}` | Modifier un projet (admin) |
| `DELETE` | `/api/v1/projects/{id}` | Supprimer un projet (propriétaire) |
| `GET` | `/api/v1/projects/{id}/members` | Lister les membres |
| `POST` | `/api/v1/projects/{id}/members` | Ajouter un membre (admin) |
| `PATCH` | `/api/v1/projects/{id}/members/{userId}` | Changer un rôle (admin) |
| `DELETE` | `/api/v1/projects/{id}/members/{userId}` | Retirer un membre (admin) |

### Tâches

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/projects/{id}/tasks/` | Lister les tâches |
| `POST` | `/api/v1/projects/{id}/tasks/` | Créer une tâche |
| `PATCH` | `/api/v1/projects/{id}/tasks/{taskId}` | Modifier une tâche |
| `DELETE` | `/api/v1/projects/{id}/tasks/{taskId}` | Supprimer une tâche |

### WebSocket
```
ws://localhost:8000/api/v1/ws/{projectId}
```

Envoyer le token d'accès comme premier message après connexion :
```json
{ "token": "<access_token>" }
```

Événements reçus :
```json
{ "event": "task.created", "data": { ...task } }
{ "event": "task.updated", "data": { ...task } }
{ "event": "task.deleted", "data": { "id": "<uuid>" } }
```

---

## Tests
```bash
# Créer la base de test
docker compose exec db createdb -U postgres taskboard_test

# Lancer les tests
docker compose exec backend pytest app/tests/ -v
```

Les tests couvrent l'inscription, la connexion, la gestion de projets et les opérations CRUD sur les tâches. Chaque test tourne sur une base isolée, créée et détruite automatiquement.

---

## Pipeline CI/CD

Le fichier `.github/workflows/ci.yml` orchestre trois étapes déclenchées à chaque push :

1. **Tests** — le backend est testé contre un vrai PostgreSQL et Redis via les services GitHub Actions
2. **Build** — les images Docker sont construites et poussées sur GitHub Container Registry
3. **Déploiement** — les hooks Render sont déclenchés pour mettre à jour les services en production

Pour activer le déploiement, ajouter ces secrets dans les paramètres du dépôt GitHub :

| Secret | Description |
|---|---|
| `RENDER_DEPLOY_HOOK_BACKEND` | URL du deploy hook Render — backend |
| `RENDER_DEPLOY_HOOK_FRONTEND` | URL du deploy hook Render — frontend |

---

## Variables d'environnement

| Variable | Description |
|---|---|
| `DATABASE_URL` | Chaîne de connexion PostgreSQL async |
| `TEST_DATABASE_URL` | Base séparée pour les tests |
| `REDIS_URL` | Chaîne de connexion Redis |
| `SECRET_KEY` | Clé de signature JWT (`openssl rand -hex 32`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie du token d'accès (défaut : 30) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Durée de vie du refresh token (défaut : 7) |
| `ALLOWED_ORIGINS` | Origines CORS autorisées |

---

## Commandes utiles
```bash
# Arrêter les services
docker compose down

# Arrêter et supprimer les données
docker compose down -v

# Voir les logs du backend
docker compose logs backend -f

# Générer une migration après modification d'un modèle
docker compose exec backend alembic revision --autogenerate -m "description"

# Appliquer les migrations
docker compose exec backend alembic upgrade head
```

---

## Licence

MIT