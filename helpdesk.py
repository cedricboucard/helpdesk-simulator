#!/usr/bin/env python3
"""
Helpdesk — Juste l'appel.
Un problème aléatoire. Aucune indication. Tu découvres.
"""

import random
import requests
import sys

OLLAMA = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

PROBLEMS = [
    {
        "intro": "Bonjour, depuis ce matin je n'arrive plus à imprimer.",
        "prompt": (
            "Tu es Sophie des RH. Polie, un peu pressée. "
            "La cause réelle : dans Word, c'est 'Microsoft Print to PDF' qui est sélectionnée "
            "au lieu de l'imprimante réseau Canon-RH. "
            "Réponds en une ou deux phrases courtes, comme au téléphone. "
            "Si le technicien te fait regarder quelle imprimante est choisie dans la boîte de dialogue, "
            "tu t'en rends compte, tu sélectionnes la bonne et l'imprimante démarre."
        ),
        "temp": 0.4,
    },
    {
        "intro": "Allo ? C'est Christian du marketing. Mon mot de passe ne marche plus depuis que je suis revenu de vacances.",
        "prompt": (
            "Tu es Christian, marketing. Calme mais un peu distrait. "
            "La cause réelle : la touche Caps Lock est activée sur ton clavier. "
            "Réponds en une ou deux phrases. "
            "Si le technicien te fait vérifier le voyant Caps Lock ou te demande de taper le mot de passe "
            "dans un champ visible, tu découvres le problème et tu te connectes."
        ),
        "temp": 0.4,
    },
    {
        "intro": "Support ? Julien du bureau d'études. J'ai une croix rouge sur mon lecteur Z, impossible d'ouvrir les plans.",
        "prompt": (
            "Tu es Julien, dessinateur projeteur. Tu as des bases informatiques. "
            "La cause réelle : la session SMB du lecteur réseau Z: a expiré après le renouvellement du bail DHCP. "
            "Réponds brièvement. "
            "Si le technicien te fait tester le chemin UNC (\\\\serveur\\partage) ou un ping vers le serveur, "
            "le lecteur redevient accessible."
        ),
        "temp": 0.3,
    },
    {
        "intro": "Bonjour le support, Sarah de l'ADV. Quand je lance la facturation j'ai une erreur : 'Impossible d'établir la connexion avec le serveur SQL'.",
        "prompt": (
            "Tu es Sarah, assistante ADV. Rigoureuse, tu lis les messages d'erreur exactement. "
            "La cause réelle : le service Windows MSSQLSERVER sur le serveur est arrêté. "
            "Réponds de façon précise. "
            "Si le technicien te dit qu'il redémarre le service SQL ou vérifie le port 1433, "
            "après un moment tu confirmes que le logiciel se reconnecte."
        ),
        "temp": 0.25,
    },
]


def ask(messages, temp):
    try:
        r = requests.post(
            OLLAMA,
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temp, "num_predict": 100},
            },
            timeout=15,
        )
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"\nOllama indisponible : {e}")
        sys.exit(1)


def call():
    problem = random.choice(PROBLEMS)
    print("\nNouvel appel entrant...\n")
    print(f"Utilisateur :\n{problem['intro']}")

    messages = [
        {"role": "system", "content": problem["prompt"]},
        {"role": "assistant", "content": problem["intro"]},
    ]

    while True:
        try:
            user = input("\nTechnicien : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAppel terminé.")
            break

        if not user or user.lower() in ("q", "quitter", "exit", "fin"):
            print("\nAppel terminé.")
            break

        messages.append({"role": "user", "content": user})
        reply = ask(messages, problem["temp"])
        print(f"\nUtilisateur :\n{reply}")
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    call()
