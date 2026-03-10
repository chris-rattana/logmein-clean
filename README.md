cat > README.md <<'EOF'
# LogMeIn — Infrastructure DevOps et Architecture Réseau Sécurisée

## Présentation du projet

**LogMeIn** est un projet démonstratif combinant développement applicatif, DevOps et architecture réseau sécurisée.

L’objectif est de montrer comment concevoir et déployer une application web moderne en utilisant :

- une architecture containerisée avec Docker
- une pipeline CI/CD avec GitHub Actions
- une segmentation réseau sécurisée
- une architecture inter-sites avec VPN
- une supervision d’infrastructure avec Zabbix

Ce projet met l’accent sur la conception d’infrastructure et la sécurité.

---

# Objectifs du projet

Ce projet démontre la capacité à :

- concevoir une architecture applicative moderne
- déployer une application via Docker et Docker Compose
- mettre en place une CI/CD automatisée
- définir une architecture réseau sécurisée
- documenter une infrastructure complète

---

# Architecture du projet

Le projet repose sur plusieurs composants :

## Frontend
- Nginx
- reverse proxy vers l’API backend

## Backend
- Flask (Python)
- expose une API REST

## Base de données
- PostgreSQL

## Infrastructure
- Docker Compose
- Docker Swarm (optionnel)

## Sécurité réseau
- segmentation VLAN
- plan d’adressage VLSM
- ACL
- VPN site-to-site

## Supervision
- Zabbix

---

# Architecture simplifiée

Utilisateur  
↓  
Nginx  
↓  
Backend Flask  
↓  
PostgreSQL

Dans une architecture réseau complète :

Site B (utilisateurs)  
↓  
VPN site-to-site  
↓  
Site A (infrastructure)

Frontend → Backend → Database  
            ↓  
          Zabbix

---

# Installation locale

## Prérequis

- Docker
- Docker Compose
- Git

---

## Cloner le projet

git clone https://github.com/chris-rattana/logmein-clean.git  
cd logmein-clean

---

## Lancer l'application

docker compose up -d --build

---

## Vérifier les conteneurs

docker ps

---

# Accès à l'application

Frontend :

http://localhost

API backend :

http://localhost/api

---

# Commandes utiles

Arrêter les conteneurs :

docker compose down

Reconstruire l'application :

docker compose up -d --build

Voir les logs :

docker compose logs -f

---

# Pipeline CI/CD

Le projet utilise GitHub Actions pour automatiser :

- le linting
- les tests
- l’analyse de sécurité
- la construction des images Docker
- la publication dans GitHub Container Registry

---

# Architecture réseau

La conception réseau comprend :

- topologie logique multi-sites
- segmentation VLAN
- plan d’adressage VLSM
- matrice des flux
- politiques ACL
- VPN site-to-site
- supervision Zabbix

Documentation détaillée :

docs/network/logmein_network_documentation.md

---

# Structure du repository

LogMeIn-clean

app/                 Code de l'application  
ops/                 Scripts d'exploitation  
docs/                Documentation technique  
docs/network/        Documentation réseau  

docker-compose.yml  
docker-stack.yml  
README.md  

---

# Déploiement Docker Swarm (optionnel)

Initialiser le swarm :

bash ops/init-swarm.sh

Créer les secrets :

bash ops/create-secrets.sh

Déployer la stack :

bash ops/deploy-stack.sh

---

# Supervision

Une architecture de supervision Zabbix est prévue pour :

- surveiller les serveurs
- surveiller les équipements réseau
- détecter les pannes
- suivre la disponibilité de l'application

---

# Documentation

Documentation disponible dans :

docs/

Documentation réseau détaillée :

docs/network/logmein_network_documentation.md

---

# Auteur

Projet réalisé par :

Christophe Rattanamongkhoun

---

# Licence

Projet pédagogique destiné à démontrer des compétences en :

- DevOps
- Sécurité réseau
- Architecture d'infrastructure
- Déploiement applicatif

EOF