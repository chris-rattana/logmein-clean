# LogMeIn

## Présentation du projet

**LogMeIn** est un projet de tableau de bord de logs et d'infrastructure, conçu pour démontrer une approche complète **applicative + DevOps + réseau/sécurité**.

Le projet s'appuie sur :

- un **backend Flask** ;
- une **base de données PostgreSQL** ;
- un **frontend servi par Nginx** ;
- une chaîne **CI/CD avec GitHub Actions** ;
- une publication d'images Docker sur **GHCR** ;
- un mode de déploiement local avec **Docker Compose** ;
- un mode de déploiement cible avec **Docker Swarm** ;
- une **documentation technique réseau** couvrant VLAN, VLSM, ACL, VPN et supervision Zabbix.

L'objectif du projet est de montrer une architecture cohérente, conteneurisée, sécurisée et documentée, exploitable dans un contexte de démonstration technique ou de rendu académique / professionnalisant.

---

## À quoi sert ce projet ?

Ce projet sert à :

- centraliser et consulter des logs via une application web ;
- démontrer une architecture web simple en **3 couches** :
  - frontend ;
  - backend ;
  - base de données ;
- illustrer un pipeline DevOps moderne :
  - qualité de code ;
  - tests ;
  - CI ;
  - CD ;
  - build d'images Docker ;
- documenter une conception réseau crédible :
  - segmentation VLAN ;
  - plan d'adressage VLSM ;
  - politique ACL ;
  - VPN site-to-site ;
  - supervision Zabbix.

---

## Fonctionnalités principales

- Interface web servie par **Nginx**
- Backend **Flask**
- Base de données **PostgreSQL**
- Proxy du frontend vers l'API via `/api`
- Exécution locale via **Docker Compose**
- Déploiement cible via **Docker Swarm**
- Documentation technique réseau dans `docs/network/`

---

## Architecture technique

### Stack utilisée

- **Frontend** : Nginx
- **Backend** : Flask
- **Base de données** : PostgreSQL
- **Conteneurisation** : Docker / Docker Compose
- **Déploiement** : Docker Swarm
- **CI/CD** : GitHub Actions + GHCR
- **Documentation réseau** : segmentation, ACL, VPN, supervision

### Vue logique simplifiée

```text
Utilisateur
   |
   v
Frontend Nginx
   |
   v
Backend Flask
   |
   v
PostgreSQL