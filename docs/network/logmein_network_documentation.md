# LogMeIn — Documentation technique réseau

## 1. Introduction

Le projet **LogMeIn** repose sur une architecture applicative et réseau conçue pour être **segmentée, sécurisée et supervisée**.

Cette documentation technique présente :

- la topologie logique retenue ;
- la segmentation par VLAN ;
- le plan d’adressage IP en VLSM ;
- la matrice des flux ;
- la politique ACL ;
- l’interconnexion sécurisée par VPN site-to-site ;
- la supervision centralisée avec Zabbix.

L’objectif est de proposer une architecture cohérente et défendable dans le cadre du projet, même sans maquette GNS3 finalisée.

---

## 2. État des livrables du projet

### 2.1. Partie application et DevOps déjà réalisée

Les éléments suivants sont considérés comme réalisés :

- Backend Flask fonctionnel ;
- Tests backend validés ;
- Qualité locale validée : black, flake8, bandit, pytest ;
- Docker Compose fonctionnel ;
- Frontend Nginx avec proxy `/api` ;
- CI GitHub Actions opérationnelle ;
- CD GitHub Actions opérationnelle ;
- Publication des images sur GHCR ;
- Backend durci avec Gunicorn, healthcheck Docker et utilisateur non-root ;
- `docker-stack.yml` prêt pour Docker Swarm ;
- Support des secrets Swarm ajouté ;
- Scripts d’exploitation présents : `init-swarm.sh`, `create-secrets.sh`, `deploy-stack.sh`.

### 2.2. Documentation déjà produite

Les éléments documentaires suivants sont disponibles :

- README corrigé ;
- documentation d’architecture de base ;
- documentation CI/CD de base ;
- documentation sécurité de base ;
- documentation déploiement de base ;
- documentation réseau de base.

### 2.3. Partie réseau et sécurité consolidée dans ce document

Le présent livrable formalise les éléments suivants :

- topologie logique finale ;
- tableau VLAN ;
- plan IP VLSM ;
- matrice des flux ;
- règles ACL ;
- logique VPN site-to-site ;
- supervision Zabbix ;
- documentation réseau finale consolidée.

### 2.4. Finitions optionnelles restantes

Les éléments suivants sont considérés comme optionnels ou bonus :

- healthcheck frontend ;
- healthcheck base de données ;
- test réel Docker Swarm ;
- finition documentaire globale ;
- annexes techniques supplémentaires si besoin.

---

## 3. Topologie logique finale

### 3.1. Hypothèse d’architecture retenue

L’architecture retenue repose sur **deux sites** :

- **Site A** : site principal / siège ;
- **Site B** : site distant / agence.

Le **Site A** centralise les ressources critiques du système, notamment :

- le frontend Nginx ;
- le backend Flask ;
- la base de données PostgreSQL ;
- le serveur de supervision Zabbix ;
- les accès d’administration principaux.

Le **Site B** héberge quant à lui :

- les postes utilisateurs distants ;
- un éventuel poste d’administration locale.

L’interconnexion entre les deux sites est assurée par un **VPN site-to-site**.

### 3.2. Logique de fonctionnement globale

L’application **LogMeIn** est hébergée de manière centralisée sur le **Site A**.  
Les utilisateurs du **Site B** accèdent à cette application via un tunnel sécurisé inter-sites.

La base de données est volontairement **centralisée et fortement protégée**.  
La supervision est également centralisée sur le Site A afin d’assurer une visibilité unifiée sur les serveurs et les équipements.

### 3.3. Schéma logique global

