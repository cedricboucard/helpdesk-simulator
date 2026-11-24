# 📞 Helpdesk Simulator — Simulateur d'Appels Support N1/N2 (CLI & IA Locale)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/LLM-Llama_3.2_%28Ollama%29-black.svg)](https://ollama.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Deux versions coexistent :

| Fichier | Description |
|---------|-------------|
| **`helpdesk.py`** | Version minimale. Un appel aléatoire, aucun menu, aucune indication. Tu découvres le problème en posant des questions. |
| **`helpdesk_full.py`** | Version complète. Menu, 6 scénarios, voix Piper TTS. |

L'ancienne `simulateur_helpdesk.py` est conservée pour référence.

---

## Version minimale (recommandée)

```bash
python3 helpdesk.py
```

Un appel arrive. Un problème caché. Tu poses des questions.

## Version complète

```bash
python3 helpdesk_full.py
```

Nécessite Piper TTS et le modèle de voix (voir plus bas).

---

## Scénarios (version complète)

| Niveau | Titre | Problème |
|:---:|---|---|
| 1 | Mot de passe oublié | Caps Lock |
| 2 | Imprimante inaccessible | Mauvaise imprimante par défaut |
| 3 | Lecteur réseau | Session SMB expirée |
| 4 | SQL Server | Service arrêté |
| 5 | ERP verrouillé | Processus orphelin |
| 6 | Mode Enfer | Chaos utilisateur |

## Installation

```bash
git clone https://github.com/cedricboucard/helpdesk-simulator.git
cd helpdesk-simulator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:3b
```

Pour la version vocale uniquement :
- Installer Piper + modèle `fr_FR-siwis-medium.onnx` dans les dossiers `piper/` et `models/`.

## Licence

MIT
