# COMPLIDO

## Plateforme de gestion des traitements de données personnelles

COMPLIDO est une application web développée avec Django permettant de gérer les traitements de données à caractère personnel dans le cadre de la conformité au RGPD.

L'application permet notamment de :

- gérer les traitements de données personnelles ;
- interagir avec un service d'intelligence artificielle (chatbot) en posant des questions sur le RGPD ;
- gérer ses informations personnelles de son compte utilisateur ;
- tester automatiquement les fonctionnalités de l'application ;
- exécuter l'application dans un environnement conteneurisé avec Docker et PostgreSQL.

---

## 1. Technologies utilisées

### Backend

- Python 3.12
- Django
- PostgreSQL 16

### Tests

- Pytest
- pytest-django
- pytest-cov

### Conteneurisation

- Docker
- Docker Compose
- PostgreSQL 16

### Intégration continue

- GitHub Actions

### Frontend

- HTML
- CSS
- Bootstrap 5

---

## 2. Architecture du projet

```text
complido_project/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Complido/
│   │
│   ├── manage.py
│   ├── pytest.ini
│   │
│   ├── Complido/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── entities/
│   │   └── ...
│   │
│   ├── personal_data_processing/
│   │   └── ...
│   │
│   ├── users/
│   │   └── ...
│   │
│   ├── templates/
│   │   ├── components/
│   │   ├── comments/
│   │   ├── personal_data_processing/
│   │   ├── users/
│   │   └── base.html
│   │
│   └── static/
│
├── seeds/
│
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

Le projet Django se situe dans le répertoire `Complido/`.

Les fichiers liés à Docker, aux dépendances et à GitHub Actions se trouvent à la racine du dépôt.

---

## 3. Fonctionnalités principales

### 3.1. Gestion des utilisateurs

L'application dispose d'un système d'authentification permettant aux utilisateurs de se connecter à l'application.

Chaque utilisateur possède notamment :

- un nom d'utilisateur ;
- un prénom ;
- un nom ;
- une adresse e-mail ;
- une entité ;
- un rôle.

L'utilisateur peut consulter et modifier ses informations personnelles.

Les informations suivantes sont modifiables :

- nom ;
- prénom ;
- nom d'utilisateur ;
- adresse e-mail.

L'entité et le rôle ne sont pas modifiables depuis le profil utilisateur.

---

### 3.2. Gestion des traitements

Chaque traitement de données personnelles est associé à une entité et à un utilisateur créateur.

Un traitement possède notamment :

- un nom ;
- une description ;
- une entité ;
- un créateur ;
- un statut ;
- une finalité ;
- une sous-finalité ;
- une description de la finalité ;
- une durée de conservation ;
- une base légale ;
- des catégories de données ;
- des catégories de personnes concernées ;
- des destinataires ;
- des sous-traitants ;
- des opérations ;
- des mesures de sécurité ;
- des informations relatives aux transferts internationaux ;
- une indication concernant la nécessité d'une AIPD.

---

## 4. Gestion des droits

Les traitements sont associés à une entité.

Un utilisateur consulte les traitements appartenant à son entité.

Les droits de modification et de suppression sont limités.

### Modification

Un traitement peut être modifié uniquement par :

- son créateur ;
- le DPO de l'entité à laquelle appartient le traitement.

### Suppression

Un traitement peut être supprimé uniquement par :

- son créateur ;
- le DPO de l'entité à laquelle appartient le traitement.

Un utilisateur appartenant à une autre entité ne peut pas accéder aux traitements de cette entité.

De la même manière, un DPO ne peut agir que sur les traitements appartenant à sa propre entité.

Les contrôles d'autorisation sont réalisés côté serveur dans les vues Django.

---

## 5. Base de données

COMPLIDO utilise PostgreSQL comme système de gestion de base de données.

La configuration de Django utilise des variables d'environnement afin de permettre l'utilisation de différentes bases selon l'environnement.

Les principales variables sont :

```text
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

La base de données utilisée pour les tests est distincte de celle utilisée par l'application.

---

## 6. Installation en environnement local

### 6.1. Prérequis

Pour exécuter le projet localement, les éléments suivants sont nécessaires :

- Python 3.12 ;
- PostgreSQL 16 ;
- Git.

Il est également possible d'utiliser Docker pour éviter l'installation locale de PostgreSQL.

---

## 7. Installation avec Python

Depuis la racine du projet :

```bash
git clone <URL_DU_REPOSITORY>
cd complido_project
```

Créer un environnement virtuel :

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## 8. Configuration de la base de données

PostgreSQL doit être disponible avant de lancer Django.