```text
                              INTERNET
                                  |
                           [ Routeur / Firewall ]
                                  |
                     =================================
                     ||                             ||
                [ VPN site-to-site ]         Accès admin contrôlé
                     ||
     ==============================================================
     ||                                                           ||
     ||                    SITE A — SIÈGE / DC                    ||
     ||                                                           ||
     ||   [ Core L3 Switch ]                                      ||
     ||        |                                                  ||
     ||        |-- VLAN Admin                                     ||
     ||        |-- VLAN Utilisateurs Site A                       ||
     ||        |-- VLAN Frontend / Reverse Proxy                  ||
     ||        |-- VLAN Backend Applicatif                        ||
     ||        |-- VLAN Base de données                           ||
     ||        |-- VLAN Supervision                               ||
     ||                                                           ||
     ||   [ Docker Host / Swarm ]                                 ||
     ||        |-- Nginx Frontend                                 ||
     ||        |-- Flask Backend                                  ||
     ||                                                           ||
     ||   [ Serveur PostgreSQL ]                                  ||
     ||   [ Serveur Zabbix ]                                      ||
     ||   [ Poste(s) Admin ]                                      ||
     ||                                                           ||
     ==============================================================

                                  ||
                                  ||
                           [ Routeur / Firewall ]
                                  |
     ==============================================================
     ||                                                           ||
     ||                  SITE B — AGENCE / DISTANT                ||
     ||                                                           ||
     ||   [ Switch d’accès ]                                      ||
     ||        |-- VLAN Utilisateurs Site B                       ||
     ||        |-- VLAN Admin Site B                              ||
     ||                                                           ||
     ||   [ Postes utilisateurs ]                                 ||
     ||   [ Poste admin local si besoin ]                         ||
     ||                                                           ||
     ==============================================================
```

### 3.4. Rôle de chaque site

#### 3.4.1. Site A

Le Site A constitue le cœur du système. Il héberge :

- les composants applicatifs ;
- les ressources de supervision ;
- les accès d’administration ;
- les données critiques.

#### 3.4.2. Site B

Le Site B représente un site distant consommateur de services.  
Il ne stocke pas de ressources critiques et ne fait qu’accéder au système centralisé.

---

## 4. Segmentation réseau par VLAN

### 4.1. Principe de segmentation

Afin d’isoler les usages, les fonctions d’administration, les composants applicatifs et les ressources critiques, l’architecture repose sur une **segmentation par VLAN**.

Cette segmentation vise à :

- réduire la surface d’exposition ;
- limiter les communications latérales ;
- faciliter l’application de politiques de filtrage ;
- améliorer la lisibilité globale du réseau.

### 4.2. Tableau VLAN retenu

| VLAN ID | Nom VLAN | Site | Rôle principal |
|---:|---|---|---|
| 10 | ADMIN_A | Site A | Administration du SI, accès restreint aux équipements et serveurs |
| 20 | USERS_A | Site A | Postes utilisateurs du site principal |
| 30 | FRONTEND_A | Site A | Zone frontend / reverse proxy Nginx |
| 40 | BACKEND_A | Site A | Zone applicative backend Flask |
| 50 | DB_A | Site A | Zone base de données PostgreSQL |
| 60 | MONITORING_A | Site A | Supervision Zabbix et outils de monitoring |
| 110 | ADMIN_B | Site B | Administration locale du site distant |
| 120 | USERS_B | Site B | Postes utilisateurs du site distant |
| 200 | VPN_TRANSIT | Inter-site | Réseau logique d’interconnexion VPN / transit |

### 4.3. Justification du découpage

Le découpage retenu distingue clairement :

- les zones utilisateurs ;
- les zones d’administration ;
- la couche frontend ;
- la couche backend ;
- la base de données ;
- la supervision ;
- l’interconnexion inter-sites.

Cette structuration est suffisamment simple pour rester défendable à l’oral tout en étant assez rigoureuse pour justifier ACL, VPN et supervision.

---

## 5. Plan d’adressage IP en VLSM

### 5.1. Principe retenu

Le plan d’adressage IP repose sur l’espace privé :

**10.10.0.0/16**

Une logique **VLSM** est appliquée afin d’adapter la taille des sous-réseaux aux besoins réels de chaque zone.

Répartition logique :

- Site A : bloc autour de `10.10.0.0/24`
- Site B : bloc autour de `10.10.1.0/24`
- Transit VPN : bloc dédié séparé

### 5.2. Plan VLSM du Site A

