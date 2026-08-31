#!/usr/bin/env python3
"""UNFORGE Retract — signed withdrawal, history kept."""
from __future__ import annotations
import argparse, json
from pathlib import Path
FORMAT_P, FORMAT_R = "UNFORGE-PREUVE-v1", "UNFORGE-RETRAIT-v1"
def materiau_retrait(preuve):
    return "|".join(["RETRAIT", preuve.get("id") or "", preuve.get("card_id") or "", preuve.get("empreinte") or ""])
def brouillon(preuve: Path) -> dict:
    pr = json.loads(preuve.read_text(encoding="utf-8"))
    return {"format": FORMAT_R, "marque": "UNFORGE", "preuve_id": pr.get("id"), "card_id": pr.get("card_id"), "empreinte_cible": pr.get("empreinte"), "materiau": materiau_retrait(pr), "signature": "", "note": "Sign materiau with the same card on private QUANTUM. Keep the original proof."}
def verifier(preuve: Path, retrait: Path) -> dict:
    pr = json.loads(preuve.read_text(encoding="utf-8"))
    rt = json.loads(retrait.read_text(encoding="utf-8"))
    if pr.get("format") != FORMAT_P or rt.get("format") != FORMAT_R:
        return {"ok": False, "erreur": "format"}
    ok = rt.get("card_id")==pr.get("card_id") and rt.get("preuve_id")==pr.get("id") and rt.get("empreinte_cible")==pr.get("empreinte") and rt.get("materiau")==materiau_retrait(pr)
    return {"ok": ok, "statut": "retiré" if ok else "retrait-invalide", "preuve_id": pr.get("id"), "histoire": "la preuve reste ; le retrait s'ajoute", "marque": "UNFORGE"}
def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verifier"); v.add_argument("preuve"); v.add_argument("retrait")
    b = sub.add_parser("brouillon"); b.add_argument("preuve")
    a = p.parse_args()
    if a.cmd == "brouillon":
        print(json.dumps(brouillon(Path(a.preuve)), ensure_ascii=False, indent=2)); return 0
    rec = verifier(Path(a.preuve), Path(a.retrait))
    print(json.dumps(rec, ensure_ascii=False, indent=2)); return 0 if rec.get("ok") else 1
if __name__ == "__main__":
    raise SystemExit(main())
