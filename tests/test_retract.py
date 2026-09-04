#!/usr/bin/env python3
"""UNFORGE Retract — withdrawal beside the card. History stays. Signature stays closed."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from retract import (  # noqa: E402
    FORMAT_R,
    SCHEMA_ID,
    brouillon,
    dest_defaut,
    habiller,
    inscrire,
    ligne_humaine,
    materiau_retrait,
    phrase_retract,
    resoudre,
    schema,
    verifier,
    voisin_carte,
    voisin_retrait,
)

FICHIER = ROOT / "examples" / "bienvenue.txt"
CARTE = ROOT / "examples" / "bienvenue.txt.unforge.json"
RETRAIT = ROOT / "examples" / "bienvenue.txt.retrait.json"
PY = [sys.executable, str(ROOT / "retract.py")]


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(PY + args, capture_output=True, text=True, cwd=str(ROOT))


def _paquet() -> dict:
    return json.loads(CARTE.read_text(encoding="utf-8"))


class CarteDemo(unittest.TestCase):
    def test_demo_a_les_clefs_check_press_trail(self):
        p = _paquet()
        for cle in (
            "format",
            "marque",
            "id",
            "card_id",
            "card_public",
            "token_id",
            "empreinte",
            "signature",
            "fait",
            "created_at",
        ):
            self.assertIn(cle, p)
        self.assertEqual(p["format"], "UNFORGE-PREUVE-v1")
        self.assertEqual(p["id"], "QT-PR-DEMO0001")
        self.assertEqual(p["objet"]["sha256"], "e8fe730c49dc859358e3b94376fb0a5f0916aca21b18457eb3d8391c4ebc0838")
        self.assertEqual(FICHIER.stat().st_size, 92)
        self.assertEqual(p["objet"]["octets"], 92)
        self.assertIn("Not Carl's node", p["note"])

    def test_retrait_demo_est_brouillon(self):
        rt = json.loads(RETRAIT.read_text(encoding="utf-8"))
        self.assertEqual(rt["format"], FORMAT_R)
        self.assertEqual(rt["preuve_id"], "QT-PR-DEMO0001")
        self.assertEqual(rt["card_id"], "QT-EM-DEMO0001")
        self.assertEqual(rt["empreinte_cible"], _paquet()["empreinte"])
        self.assertEqual(rt["empreinte"], _paquet()["empreinte"])
        self.assertEqual(rt["materiau"], materiau_retrait(_paquet()))
        self.assertEqual(rt["signature"], "")
        self.assertIn("Not Carl's node", rt["note"])


class Materiau(unittest.TestCase):
    def test_ligne_retrait(self):
        self.assertEqual(
            materiau_retrait(_paquet()),
            "RETRAIT|QT-PR-DEMO0001|QT-EM-DEMO0001|985d3ff3389f8c64c87eeb829ccebf4ae09b943fd3500e442614b1e1731498e5",
        )

    def test_brouillon_ne_signe_pas(self):
        carte = brouillon(CARTE)
        self.assertEqual(carte["format"], FORMAT_R)
        self.assertEqual(carte["signature"], "")
        self.assertEqual(carte["token_id"], "QT-JK-DEMO0001")
        self.assertEqual(carte["card_public"], _paquet()["card_public"])
        self.assertNotIn("VERT", json.dumps(carte))
        self.assertNotIn("IMPRIMÉ", json.dumps(carte))


class Bind(unittest.TestCase):
    def test_fixture_lie(self):
        rec = verifier(CARTE, RETRAIT)
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["geste"], "retract")
        self.assertEqual(rec["schema"], SCHEMA_ID)
        self.assertEqual(rec["statut"], "retiré")
        self.assertTrue(rec["memes"])
        self.assertTrue(rec["materiau_ok"])
        self.assertFalse(rec["signe"])
        self.assertFalse(rec["signature_ouverte"])
        self.assertEqual(rec["histoire"], "la preuve reste ; le retrait s'ajoute")
        self.assertEqual(rec["noeud"], "non requis")
        self.assertIn("reste", rec["phrase"])
        self.assertIn("à côté de la carte", rec["phrase"])

    def test_preuve_inchangee(self):
        avant = CARTE.read_bytes()
        rec = verifier(CARTE, RETRAIT)
        self.assertTrue(rec["ok"])
        self.assertEqual(CARTE.read_bytes(), avant)

    def test_mauvais_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            faux = Path(tmp) / "x.retrait.json"
            rt = json.loads(RETRAIT.read_text(encoding="utf-8"))
            rt["preuve_id"] = "OTHER"
            faux.write_text(json.dumps(rt), encoding="utf-8")
            rec = verifier(CARTE, faux)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["erreur"], "liaison")
        self.assertEqual(rec["statut"], "retrait-invalide")

    def test_mauvais_materiau(self):
        with tempfile.TemporaryDirectory() as tmp:
            faux = Path(tmp) / "x.retrait.json"
            rt = json.loads(RETRAIT.read_text(encoding="utf-8"))
            rt["materiau"] = "REGISTRE|x"
            faux.write_text(json.dumps(rt), encoding="utf-8")
            rec = verifier(CARTE, faux)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["erreur"], "materiau")
        self.assertFalse(rec["materiau_ok"])

    def test_token_divergent(self):
        with tempfile.TemporaryDirectory() as tmp:
            faux = Path(tmp) / "x.retrait.json"
            rt = json.loads(RETRAIT.read_text(encoding="utf-8"))
            rt["token_id"] = "QT-JK-OTHER"
            faux.write_text(json.dumps(rt), encoding="utf-8")
            rec = verifier(CARTE, faux)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["erreur"], "liaison")

    def test_trail_minimal_sans_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            mini = Path(tmp) / "x.retrait.json"
            mini.write_text(
                json.dumps(
                    {
                        "format": FORMAT_R,
                        "preuve_id": "QT-PR-DEMO0001",
                        "card_id": "QT-EM-DEMO0001",
                        "empreinte_cible": _paquet()["empreinte"],
                        "materiau": materiau_retrait(_paquet()),
                    }
                ),
                encoding="utf-8",
            )
            rec = verifier(CARTE, mini)
        self.assertTrue(rec["ok"], "trail-shaped retract with materiau still binds")

    def test_format_retrait(self):
        with tempfile.TemporaryDirectory() as tmp:
            faux = Path(tmp) / "x.retrait.json"
            faux.write_text(json.dumps({"format": "NON"}), encoding="utf-8")
            rec = verifier(CARTE, faux)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["erreur"], "format retrait")


class Inscrire(unittest.TestCase):
    def test_ecrit_sans_effacer(self):
        with tempfile.TemporaryDirectory() as tmp:
            preuve = Path(tmp) / "doc.unforge.json"
            preuve.write_text(CARTE.read_text(encoding="utf-8"), encoding="utf-8")
            avant = preuve.read_bytes()
            rec = inscrire(preuve)
            self.assertTrue(rec["ok"])
            self.assertEqual(rec["statut"], "brouillon")
            dest = Path(rec["retract"])
            self.assertTrue(dest.is_file())
            self.assertEqual(dest.name, "doc.retrait.json")
            self.assertEqual(preuve.read_bytes(), avant)
            carte = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(carte["signature"], "")
            self.assertEqual(carte["materiau"], materiau_retrait(_paquet()))
            again = inscrire(preuve)
            self.assertFalse(again["ok"])
            self.assertEqual(again["erreur"], "existe")
            self.assertEqual(dest.read_bytes(), dest.read_bytes())
            self.assertEqual(preuve.read_bytes(), avant)

    def test_itineraire_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            trail = Path(tmp) / "x.unforge-trail.json"
            trail.write_text(json.dumps({"format": "UNFORGE-TRAIL-v1", "etapes": []}), encoding="utf-8")
            rec = inscrire(trail)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["erreur"], "itinéraire")

    def test_dest_defaut(self):
        self.assertEqual(dest_defaut(Path("doc.pdf.unforge.json")).name, "doc.pdf.retrait.json")
        self.assertEqual(voisin_carte(FICHIER), CARTE)
        self.assertEqual(resoudre(FICHIER), CARTE)
        self.assertEqual(resoudre(CARTE), CARTE)
        self.assertEqual(voisin_retrait(CARTE), RETRAIT)
        with self.assertRaises(FileNotFoundError):
            resoudre(ROOT / "README.md")


class SchemaEtHabit(unittest.TestCase):
    def test_schema_fichier(self):
        s = schema()
        self.assertEqual(s["title"], "unforge.retract.v0")
        self.assertIn("ok", s["required"])
        self.assertIn("geste", s["required"])
        desc = s["description"].lower()
        self.assertIn("history stays", desc)
        self.assertIn("unforge-check", desc)
        self.assertIn("unforge-press", desc)

    def test_habiller_erreur(self):
        rec = habiller({"ok": False, "erreur": "json"})
        self.assertEqual(rec["geste"], "retract")
        self.assertEqual(phrase_retract(rec), "JSON illisible.")
        self.assertFalse(rec["signature_ouverte"])

    def test_humain_n_est_pas_vert_ni_imprime(self):
        rec = verifier(CARTE, RETRAIT)
        ligne = ligne_humaine(rec)
        self.assertIn("RETIRÉ", ligne)
        self.assertNotIn("VERT", ligne)
        self.assertNotIn("ROUGE", ligne)
        self.assertNotIn("IMPRIMÉ", ligne)
        brou = habiller({"ok": True, "statut": "brouillon", "preuve_id": "QT-PR-DEMO0001", "retract": "x.retrait.json"})
        self.assertIn("BROUILLON", ligne_humaine(brou))
        self.assertNotIn("VERT", ligne_humaine(brou))


class CLI(unittest.TestCase):
    def test_verifier_exit_0(self):
        r = _run([str(CARTE), str(RETRAIT)])
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["geste"], "retract")
        self.assertEqual(rec["schema"], SCHEMA_ID)
        self.assertEqual(rec["statut"], "retiré")

    def test_voisin_une_commande(self):
        r = _run([str(FICHIER)])
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["preuve_id"], "QT-PR-DEMO0001")
        self.assertEqual(rec["statut"], "retiré")

    def test_subcommand_verifier(self):
        r = _run(["verifier", str(CARTE), str(RETRAIT)])
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertTrue(rec["ok"])

    def test_subcommand_brouillon(self):
        r = _run(["brouillon", str(CARTE)])
        self.assertEqual(r.returncode, 0, r.stderr)
        carte = json.loads(r.stdout)
        self.assertEqual(carte["format"], FORMAT_R)
        self.assertEqual(carte["signature"], "")
        self.assertTrue(carte["materiau"].startswith("RETRAIT|"))

    def test_inscrire_tmp(self):
        with tempfile.TemporaryDirectory() as tmp:
            preuve = Path(tmp) / "doc.unforge.json"
            preuve.write_text(CARTE.read_text(encoding="utf-8"), encoding="utf-8")
            dest = Path(tmp) / "out.retrait.json"
            r = _run([str(preuve), "-o", str(dest)])
            self.assertEqual(r.returncode, 0, r.stderr)
            rec = json.loads(r.stdout)
            self.assertTrue(rec["ok"])
            self.assertEqual(rec["statut"], "brouillon")
            self.assertTrue(dest.is_file())
            self.assertEqual(preuve.read_text(encoding="utf-8"), CARTE.read_text(encoding="utf-8"))
            again = _run([str(preuve), "-o", str(dest)])
            self.assertEqual(again.returncode, 1)
            self.assertEqual(json.loads(again.stdout)["erreur"], "existe")

    def test_human(self):
        r = _run([str(CARTE), str(RETRAIT), "--human"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("RETIRÉ", r.stdout)
        self.assertIn("QT-PR-DEMO0001", r.stdout)
        self.assertNotIn("VERT", r.stdout)
        self.assertNotIn("IMPRIMÉ", r.stdout)
        self.assertNotIn("{", r.stdout)

    def test_schema_flag(self):
        r = _run(["--schema"])
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["title"], "unforge.retract.v0")

    def test_sans_args(self):
        r = _run([])
        self.assertEqual(r.returncode, 2)
        self.assertIn(".unforge.json", r.stderr)

    def test_format_exit_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            faux = Path(tmp) / "x.unforge.json"
            faux.write_text(json.dumps({"format": "NON"}), encoding="utf-8")
            dest = Path(tmp) / "x.retrait.json"
            r = _run([str(faux), "-o", str(dest)])
        self.assertEqual(r.returncode, 1)
        rec = json.loads(r.stdout)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["erreur"], "format")

    def test_itineraire_exit_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            trail = Path(tmp) / "x.unforge-trail.json"
            trail.write_text(json.dumps({"format": "UNFORGE-TRAIL-v1", "etapes": []}), encoding="utf-8")
            r = _run([str(trail)])
        self.assertEqual(r.returncode, 1)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["erreur"], "itinéraire")

    def test_carte_absente(self):
        with tempfile.TemporaryDirectory() as tmp:
            seul = Path(tmp) / "orphelin.txt"
            seul.write_text("x", encoding="utf-8")
            r = _run([str(seul)])
        self.assertEqual(r.returncode, 2)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["erreur"], "preuve introuvable")

    def test_json_illisible(self):
        with tempfile.TemporaryDirectory() as tmp:
            mauvais = Path(tmp) / "x.unforge.json"
            mauvais.write_text("{", encoding="utf-8")
            dest = Path(tmp) / "out.retrait.json"
            r = _run([str(mauvais), "-o", str(dest)])
        self.assertEqual(r.returncode, 2)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["erreur"], "json")

    def test_liaison_exit_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            faux = Path(tmp) / "x.retrait.json"
            rt = json.loads(RETRAIT.read_text(encoding="utf-8"))
            rt["card_id"] = "QT-EM-OTHER"
            faux.write_text(json.dumps(rt), encoding="utf-8")
            r = _run([str(CARTE), str(faux)])
        self.assertEqual(r.returncode, 1)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["erreur"], "liaison")


class DoorCopy(unittest.TestCase):
    """Public door: withdrawal beside the card. ok:true is a field bind."""

    DOORS = (
        ROOT / "README.md",
        ROOT / "INTEROP.md",
        ROOT / "SPEC.md",
        ROOT / "PREVIEW.md",
        ROOT / "examples" / "README.md",
        ROOT / "retract.py",
        ROOT / "schema" / "retract.v0.json",
    )

    def _text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def _doors(self) -> str:
        return "\n".join(self._text(p) for p in self.DOORS)

    def test_readme_leads_withdrawal_beside_the_card(self):
        readme = self._text(ROOT / "README.md")
        lead = readme.split("```", 1)[0]
        self.assertIn("Withdrawal beside the card", lead)
        self.assertIn("ok: true", readme)
        self.assertIn("fields bind", readme)
        self.assertIn("card shape holds", readme)
        self.assertIn("not a QUANTUM signature", readme)

    def test_help_is_withdrawal_beside_the_card(self):
        r = _run(["--help"])
        self.assertEqual(r.returncode, 0, r.stderr)
        help_txt = r.stdout
        self.assertIn("withdrawal beside the card", help_txt)
        self.assertIn("field bind", help_txt)
        self.assertIn("card shape holds", help_txt)
        self.assertNotIn("signed withdrawal", help_txt.lower())

    def test_doors_say_withdrawal_beside_the_card(self):
        for path in self.DOORS:
            text = self._text(path)
            self.assertIn(
                "withdrawal beside the card",
                text.lower(),
                f"{path.name} must say withdrawal beside the card",
            )
            self.assertNotIn("signed withdrawal", text.lower(), path.name)
            self.assertNotIn("Imagine", text)
            self.assertNotIn("formally verified", text.lower())

    def test_ok_true_is_field_bind_not_quantum_signature(self):
        rec = verifier(CARTE, RETRAIT)
        self.assertTrue(rec["ok"])
        self.assertFalse(rec["signe"])
        self.assertFalse(rec["signature_ouverte"])
        self.assertEqual(json.loads(RETRAIT.read_text(encoding="utf-8"))["signature"], "")
        self.assertIn("à côté de la carte", rec["phrase"])
        self.assertIn("champs lient", rec["phrase"])

        interop = self._text(ROOT / "INTEROP.md")
        self.assertIn("field bind", interop)
        self.assertIn("card shape holds", interop)
        self.assertIn("not a QUANTUM signature", interop)

        schema_txt = self._text(ROOT / "schema" / "retract.v0.json")
        self.assertIn("field bind", schema_txt)
        self.assertIn("card shape holds", schema_txt)
        self.assertIn("Not a QUANTUM signature", schema_txt)

        doors = self._doors().lower()
        self.assertNotIn("signed quantum withdrawal", doors)
        self.assertNotIn("ok: true is a signed", doors)
        self.assertNotIn("ok: true means quantum signed", doors)

    def test_schema_ok_is_field_bind(self):
        s = schema()
        desc = s["description"].lower()
        ok = s["properties"]["ok"]["description"].lower()
        self.assertIn("withdrawal beside the card", desc)
        self.assertIn("field bind", desc)
        self.assertIn("card shape holds", desc)
        self.assertIn("not a quantum signature", desc)
        self.assertIn("fields bind", ok)
        self.assertIn("card shape holds", ok)
        self.assertIn("not a quantum signature", ok)
        self.assertNotIn("imagine", desc)
        self.assertNotIn("formally verified", desc)


if __name__ == "__main__":
    unittest.main()