| VLAN ID | Nom VLAN | Sous-réseau | Masque | Capacité utile | Passerelle | Usage |
|---:|---|---|---|---:|---|---|
| 20 | USERS_A | 10.10.0.0/26 | 255.255.255.192 | 62 hôtes | 10.10.0.1 | Postes utilisateurs Site A |
| 10 | ADMIN_A | 10.10.0.64/28 | 255.255.255.240 | 14 hôtes | 10.10.0.65 | Administration Site A |
| 30 | FRONTEND_A | 10.10.0.80/28 | 255.255.255.240 | 14 hôtes | 10.10.0.81 | Frontend / reverse proxy |
| 40 | BACKEND_A | 10.10.0.96/28 | 255.255.255.240 | 14 hôtes | 10.10.0.97 | Backend Flask |
| 50 | DB_A | 10.10.0.112/29 | 255.255.255.248 | 6 hôtes | 10.10.0.113 | Base PostgreSQL |
| 60 | MONITORING_A | 10.10.0.128/28 | 255.255.255.240 | 14 hôtes | 10.10.0.129 | Supervision Zabbix |

### 5.3. Plan VLSM du Site B

| VLAN ID | Nom VLAN | Sous-réseau | Masque | Capacité utile | Passerelle | Usage |
|---:|---|---|---|---:|---|---|
| 120 | USERS_B | 10.10.1.0/27 | 255.255.255.224 | 30 hôtes | 10.10.1.1 | Postes utilisateurs Site B |
| 110 | ADMIN_B | 10.10.1.32/28 | 255.255.255.240 | 14 hôtes | 10.10.1.33 | Administration Site B |

### 5.4. Réseau de transit VPN

| VLAN ID | Nom VLAN | Sous-réseau | Masque | Capacité utile | Usage |
|---:|---|---|---|---:|---|
| 200 | VPN_TRANSIT | 10.10.255.0/30 | 255.255.255.252 | 2 hôtes | Liaison logique site-to-site |

Exemple :

- extrémité Site A : `10.10.255.1`
- extrémité Site B : `10.10.255.2`

### 5.5. Adresses clés proposées

#### Site A

| Composant | IP proposée |
|---|---|
| Gateway USERS_A | 10.10.0.1 |
| Gateway ADMIN_A | 10.10.0.65 |
| Gateway FRONTEND_A | 10.10.0.81 |
| Gateway BACKEND_A | 10.10.0.97 |
| Gateway DB_A | 10.10.0.113 |
| Gateway MONITORING_A | 10.10.0.129 |
| Nginx Frontend | 10.10.0.82 |
| Flask Backend | 10.10.0.98 |
| PostgreSQL | 10.10.0.114 |
| Zabbix Server | 10.10.0.130 |
| Poste Admin A | 10.10.0.66 |

#### Site B

| Composant | IP proposée |
|---|---|
| Gateway USERS_B | 10.10.1.1 |
| Gateway ADMIN_B | 10.10.1.33 |
| Poste Admin B | 10.10.1.34 |

#### VPN

| Extrémité | IP proposée |
|---|---|
| VPN Site A | 10.10.255.1 |
| VPN Site B | 10.10.255.2 |

### 5.6. Justification du plan d’adressage

Ce plan présente les avantages suivants :

- lisibilité ;
- cohérence avec la segmentation VLAN ;
- limitation du gaspillage d’adresses ;
- facilitation des ACL et du routage ;
- simplicité d’explication en soutenance.

---

## 6. Matrice des flux

### 6.1. Politique générale

Le principe de sécurité retenu est le suivant :

- tout flux est interdit par défaut ;
- seuls les flux strictement nécessaires sont autorisés ;
- la base de données n’est jamais exposée ;
- le backend n’est pas accessible directement par les utilisateurs ;
- les accès d’administration sont réservés aux VLAN dédiés ;
- la supervision est centralisée et contrôlée.

### 6.2. Matrice des flux