Les paramètres de connexion sont définis à l'aide des variables d'environnement :

```text
DB_NAME=complido
DB_USER=complido
DB_PASSWORD=complido_password
DB_HOST=localhost
DB_PORT=5432
```

La configuration Django se trouve dans :

```text
Complido/Complido/settings.py
```

---

## 9. Migrations Django

Depuis le répertoire contenant `manage.py` :

```bash
cd Complido
```

Vérifier les migrations :

```bash
python manage.py makemigrations --check --dry-run
```

Appliquer les migrations :

```bash
python manage.py migrate
```

---

## 10. Créer un superutilisateur

Pour créer un compte administrateur :

```bash
python manage.py createsuperuser
```

Puis suivre les instructions affichées dans le terminal.

---

## 11. Lancer l'application

Depuis le répertoire `Complido/` :

```bash
python manage.py runserver
```

L'application est accessible à l'adresse :

```text
http://127.0.0.1:8000/
```

---

# 12. Tests automatisés

COMPLIDO utilise Pytest pour automatiser les tests fonctionnels de l'application.

Les tests sont organisés au niveau des différentes applications Django.

Pour lancer l'ensemble des tests :

```bash
cd Complido
pytest -v
```

Pour obtenir la couverture de code :

```bash
pytest -v --cov=. --cov-report=term-missing
```

---

# 13. Conteneurisation avec Docker

COMPLIDO peut être exécuté entièrement avec Docker.

L'architecture Docker repose sur deux conteneurs principaux :

```text
┌─────────────────────────────────┐
│          Docker Compose         │
│                                 │
│  ┌───────────────────────────┐  │
│  │         COMPLIDO          │  │
│  │          Django           │  │
│  │        port 8000          │  │
│  └─────────────┬─────────────┘  │
│                │                │
│                │ PostgreSQL     │
│                ▼                │
│  ┌───────────────────────────┐  │
│  │       PostgreSQL 16       │  │
│  │        port 5432          │  │
│  └───────────────────────────┘  │
│                                 │
└─────────────────────────────────┘
```

---

# 14. Construire les conteneurs

Depuis la racine du projet :

```bash
docker compose build
```

---

# 15. Démarrer l'application avec Docker

```bash
docker compose up
```

Pour lancer les conteneurs en arrière-plan :

```bash
docker compose up -d
```

L'application est alors accessible à :

```text
http://localhost:8000
```

---

# 16. Arrêter les conteneurs

```bash
docker compose down
```

Pour supprimer également le volume PostgreSQL :

```bash
docker compose down -v
```

> **Attention :** l'option `-v` supprime les données stockées dans le volume PostgreSQL.

---

# 17. Consulter les logs

### Logs Django

```bash
docker compose logs -f web
```

### Logs PostgreSQL

```bash
docker compose logs -f db
```

### Logs de tous les services

```bash
docker compose logs -f
```

---

# 18. Exécuter les commandes Django dans Docker

### Migrations

```bash
docker compose exec web python Complido/manage.py migrate
```

### Créer un superutilisateur

```bash
docker compose exec web python Complido/manage.py createsuperuser
```

### Lancer les tests

```bash
docker compose exec web pytest
```

---

# 19. Intégration continue avec GitHub Actions

COMPLIDO utilise GitHub Actions afin d'automatiser les contrôles du projet.

Le pipeline est déclenché :

- lors d'un `push` sur la branche `main` ;
- lors d'une Pull Request vers la branche `main`.

Le workflow est défini dans :

```text
.github/workflows/ci.yml
```

---

# 20. Étapes du pipeline CI

Le pipeline est organisé selon les étapes suivantes :

1. Préparation de l'environnement ;
2. Mise en place de la base de données de test ;
3. Exécution des tests automatisés ;
4. Conteneurisation ;
5. Intégration sur la branche `main`.

---

## 20.1. Préparation de l'environnement

Le pipeline :

1. récupère le code source ;
2. installe Python 3.12 ;
3. installe les dépendances présentes dans `requirements.txt` ;
4. configure les variables d'environnement nécessaires à Django.

Les dépendances sont installées depuis la racine du projet :

```bash
pip install -r requirements.txt
```

Les commandes Django sont ensuite exécutées depuis le répertoire `Complido/`.

---

## 20.2. Mise en place de la base de données de test

GitHub Actions utilise l'image officielle :

```text
postgres:16
```

Une base dédiée aux tests est créée :

```text
complido_test
```

La base de données de test est indépendante de la base de données utilisée par l'application.

Cette séparation permet d'exécuter les tests sans modifier les données d'un environnement réel.

