import subprocess
import sys
import unittest
from pathlib import Path


HELPDESK = Path(__file__).resolve().parents[1] / "helpdesk.py"


class SqlReplayTest(unittest.TestCase):
    def play(self, *actions):
        result = subprocess.run(
            [sys.executable, str(HELPDESK), "--scenario", "sql-replay"],
            input="\n".join(actions) + "\n",
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
            timeout=5,
        )
        return result.stdout

    def test_failed_verification_and_port_check_leave_ticket_open(self):
        output = self.play("/facturation", "/port", "/cloturer", "fin")

        self.assertIn("Test fonctionnel échoué", output)
        self.assertIn("1433 : inaccessible", output)
        self.assertIn("Ticket ouvert", output)
        self.assertNotIn("Ticket résolu", output)

    def test_closing_requires_a_successful_functional_check_after_recovery(self):
        output = self.play(
            "/service", "/facturation", "/relancer", "/port", "/cloturer",
            "/facturation", "/cloturer",
        )

        self.assertIn("MSSQLSERVER : arrêté", output)
        self.assertIn("1433 : accessible", output)
        self.assertEqual(output.count("Ticket ouvert"), 1)
        self.assertEqual(output.count("Ticket résolu"), 1)
        self.assertLess(output.index("Ticket ouvert"), output.index("Test fonctionnel réussi"))
        self.assertLess(output.index("Test fonctionnel réussi"), output.index("Ticket résolu"))