| Source | Destination | Service / usage | Protocole | Port(s) | Action | Justification |
|---|---|---|---|---|---|---|
| USERS_A | FRONTEND_A | Accès application web | TCP | 443 | Autorisé | Accès applicatif HTTPS |
| USERS_B | FRONTEND_A | Accès application via VPN | TCP | 443 | Autorisé | Accès distant sécurisé |
| USERS_A | BACKEND_A | Accès direct backend | TCP | 5000 ou port backend | Interdit | Le backend n’est pas exposé |
| USERS_B | BACKEND_A | Accès direct backend | TCP | 5000 ou port backend | Interdit | Même logique |
| USERS_A | DB_A | Accès base | TCP | 5432 | Interdit | La base est isolée |
| USERS_B | DB_A | Accès base | TCP | 5432 | Interdit | La base est isolée |
| FRONTEND_A | BACKEND_A | Trafic applicatif interne | TCP | 5000 | Autorisé | Reverse proxy vers backend |
| FRONTEND_A | DB_A | Accès direct DB | TCP | 5432 | Interdit | Le frontend ne joint pas la base |
| BACKEND_A | DB_A | Requêtes SQL applicatives | TCP | 5432 | Autorisé | Seul le backend joint la DB |
| ADMIN_A | FRONTEND_A | Administration | TCP | 22, 443 | Autorisé | Maintenance du frontend |
| ADMIN_A | BACKEND_A | Administration | TCP | 22 | Autorisé | Maintenance du backend |
| ADMIN_A | DB_A | Administration | TCP | 22, 5432 si besoin | Autorisé sous restriction | Maintenance exceptionnelle |
| ADMIN_A | MONITORING_A | Administration Zabbix | TCP | 22, 443 | Autorisé | Gestion supervision |
| ADMIN_B | FRONTEND_A | Administration distante limitée | TCP | 443, éventuellement 22 | Autorisé sous restriction | Accès distant limité |
| ADMIN_B | BACKEND_A | Administration distante | TCP | 22 | Autorisé sous restriction | Selon le scénario |
| ADMIN_B | DB_A | Administration DB | TCP | 22, 5432 | Interdit ou très restreint | DB réservée au Site A |
| MONITORING_A | FRONTEND_A | Supervision | ICMP / TCP / agent | ICMP, 10050, 80/443 selon méthode | Autorisé | Contrôle de disponibilité |
| MONITORING_A | BACKEND_A | Supervision | ICMP / TCP / agent | ICMP, 10050 | Autorisé | Supervision backend |
| MONITORING_A | DB_A | Supervision | ICMP / TCP / agent | ICMP, 10050, éventuellement 5432 | Autorisé sous restriction | Contrôle de disponibilité |
| MONITORING_A | Équipements réseau | Supervision | ICMP / SNMP | ICMP, UDP 161 | Autorisé | Contrôle équipement |
| INTERNET | FRONTEND_A | Accès public web | TCP | 443 | Autorisé | Seul point exposé |
| INTERNET | BACKEND_A | Accès public backend | TCP | Any | Interdit | Backend non exposé |
| INTERNET | DB_A | Accès public DB | TCP | 5432 | Interdit | Interdiction absolue |
| INTERNET | MONITORING_A | Accès supervision | TCP/UDP | Any | Interdit | Supervision interne |

### 6.3. Synthèse

Les flux indispensables au fonctionnement sont :

- utilisateurs vers frontend ;
- frontend vers backend ;
- backend vers base ;
- administration vers serveurs ;
- supervision vers composants cibles ;
- accès inter-sites via VPN.

---

## 7. Politique ACL

### 7.1. Principes retenus

Les ACL traduisent la matrice des flux en politique de filtrage effective.

Les principes retenus sont les suivants :

- tout trafic non explicitement autorisé est interdit ;
- les utilisateurs ne peuvent accéder qu’au frontend ;
- le frontend seul peut joindre le backend ;
- le backend seul peut joindre la base ;
- les accès d’administration sont réservés aux VLAN dédiés ;
- la supervision dispose de flux dédiés ;
- l’interconnexion inter-sites est filtrée et ne repose pas sur un any-any.

### 7.2. ACL logiques

#### 7.2.1. Accès utilisateurs vers l’application

| Source | Destination | Protocole | Port | Action |
|---|---|---|---|---|
| USERS_A | FRONTEND_A | TCP | 443 | Permit |
| USERS_B | FRONTEND_A | TCP | 443 | Permit |
| USERS_A | BACKEND_A | TCP | Any | Deny |
| USERS_B | BACKEND_A | TCP | Any | Deny |
| USERS_A | DB_A | TCP | 5432 | Deny |
| USERS_B | DB_A | TCP | 5432 | Deny |

