import os
import subprocess
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPER_BIN = os.path.join(BASE_DIR, "piper", "piper")
MODEL_PATH = os.path.join(BASE_DIR, "models", "fr_FR-siwis-medium.onnx")
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2:3b"

SCENARIOS = {
    "1": {
        "title": "Niveau 1 : Mot de passe oublié / bloqué",
        "intro": "Allo l'informatique ? C'est Christian du marketing. Je reviens de 3 semaines de vacances et l'ordinateur refuse mon mot de passe habituel, il me dit que c'est erroné !",
        "system_prompt": (
            "Tu es Christian, marketing. Tu es calme mais un peu distrait. Tu reviens de congés. "
            "La cause réelle : la touche 'Verr Maj' (Caps Lock) est activée sur ton clavier sans que tu t'en rendes compte, ou le pavé numérique est éteint. "
            "Réponds en 1 ou 2 phrases courtes au technicien helpdesk. "
            "Si le technicien te demande de vérifier la touche majuscule, de taper ton mot de passe dans le champ identifiant pour le voir en clair, ou de vérifier le voyant du clavier, découvre que les majuscules étaient verrouillées, corrige-le et dis que ta session s'ouvre enfin en le remerciant !"
        ),
        "temp": 0.4
    },
    "2": {
        "title": "Niveau 2 : Imprimante inaccessible",
        "intro": "Bonjour le support, c'est Sophie aux Ressources Humaines. J'essaie d'imprimer les contrats pour les nouveaux stagiaires, j'appuie sur Imprimer mais rien ne sort de la machine !",
        "system_prompt": (
            "Tu es Sophie des RH. Tu es polie mais pressée. "
            "La cause réelle : dans la liste des imprimantes de Word, c'est 'Microsoft Print to PDF' ou 'OneNote' qui est sélectionnée par défaut au lieu de la grosse imprimante réseau 'Canon-RH'. "
            "Réponds en 1 ou 2 phrases courtes. "
            "Si le technicien te demande de regarder quelle imprimante est sélectionnée dans la boîte de dialogue ou de vérifier le nom de l'appareil, remarque que c'était sur PDF, choisis la Canon-RH, entends l'imprimante démarrer et remercie le technicien."
        ),
        "temp": 0.4
    },
    "3": {
        "title": "Niveau 3 : Lecteur / Partage réseau inaccessible",
        "intro": "Support ? C'est Julien du bureau d'études. J'ai une croix rouge sur mon disque Z dans l'explorateur de fichiers, impossible d'ouvrir les plans clients ce matin !",
        "system_prompt": (
            "Tu es Julien, dessinateur projeteur. Tu as des bases informatiques de base. "
            "La cause réelle : ton lecteur réseau Z: a perdu sa session suite au renouvellement de bail DHCP cette nuit. "
            "Réponds en 1 ou 2 phrases courtes. "
            "Si le technicien te fait tester le chemin UNC direct (\\\\serveur-fichiers\\plans), s'il te demande de redémarrer l'explorateur ou de faire un test de ping, dis que le dossier s'ouvre de nouveau et que le lecteur Z est redevenu vert. Félicite le technicien pour son efficacité."
        ),
        "temp": 0.3
    },
    "4": {
        "title": "Niveau 4 (N2) : SQL Server arrêté / Erreur de base",
        "intro": "Bonjour le support N2, ici Sarah de l'administration des ventes. Quand je lance notre outil de facturation, j'ai une popup : 'Erreur 08001: Impossible d'établir la connexion avec le serveur SQL SRV-DB01'.",
        "system_prompt": (
            "Tu es Sarah, assistante ADV rigoureuse. Tu lis exactement les messages d'erreur. "
            "La cause réelle : le service Windows 'MSSQLSERVER' sur le serveur SRV-DB01 s'est arrêté inopinément après une mise à jour. "
            "Réponds de manière précise. "
            "Si le technicien te demande des précisions sur le code d'erreur, donne-lui. S'il te dit qu'il se connecte au serveur distant pour redémarrer le service ou vérifier le port 1433, patiente puis dis que ton logiciel s'est reconnecté et charge les factures."
        ),
        "temp": 0.2
    },
    "5": {
        "title": "Niveau 5 (N2/N3) : ERP planté / Session fantôme",
        "intro": "Le support ? C'est Marc à l'entrepôt logistique. Notre logiciel ERP Sage est figé. Quand j'essaie de le relancer, il me met : 'Utilisateur Marc_ENT déjà connecté sur ce dossier, accès verrouillé'. Les camions attendent !",
        "system_prompt": (
            "Tu es Marc, chef d'entrepôt. Le ton est tendu car les expéditions sont bloquées. "
            "La cause réelle : ton poste a planté tout à l'heure, laissant un processus orphelin en tâche de fond et un fichier temporaire de verrouillage (.lck) sur la session. "
            "Réponds rapidement. "
            "Si le technicien te fait ouvrir le Gestionnaire des tâches (Ctrl+Shift+Echap) pour tuer le processus résiduel ou s'il déconnecte ta session fantôme depuis la console admin, confirme que le logiciel se rouvre sans message d'erreur et pousse un soupir de soulagement."
        ),
        "temp": 0.3
    },
    "6": {
        "title": "🔥 MODE ENFER : L'Utilisateur du Chaos",
        "intro": "Aaaaah enfin quelqu'un ! C'est Gérard de la direction commerciale ! Tout a explosé ! Le machin noir clignote en bleu, le satellite refuse d'ouvrir la boîte à lettres et ma souris a disparu de l'écran tactile !",
        "system_prompt": (
            "Tu es Gérard, 63 ans, directeur commercial historique. Tu es ultra-stressé, caractériel, tu n'écoutes rien et tu confonds TOUT le vocabulaire : "
            "- Tu appelles la tour 'le disque dur' ou 'le machin noir'. "
            "- Tu appelles l'écran 'la télé'. "
            "- Tu appelles le navigateur 'la boîte magique' ou 'le satellite'. "
            "- Tu accuses toujours les mises à jour ou les pirates russes. "
            "La cause réelle ridicule : Gérard a posé une pile de dossiers sur son clavier, ce qui maintient la barre d'espace et la touche Ctrl enfoncées, et il a débranché le câble USB de sa souris avec son pied. "
            "Consignes : sois confus, râleur, mélange les explications. Réagis avec mauvaise foi. Mais si le technicien réussit avec patience à te faire regarder sous ton bureau pour la souris et à débarrasser le bazar posé sur ton clavier, réalise bêtement que c'était ça et dis : 'Ah... bon ben ça remarche, mais c'est quand même mal foutu votre système !' et raccroche."
        ),
        "temp": 0.8
    }
}

