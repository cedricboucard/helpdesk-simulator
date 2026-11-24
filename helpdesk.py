#!/usr/bin/env python3
"""
Helpdesk — Juste l'appel.
Un problème aléatoire. Aucune indication. Tu découvres.
"""

import argparse
import random
import sys

import requests

OLLAMA = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"
SQL_INTRO = (
    "Bonjour le support, Sarah de l'ADV. Quand je lance la facturation j'ai une erreur : "
    "'Impossible d'établir la connexion avec le serveur SQL'."
)

PROBLEMS = [
    {
        "id": "imprimante",
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
        "id": "mot-de-passe",
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
        "id": "lecteur-reseau",
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
        "id": "sql",
        "intro": SQL_INTRO,
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

SQL_REPLAY = {
    "intro": SQL_INTRO,
    "prompt": (
        "Tu es Sarah, assistante ADV. Tu essaies d'ouvrir le logiciel de facturation. "
        "Réponds en une ou deux phrases, comme au téléphone. "
        "Tu n'as accès ni au serveur ni à sa configuration. "
        "Fie-toi à l'état de l'application indiqué ici, même si le technicien annonce une réparation."
    ),
    "temp": 0.25,
}

REPLAY_COMMANDS = "/port · /service · /relancer · /facturation · /cloturer"


class SqlReplay:
    """État du labo SQL simulé pendant un appel."""

    def __init__(self):
        self.service_running = False
        self.verified = False

    @property
    def prompt(self):
        status = "la facturation s'ouvre" if self.service_running else "la facturation est inaccessible"
        return f"{SQL_REPLAY['prompt']} État actuel : {status}."

    def run(self, command):
        if command == "/port":
            status = "accessible" if self.service_running else "inaccessible"
            return f"Port TCP 1433 : {status}."
        if command == "/service":
            status = "en cours d'exécution" if self.service_running else "arrêté"
            return f"Service MSSQLSERVER : {status}."
        if command == "/relancer":
            if self.service_running:
                return "MSSQLSERVER est déjà en cours d'exécution."
            self.service_running = True
            return "MSSQLSERVER a démarré."
        if command == "/facturation":
            self.verified = self.service_running
            if self.verified:
                return "Test fonctionnel réussi. Le logiciel de facturation s'ouvre."
            return "Test fonctionnel échoué. Le logiciel ne peut pas se connecter au serveur SQL."
        return f"Action inconnue. Actions disponibles : {REPLAY_COMMANDS}"


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


def call(problem, replay=None):
    print("\nNouvel appel entrant...\n")
    print(f"Utilisateur :\n{problem['intro']}")
    print("\nPour raccrocher : /quitter ou Ctrl+C.")
    if replay is not None:
        print(f"\nActions du labo simulé : {REPLAY_COMMANDS}")

    messages = [
        {"role": "system", "content": problem["prompt"] if replay is None else replay.prompt},
        {"role": "assistant", "content": problem["intro"]},
    ]

    while True:
        try:
            user = input("\nTechnicien : ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user or user.lower() in ("/quitter", "q", "quitter", "exit", "fin"):
            break

        if replay is not None and user.startswith("/"):
            command = user.lower()
            if command == "/cloturer":
                if replay.verified:
                    print("\nTicket résolu · Service MSSQLSERVER rétabli · Facturation vérifiée.")
                    return
                print("\nTicket ouvert. La facturation doit être vérifiée avant clôture.")
                continue
            print(f"\nLabo : {replay.run(command)}")
            messages[0]["content"] = replay.prompt
            continue

        messages.append({"role": "user", "content": user})
        try:
            reply = ask(messages, problem["temp"])
        except KeyboardInterrupt:
            break
        print(f"\nUtilisateur :\n{reply}")
        messages.append({"role": "assistant", "content": reply})

    print("\nAppel terminé.")
    if replay is not None:
        print("Le ticket reste ouvert.")


def main():
    scenarios = {problem["id"]: problem for problem in PROBLEMS}
    scenarios["sql-replay"] = SQL_REPLAY
    parser = argparse.ArgumentParser(description="Simulateur d'appels support N1/N2.")
    parser.add_argument("--scenario", choices=scenarios, help="choisir un scénario précis")
    args = parser.parse_args()

    problem = scenarios[args.scenario] if args.scenario else random.choice(PROBLEMS)
    replay = SqlReplay() if args.scenario == "sql-replay" else None
    call(problem, replay)


if __name__ == "__main__":
    main()