#### 7.2.2. Frontend vers backend

| Source | Destination | Protocole | Port | Action |
|---|---|---|---|---|
| FRONTEND_A | BACKEND_A | TCP | 5000 | Permit |
| FRONTEND_A | DB_A | TCP | 5432 | Deny |

#### 7.2.3. Backend vers base de données

| Source | Destination | Protocole | Port | Action |
|---|---|---|---|---|
| BACKEND_A | DB_A | TCP | 5432 | Permit |
| Toute autre source | DB_A | TCP | 5432 | Deny |

#### 7.2.4. Administration

| Source | Destination | Protocole | Port | Action |
|---|---|---|---|---|
| ADMIN_A | FRONTEND_A | TCP | 22, 443 | Permit |
| ADMIN_A | BACKEND_A | TCP | 22 | Permit |
| ADMIN_A | DB_A | TCP | 22 | Permit |
| ADMIN_A | DB_A | TCP | 5432 | Permit si administration DB nécessaire |
| ADMIN_A | MONITORING_A | TCP | 22, 443 | Permit |
| ADMIN_B | FRONTEND_A | TCP | 443 | Permit |
| ADMIN_B | BACKEND_A | TCP | 22 | Permit sous restriction |
| ADMIN_B | DB_A | TCP | 22, 5432 | Deny |

#### 7.2.5. Supervision Zabbix

| Source | Destination | Protocole | Port | Action |
|---|---|---|---|---|
| MONITORING_A | FRONTEND_A | ICMP / TCP | ICMP, 443, 10050 | Permit |
| MONITORING_A | BACKEND_A | ICMP / TCP | ICMP, 10050 | Permit |
| MONITORING_A | DB_A | ICMP / TCP | ICMP, 10050 | Permit |
| MONITORING_A | Équipements réseau | ICMP / UDP | ICMP, 161 | Permit |

#### 7.2.6. Exposition Internet

| Source | Destination | Protocole | Port | Action |
|---|---|---|---|---|
| INTERNET | FRONTEND_A | TCP | 443 | Permit |
| INTERNET | BACKEND_A | TCP | Any | Deny |
| INTERNET | DB_A | TCP | 5432 | Deny |
| INTERNET | MONITORING_A | TCP/UDP | Any | Deny |

#### 7.2.7. Inter-site via VPN

| Source | Destination | Protocole | Port | Action |
|---|---|---|---|---|
| USERS_B | FRONTEND_A | TCP | 443 | Permit via VPN |
| ADMIN_B | FRONTEND_A | TCP | 443 | Permit via VPN |
| ADMIN_B | BACKEND_A | TCP | 22 | Permit sous restriction via VPN |
| USERS_B | DB_A | TCP | 5432 | Deny |
| USERS_B | BACKEND_A | TCP | Any | Deny |

### 7.3. Bénéfices de la politique ACL

Cette politique empêche notamment :

- l’exposition directe du backend ;
- l’accès direct des utilisateurs à la base ;
- les communications latérales non justifiées ;
- l’ouverture excessive entre les sites.

---

## 8. Interconnexion sécurisée par VPN site-to-site

### 8.1. Objectif du VPN

Le VPN site-to-site a pour rôle de :

- relier le Site B au Site A ;
- chiffrer les échanges inter-sites ;
- permettre aux utilisateurs distants d’accéder à l’application centralisée ;
- autoriser certains accès d’administration distants ;
- éviter l’exposition directe des ressources internes sur Internet.

### 8.2. Schéma logique du VPN

```text
                           INTERNET
                              |
                  =========================
                  |                      |
 [ Firewall / Routeur Site A ]   [ Firewall / Routeur Site B ]
                  |                      |
                  |====== VPN IPsec =====|
                  |                      |
             -----------             -----------
             | Site A  |             | Site B  |
             -----------             -----------

Site A :
- FRONTEND_A : 10.10.0.80/28
- BACKEND_A  : 10.10.0.96/28
- DB_A       : 10.10.0.112/29
- ADMIN_A    : 10.10.0.64/28
- MONITORING_A : 10.10.0.128/28

Site B :
- USERS_B    : 10.10.1.0/27
- ADMIN_B    : 10.10.1.32/28

Transit logique VPN :
- Site A : 10.10.255.1/30
- Site B : 10.10.255.2/30
```