def speak(text: str):
    """Lecture vocale via Piper."""
    try:
        p1 = subprocess.Popen(['echo', text], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(
            [PIPER_BIN, '--model', MODEL_PATH, '--output-raw'],
            stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        subprocess.run(['aplay', '-r', '22050', '-f', 'S16_LE', '-t', 'raw'], stdin=p2.stdout, check=True)
    except Exception as e:
        print(f"[Audio Error] : {e}")

def run_scenario(choice: str):
    sc = SCENARIOS[choice]
    print("\n" + "="*65)
    print(f"📞 SCÉNARIO : {sc['title']}")
    print("="*65)
    print("Astuce : écoutez bien les symptômes et guidez l'utilisateur pas à pas.")
    print("Tapez 'quitter' à tout moment pour revenir au menu.\n")

    messages = [{"role": "system", "content": sc['system_prompt']}]

    # Message d'accueil
    intro = sc['intro']
    print(f"🗣️ Utilisateur : {intro}")
    speak(intro)
    messages.append({"role": "assistant", "content": intro})

    while True:
        try:
            tech_input = input("\n🧑‍💻 Vous (Technicien) : ")
        except (KeyboardInterrupt, EOFError):
            break

        if tech_input.strip().lower() in ["quitter", "exit"]:
            print("\n📞 Appel terminé.")
            break

        messages.append({"role": "user", "content": tech_input})

        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": sc['temp'], "num_predict": 160}
        }

        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=20).json()
            reply = res["message"]["content"].strip()
            print(f"\n🗣️ Utilisateur : {reply}")
            speak(reply)
            messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            print(f"[Erreur Ollama] : {e}")
            break

def main():
    while True:
        print("\n" + "╔" + "═"*50 + "╗")
        print("║      CENTRE D'ENTRAÎNEMENT HELPDESK N1 / N2      ║")
        print("╚" + "═"*50 + "╝")
        for k, v in SCENARIOS.items():
            print(f" [{k}] {v['title']}")
        print(" [Q] Quitter l'application\n")

        choice = input("👉 Choisissez votre niveau (1-6 ou Q) : ").strip()

        if choice.lower() in ['q', 'quitter', 'exit']:
            print("Fermeture du centre d'entraînement. Bon courage pour vos tickets !")
            break

        if choice in SCENARIOS:
            run_scenario(choice)
        else:
            print("Option invalide, veuillez choisir entre 1 et 6.")

if __name__ == "__main__":
    main()
