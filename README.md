# Helpdesk Simulator

Simulateur d'appels support en ligne de commande.  
Un LLM local (Ollama + Llama 3.2) incarne l'utilisateur. Tu joues le technicien.

## Panne Replay

Sarah appelle le support parce qu'elle ne peut plus ouvrir son logiciel de facturation. Tu qualifies l'incident, tu vérifies le service SQL dans un labo simulé et tu confirmes le retour à la normale avant de fermer le ticket.

```bash
python3 helpdesk.py --scenario sql-replay
```

Écris à Sarah en langage naturel ou saisis une action du labo. Python contrôle l'état du service et la clôture du ticket. Ollama joue Sarah pendant l'échange. Tu peux essayer les actions ci-dessous avec les dépendances Python installées, même si Ollama est arrêté.

<details>
<summary>Démo guidée du ticket SQL</summary>

| Action | Résultat observé |
|---|---|
| `/port` | TCP 1433 est inaccessible. |
| `/service` | MSSQLSERVER est arrêté. |
| `/relancer` | MSSQLSERVER démarre. |
| `/cloturer` | Le ticket reste ouvert. La facturation doit être vérifiée. |
| `/facturation` | Le logiciel s'ouvre. Le test fonctionnel réussit. |
| `/cloturer` | Le ticket est résolu. |

Relance la même commande pour reprendre le ticket depuis le début.

</details>

## Les deux versions

| Fichier | Ce que ça fait |
|---------|----------------|
| `helpdesk.py` | **Juste l'appel.** Un problème aléatoire, aucune indication. Tu découvres en posant des questions. |
| `helpdesk_full.py` | Menu + 6 scénarios + voix Piper. Version d'entraînement complète. |

L'ancien fichier `simulateur_helpdesk.py` reste pour référence.

---

## Lancer

```bash
# Version minimale (recommandée)
python3 helpdesk.py

# Version complète
python3 helpdesk_full.py
```

## Installation

```bash
git clone https://github.com/cedricboucard/helpdesk-simulator.git
cd helpdesk-simulator
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:3b
```

Pour la version vocale uniquement : Piper + modèle `fr_FR-siwis-medium.onnx` dans `piper/` et `models/`.

## Scénarios (version complète)

| # | Problème | Cause réelle |
|---|-----------|---------------|
| 1 | Mot de passe refusé | Caps Lock |
| 2 | Imprimante muette | Mauvaise imprimante par défaut |
| 3 | Lecteur Z inaccessible | Session SMB expirée |
| 4 | Erreur SQL | Service MSSQLSERVER arrêté |
| 5 | ERP verrouillé | Processus orphelin |
| 6 | Chaos total | Dossiers sur le clavier + souris débranchée |

## Philosophie

La version minimale suit l'idée : supprimer ce qui n'est pas nécessaire.  
Pas de menu. Pas d'indication. Juste l'appel.

## Tests

```bash
python3 -m unittest discover -s tests
```

Les tests lancent le simulateur en ligne de commande et vérifient les conditions de clôture du ticket SQL.

MIT License