### 8.3. Type de VPN retenu

Le choix retenu est un **VPN site-to-site IPsec**, avec les paramètres logiques suivants :

- protocole : IPsec ;
- authentification : clé pré-partagée ou certificats ;
- chiffrement : AES-256 ;
- intégrité : SHA-256 ;
- échange de clés : IKEv2.

### 8.4. Flux autorisés dans le tunnel

#### Flux autorisés

- `USERS_B → FRONTEND_A : TCP 443`
- `ADMIN_B → FRONTEND_A : TCP 443`
- `ADMIN_B → BACKEND_A : TCP 22` si besoin

#### Flux refusés

- `USERS_B → BACKEND_A`
- `USERS_B → DB_A`
- `ADMIN_B → DB_A`
- tout flux non explicitement autorisé

### 8.5. Principe de sécurité

Le tunnel VPN sécurise le transport entre les sites, mais ne remplace pas les ACL.  
Les ACL assurent le contrôle fin des accès autorisés dans le tunnel.

---

## 9. Supervision centralisée avec Zabbix

### 9.1. Objectif

La supervision a pour objectif de :

- vérifier la disponibilité des services critiques ;
- détecter rapidement une panne ou une dégradation ;
- centraliser la visibilité sur les serveurs et équipements ;
- renforcer la dimension opérationnelle du projet.

### 9.2. Positionnement de Zabbix

Le serveur Zabbix est positionné dans le VLAN :

- **MONITORING_A**
- réseau : `10.10.0.128/28`
- IP proposée : `10.10.0.130`

### 9.3. Ressources supervisées

#### 9.3.1. Serveurs applicatifs

- frontend Nginx ;
- backend Flask ;
- serveur PostgreSQL.

#### 9.3.2. Infrastructure réseau

- routeur / firewall Site A ;
- routeur / firewall Site B ;
- switch principal Site A ;
- switch Site B.

#### 9.3.3. Connectivité inter-sites

- disponibilité du lien inter-sites ;
- atteignabilité des ressources critiques distantes.

### 9.4. Méthodes de supervision

#### Serveurs

- ICMP ;
- agent Zabbix ;
- contrôles TCP ;
- contrôles HTTP/HTTPS.

#### Équipements réseau

- ICMP ;
- SNMP si nécessaire.

### 9.5. Tableau de supervision

| Élément supervisé | Méthode | Indicateurs principaux | Criticité |
|---|---|---|---|
| Frontend Nginx | ICMP + TCP + HTTPS | Ping, port 443, réponse HTTPS | Critique |
| Backend Flask | ICMP + TCP + Agent | Ping, port backend, CPU, RAM, disque | Critique |
| PostgreSQL | ICMP + TCP + Agent | Ping, port 5432, service DB, disque | Critique |
| Routeur/Firewall Site A | ICMP / SNMP | Disponibilité, interfaces | Élevée |
| Routeur/Firewall Site B | ICMP / SNMP | Disponibilité, connectivité inter-site | Élevée |
| Switch principal Site A | ICMP / SNMP | Disponibilité, interfaces | Moyenne |
| Switch Site B | ICMP / SNMP | Disponibilité, interfaces | Moyenne |
| VPN inter-sites | ICMP / logique | Reachability entre sites | Critique |

### 9.6. Alertes proposées

#### Alertes critiques

- indisponibilité du frontend ;
- indisponibilité du backend ;
- indisponibilité de la base de données ;
- perte du lien vers le Site B ;
- perte d’un routeur ou firewall.

#### Alertes majeures

- CPU trop élevé sur le backend ;
- RAM trop élevée sur la base ;
- disque presque plein sur la base ;
- temps de réponse HTTPS anormalement élevé.

---

## 10. Documentation réseau consolidée

### 10.1. Vision d’ensemble

L’architecture réseau du projet **LogMeIn** vise à fournir une infrastructure :