---

## 20.3. Exécution des tests automatisés

Le pipeline commence par vérifier la configuration Django :

```bash
python manage.py check
```

Les migrations sont ensuite vérifiées :

```bash
python manage.py makemigrations --check --dry-run
```

Puis elles sont appliquées :

```bash
python manage.py migrate
```

Les tests automatisés sont exécutés avec Pytest :

```bash
pytest -v --cov=. --cov-report=term-missing
```

Cette étape permet de détecter les régressions introduites par les modifications du code.

Le job de conteneurisation dépend directement de la réussite du job de tests :

```yaml
needs: tests
```

Ainsi, si les tests échouent, la conteneurisation n'est pas exécutée.

---

## 20.4. Conteneurisation

Lorsque les tests sont validés sur `main`, le pipeline passe à l'étape de conteneurisation.

L'application est construite à partir du `Dockerfile` :

```bash
docker compose build
```

Les différents services sont ensuite démarrés avec Docker Compose :

```bash
docker compose up -d
```

L'architecture conteneurisée repose sur :

- un conteneur Django pour l'application COMPLIDO ;
- un conteneur PostgreSQL 16 pour la base de données.

La configuration Docker permet de reproduire l'environnement de l'application de manière isolée et reproductible.

---

## 20.5. Intégration sur la branche `main`

Le développement est réalisé à l'aide de Pull Requests.

Le fonctionnement du pipeline est le suivant :

```text
Développement
      │
      ▼
Pull Request
      │
      ▼
GitHub Actions
      │
      ├── Préparation de l'environnement
      │
      ├── PostgreSQL 16
      │
      └── Tests Pytest
             │
             ▼
          Tests OK
             │
             ▼
       Validation de la PR
             │
             ▼
        Merge vers main
             │
             ▼
       Conteneurisation
```

La branche `main` doit être protégée afin d'imposer la réussite des contrôles CI avant l'intégration d'une Pull Request.

La branche principale contient ainsi uniquement du code ayant passé les contrôles définis dans le pipeline.

---

# 21. Variables d'environnement

Les informations sensibles ne doivent pas être intégrées directement dans le code source.

Les principales variables utilisées par l'application sont :

```text
SECRET_KEY
DJANGO_DEBUG
ALLOWED_HOSTS

DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

Selon l'environnement, ces variables sont configurées différemment.

### Environnement local

Les variables peuvent être définies localement.

### GitHub Actions

Les variables nécessaires aux tests sont configurées dans le workflow CI.

### Docker

Les variables sont transmises aux conteneurs via Docker Compose.

---

# 22. Commandes principales

## Développement local

```bash
cd Complido
python manage.py runserver
```

## Migrations

```bash
cd Complido
python manage.py migrate
```

## Tests

```bash
cd Complido
pytest -v
```

## Tests avec couverture

```bash
cd Complido
pytest -v --cov=. --cov-report=term-missing
```

## Docker

Depuis la racine du projet :

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs
docker compose down
```

---

# 23. Architecture globale

COMPLIDO repose sur une architecture Django connectée à une base de données PostgreSQL.

```text
                         GitHub
                            │
                            │
                 Pull Request / Push
                            │
                            ▼
                  ┌───────────────────┐
                  │   GitHub Actions   │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Préparation       │
                  │ Python + pip      │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ PostgreSQL 16     │
                  │ Base de test      │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Pytest            │
                  │ Tests automatisés │
                  └─────────┬─────────┘
                            │
                       Tests OK
                            │
                            ▼
                  ┌───────────────────┐
                  │ Docker Compose    │
                  └─────────┬─────────┘
                            │
                     ┌──────┴──────┐
                     ▼             ▼
               ┌──────────┐  ┌────────────┐
               │ Django   │  │ PostgreSQL │
               │ COMPLIDO │  │     16     │
               └──────────┘  └────────────┘
```

---

# 24. Objectif du projet

COMPLIDO a pour objectif de fournir une application permettant de centraliser et de structurer la gestion des traitements de données personnelles.

L'application intègre des mécanismes de contrôle des accès en fonction des utilisateurs, des rôles et des entités.

L'utilisation de Django, PostgreSQL, Pytest, Docker et GitHub Actions permet de disposer :

- d'une architecture structurée ;
- d'une base de données relationnelle ;
- de tests automatisés ;
- d'un contrôle continu du code ;
- d'un environnement conteneurisé ;
- d'un processus d'intégration reproductible.

L'ensemble permet de sécuriser le cycle de développement et de limiter l'intégration de code non validé dans la branche principale.
