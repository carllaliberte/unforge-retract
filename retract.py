#!/usr/bin/env python3
"""UNFORGE Retract — signed withdrawal, history kept.

Records a UNFORGE-RETRAIT-v1 beside a card. Does not erase the proof.
Does not open the signature. Does not sign. Not a seal. Not QUANTUM.
No node. No cloud. No coin.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FORMAT_P = "UNFORGE-PREUVE-v1"
FORMAT_R = "UNFORGE-RETRAIT-v1"
TRAIL_FORMAT = "UNFORGE-TRAIL-v1"
SCHEMA_ID = "retract.v0"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema" / "retract.v0.json"


def materiau_retrait(preuve: dict) -> str:
    """Other material. Same card. Signed on QUANTUM, not here."""
    return "|".join(
        [
            "RETRAIT",
            preuve.get("id") or "",
            preuve.get("card_id") or "",
            preuve.get("empreinte") or "",
        ]
    )


def voisin_carte(fichier: Path) -> Path:
    """Card that sits beside a file: FILE.unforge.json."""
    if fichier.name.endswith(".unforge.json") or fichier.name.endswith(".unforge-trail.json"):
        return fichier
    return Path(str(fichier) + ".unforge.json")


def dest_defaut(preuve: Path) -> Path:
    """Withdrawal that sits beside the card: FILE.retrait.json."""
    name = preuve.name
    if name.endswith(".unforge.json"):
        return preuve.with_name(name[: -len(".unforge.json")] + ".retrait.json")
    return preuve.with_name(name + ".retrait.json")


def voisin_retrait(preuve: Path) -> Path | None:
    """FILE.retrait.json, or FILE.unforge.json.retrait.json (trail)."""
    for c in (dest_defaut(preuve), Path(str(preuve) + ".retrait.json")):
        if c.is_file():
            return c
    return None


def resoudre(chemin: Path) -> Path:
    """Accept a card, or a file whose card sits beside it."""
    if chemin.name.endswith(".unforge.json") or chemin.name.endswith(".unforge-trail.json"):
        if not chemin.is_file():
            raise FileNotFoundError("preuve introuvable")
        return chemin
    voisin = voisin_carte(chemin)
    if voisin.is_file():
        return voisin
    raise FileNotFoundError("preuve introuvable")


def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def phrase_retract(rec: dict) -> str:
    err = rec.get("erreur")
    phrases = {
        "format": "pas UNFORGE-PREUVE-v1.",
        "format retrait": "pas UNFORGE-RETRAIT-v1.",
        "itinéraire": "ceci est un itinéraire. Retire une carte .unforge.json.",
        "preuve introuvable": "preuve introuvable.",
        "retrait introuvable": "retrait introuvable.",
        "json": "JSON illisible.",
        "existe": "un retrait est déjà là. l'histoire reste.",
        "liaison": "le retrait ne nomme pas cette carte.",
        "materiau": "le matériau n'est pas RETRAIT|id|card|empreinte.",
    }
    if err in phrases:
        return phrases[err]
    if rec.get("ok") and rec.get("statut") == "brouillon":
        return "brouillon inscrit. signer le matériau sur QUANTUM. la preuve reste."
    if rec.get("ok"):
        return "retrait lié. la preuve reste ; le retrait s'ajoute."
    if err:
        return str(err)
    return "refus."


def habiller(rec: dict) -> dict:
    rec.setdefault("geste", "retract")
    rec.setdefault("marque", "UNFORGE")
    rec.setdefault("noeud", "non requis")
    rec.setdefault("schema", SCHEMA_ID)
    rec.setdefault("signature_ouverte", False)
    rec.setdefault("histoire", "la preuve reste ; le retrait s'ajoute")
    rec["phrase"] = phrase_retract(rec)
    return rec


def brouillon(preuve: Path) -> dict:
    """UNFORGE-RETRAIT-v1 card. Signature stays empty — QUANTUM fills it."""
    paquet = json.loads(preuve.read_text(encoding="utf-8"))
    if paquet.get("format") == TRAIL_FORMAT:
        raise ValueError("itinéraire")
    if paquet.get("format") != FORMAT_P:
        raise ValueError("format")
    rec = {
        "format": FORMAT_R,
        "marque": "UNFORGE",
        "preuve_id": paquet.get("id"),
        "card_id": paquet.get("card_id"),
        "token_id": paquet.get("token_id"),
        "empreinte": paquet.get("empreinte"),
        "empreinte_cible": paquet.get("empreinte"),
        "materiau": materiau_retrait(paquet),
        "signature": "",
        "note": "Sign materiau with the same card on private QUANTUM. Keep the original proof.",
    }
    for cle in ("card_label", "card_public", "card_public_pq"):
        if cle in paquet:
            rec[cle] = paquet.get(cle)
    return rec


def _cible(retrait: dict) -> str | None:
    return retrait.get("empreinte_cible") or retrait.get("empreinte")


def _liaison(preuve: dict, retrait: dict) -> tuple[bool, bool]:
    memes = (
        retrait.get("preuve_id") == preuve.get("id")
        and retrait.get("card_id") == preuve.get("card_id")
        and _cible(retrait) == preuve.get("empreinte")
    )
    if "token_id" in retrait and retrait.get("token_id") != preuve.get("token_id"):
        memes = False
    if "card_public" in retrait and retrait.get("card_public") != preuve.get("card_public"):
        memes = False
    attendu = materiau_retrait(preuve)
    mat_ok = (retrait.get("materiau") or "") == attendu
    return bool(memes), bool(mat_ok)


def inscrire(preuve: Path, dest: Path | None = None) -> dict:
    """Write a brouillon beside the card. Never overwrites. Never signs."""
    try:
        paquet = json.loads(preuve.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return habiller({"ok": False, "erreur": "json", "detail": str(e)})
    if paquet.get("format") == TRAIL_FORMAT:
        return habiller({"ok": False, "erreur": "itinéraire"})
    if paquet.get("format") != FORMAT_P:
        return habiller({"ok": False, "erreur": "format"})
    carte = brouillon(preuve)
    cible = dest if dest is not None else dest_defaut(preuve)
    if cible.is_file():
        return habiller(
            {
                "ok": False,
                "erreur": "existe",
                "preuve_id": paquet.get("id"),
                "card_id": paquet.get("card_id"),
                "empreinte": paquet.get("empreinte"),
                "retract": str(cible),
                "statut": "existe",
            }
        )
    cible.write_text(json.dumps(carte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return habiller(
        {
            "ok": True,
            "preuve_id": carte.get("preuve_id"),
            "card_id": carte.get("card_id"),
            "token_id": carte.get("token_id"),
            "empreinte": carte.get("empreinte"),
            "materiau": carte.get("materiau"),
            "signe": False,
            "statut": "brouillon",
            "retract": str(cible),
        }
    )


def verifier(preuve: Path, retrait: Path) -> dict:
    """Bind a withdrawal to the card. Does not open the signature."""
    try:
        pr = json.loads(preuve.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return habiller({"ok": False, "erreur": "json", "detail": str(e)})
    try:
        rt = json.loads(retrait.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return habiller({"ok": False, "erreur": "json", "detail": str(e)})
    if pr.get("format") == TRAIL_FORMAT:
        return habiller({"ok": False, "erreur": "itinéraire"})
    if pr.get("format") != FORMAT_P:
        return habiller({"ok": False, "erreur": "format"})
    if rt.get("format") != FORMAT_R:
        return habiller({"ok": False, "erreur": "format retrait"})
    memes, mat_ok = _liaison(pr, rt)
    if not memes:
        err = "liaison"
    elif not mat_ok:
        err = "materiau"
    else:
        err = None
    ok = err is None
    signe = bool(rt.get("signature"))
    rec: dict = {
        "ok": ok,
        "preuve_id": pr.get("id"),
        "card_id": pr.get("card_id"),
        "token_id": pr.get("token_id"),
        "empreinte": pr.get("empreinte"),
        "memes": memes,
        "materiau_ok": mat_ok,
        "materiau": materiau_retrait(pr),
        "signe": signe,
        "statut": "retiré" if ok else "retrait-invalide",
        "retract": str(retrait),
    }
    if err:
        rec["erreur"] = err
    return habiller(rec)


def ligne_humaine(rec: dict) -> str:
    """RETIRÉ / BROUILLON / REFUS. Not VERT. Not IMPRIMÉ."""
    if rec.get("ok") and rec.get("statut") == "brouillon":
        bits = [x for x in ("BROUILLON", rec.get("preuve_id"), rec.get("retract")) if x]
        return "  ".join(str(b) for b in bits)
    if rec.get("ok"):
        bits = [x for x in ("RETIRÉ", rec.get("preuve_id"), "la preuve reste") if x]
        return "  ".join(str(b) for b in bits)
    return f"REFUS  {rec.get('phrase')}"


def _émettre(rec: dict, human: bool) -> None:
    if human:
        print(ligne_humaine(rec))
    else:
        print(json.dumps(rec, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="retract.py",
        description=(
            "UNFORGE Retract — record a signed withdrawal beside a published proof. "
            "History stays. No node. No cloud. No coin. Does not open the signature."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python3 retract.py document.pdf.unforge.json\n"
            "  python3 retract.py document.pdf\n"
            "  python3 retract.py document.pdf.unforge.json document.pdf.retrait.json\n"
            "  python3 retract.py brouillon document.pdf.unforge.json\n"
            "  python3 retract.py verifier document.pdf.unforge.json document.pdf.retrait.json\n"
            "\n"
            "One path writes FILE.retrait.json (brouillon) if none sits beside the card.\n"
            "If a retract is already there, the same command binds it — it does not overwrite.\n"
            "Exit 0 = recorded or bound. Exit 1 = refuse. Exit 2 = unreadable.\n"
            "ok: true is a withdrawal binding, not a file match (check) and not a print (press).\n"
            "Agents: python3 retract.py --schema   or   from retract import verifier"
        ),
    )
    p.add_argument(
        "paths",
        nargs="*",
        metavar="FILE",
        help="card .unforge.json, a file whose card sits beside it, optional .retrait.json",
    )
    p.add_argument("-o", "--out", help="destination retract (default: FILE.retrait.json)")
    p.add_argument("--schema", action="store_true", help="print retract.v0 JSON Schema and exit")
    sortie = p.add_mutually_exclusive_group()
    sortie.add_argument("--json", action="store_true", help="machine record on stdout (default)")
    sortie.add_argument(
        "--human",
        action="store_true",
        help="one RETIRÉ / BROUILLON / REFUS line — not a match, not a print",
    )
    args = p.parse_args(argv)

    if args.schema:
        try:
            print(json.dumps(schema(), ensure_ascii=False, indent=2))
        except Exception as e:
            print(json.dumps({"ok": False, "erreur": str(e)}, ensure_ascii=False, indent=2))
            return 2
        return 0

    paths = list(args.paths)
    if paths and paths[0] == "brouillon":
        if len(paths) < 2:
            p.error("brouillon needs a .unforge.json")
        try:
            preuve = resoudre(Path(paths[1]))
            carte = brouillon(preuve)
        except FileNotFoundError:
            rec = habiller({"ok": False, "erreur": "preuve introuvable"})
            _émettre(rec, args.human)
            return 2
        except json.JSONDecodeError as e:
            rec = habiller({"ok": False, "erreur": "json", "detail": str(e)})
            _émettre(rec, args.human)
            return 2
        except ValueError as e:
            rec = habiller({"ok": False, "erreur": str(e)})
            _émettre(rec, args.human)
            return 1
        print(json.dumps(carte, ensure_ascii=False, indent=2))
        return 0

    if paths and paths[0] == "verifier":
        if len(paths) < 3:
            p.error("verifier needs preuve and retrait")
        paths = paths[1:]

    if not paths:
        p.error("drop a .unforge.json card, or a file whose card sits beside it")

    try:
        preuve = resoudre(Path(paths[0]))
        if len(paths) >= 2:
            retrait = Path(paths[1])
            if not retrait.is_file():
                rec = habiller({"ok": False, "erreur": "retrait introuvable", "attendu": str(retrait)})
                _émettre(rec, args.human)
                return 2
            rec = verifier(preuve, retrait)
        else:
            existing = voisin_retrait(preuve)
            if existing is not None and not args.out:
                rec = verifier(preuve, existing)
            else:
                dest = Path(args.out) if args.out else None
                rec = inscrire(preuve, dest)
    except FileNotFoundError:
        attendu = str(voisin_carte(Path(paths[0])))
        rec = habiller({"ok": False, "erreur": "preuve introuvable", "attendu": attendu})
        _émettre(rec, args.human)
        return 2
    except json.JSONDecodeError as e:
        rec = habiller({"ok": False, "erreur": "json", "detail": str(e)})
        _émettre(rec, args.human)
        return 2
    except OSError as e:
        rec = habiller({"ok": False, "erreur": str(e)})
        _émettre(rec, args.human)
        return 2

    _émettre(rec, args.human)
    if rec.get("erreur") == "json":
        return 2
    return 0 if rec.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