- segmentée ;
- sécurisée ;
- lisible ;
- supervisée ;
- cohérente avec une application web centralisée accessible depuis plusieurs sites.

### 10.2. Forces de l’architecture retenue

#### Sécurité

- séparation stricte des zones ;
- base de données isolée ;
- limitation des accès inter-sites ;
- exposition Internet réduite au strict nécessaire.

#### Lisibilité

- topologie simple à comprendre ;
- VLAN clairement identifiés ;
- adressage cohérent ;
- politique de flux facile à défendre.

#### Maintenabilité

- architecture structurée ;
- supervision centralisée ;
- segmentation permettant de futures évolutions.

#### Réalisme

Même sans maquette GNS3 finalisée, cette documentation reste crédible dans le cadre d’un projet d’architecture réseau et sécurité. Elle démontre une démarche complète de conception et de sécurisation.

---

## 11. Conclusion générale

Le projet **LogMeIn** s’appuie sur une architecture réseau pensée pour offrir un niveau de sécurité et de structuration adapté à une application web centralisée accessible depuis plusieurs sites.

La combinaison :

- d’une segmentation par VLAN ;
- d’un plan d’adressage VLSM ;
- d’une politique de flux restrictive ;
- d’ACL cohérentes ;
- d’un VPN site-to-site ;
- d’une supervision centralisée avec Zabbix ;

permet de proposer une infrastructure logique robuste, lisible et défendable dans le cadre du projet.

Cette approche constitue une base sérieuse pour un rendu académique ou professionnalisant orienté réseau, sécurité et infrastructure.

---

## 12. Annexe — Exemple de pseudo-configuration ACL

Le bloc suivant constitue une traduction illustrative de la politique de filtrage en pseudo-configuration ACL.  
Il est fourni à titre de démonstration logique et ne correspond pas à une implémentation sur un équipement constructeur spécifique.

```bash
! Politique générale
deny ip any any

! Utilisateurs vers frontend
permit tcp 10.10.0.0 0.0.0.63 10.10.0.80 0.0.0.15 eq 443
permit tcp 10.10.1.0 0.0.0.31 10.10.0.80 0.0.0.15 eq 443

! Interdiction accès direct backend
deny tcp 10.10.0.0 0.0.0.63 10.10.0.96 0.0.0.15 any
deny tcp 10.10.1.0 0.0.0.31 10.10.0.96 0.0.0.15 any

! Interdiction accès direct DB
deny tcp 10.10.0.0 0.0.0.63 10.10.0.112 0.0.0.7 eq 5432
deny tcp 10.10.1.0 0.0.0.31 10.10.0.112 0.0.0.7 eq 5432

! Frontend vers backend
permit tcp 10.10.0.80 0.0.0.15 10.10.0.96 0.0.0.15 eq 5000

! Frontend vers DB interdit
deny tcp 10.10.0.80 0.0.0.15 10.10.0.112 0.0.0.7 eq 5432

! Backend vers DB autorisé
permit tcp 10.10.0.96 0.0.0.15 10.10.0.112 0.0.0.7 eq 5432

! Admin A
permit tcp 10.10.0.64 0.0.0.15 10.10.0.80 0.0.0.15 eq 22
permit tcp 10.10.0.64 0.0.0.15 10.10.0.80 0.0.0.15 eq 443
permit tcp 10.10.0.64 0.0.0.15 10.10.0.96 0.0.0.15 eq 22
permit tcp 10.10.0.64 0.0.0.15 10.10.0.112 0.0.0.7 eq 22
permit tcp 10.10.0.64 0.0.0.15 10.10.0.112 0.0.0.7 eq 5432

! Monitoring
permit icmp 10.10.0.128 0.0.0.15 any
permit tcp 10.10.0.128 0.0.0.15 10.10.0.80 0.0.0.15 eq 443
permit tcp 10.10.0.128 0.0.0.15 10.10.0.96 0.0.0.15 eq 10050
permit tcp 10.10.0.128 0.0.0.15 10.10.0.112 0.0.0.7 eq 10050
permit udp 10.10.0.128 0.0.0.15 any eq 161
```
