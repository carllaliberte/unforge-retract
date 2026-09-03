# Interop — no server

Other agents and tools record a withdrawal with a local process. No node. No cloud. No coin. Nothing here signs.

Retract binds a `UNFORGE-RETRAIT-v1` to a `UNFORGE-PREUVE-v1` card. It does not merge [check](https://github.com/carllaliberte/unforge-check), [press](https://github.com/carllaliberte/unforge-press), or [trail](https://github.com/carllaliberte/unforge-trail). The card is the join:

| Rail | What it does with the card |
|---|---|
| Retract | withdrawal sits beside the proof; history stays |
| Check | one card — empreinte + signature + file (`VERT` = match) |
| Press | print ids (`IMPRIMÉ` = paper, not a match) |
| Trail | itinerary — same SHA-256, each `id` burned once |

## Command

```bash
python3 retract.py FILE.unforge.json
python3 retract.py FILE
python3 retract.py FILE.unforge.json FILE.retrait.json
python3 retract.py --schema
```

`FILE` alone looks for `FILE.unforge.json` beside it.
One path writes `FILE.retrait.json` when none sits there.
If a retract is already there, the same command binds it. It does not overwrite.

## Python

```python
from pathlib import Path
from retract import verifier, brouillon, inscrire, schema

carte = brouillon(Path("doc.pdf.unforge.json"))
assert carte["format"] == "UNFORGE-RETRAIT-v1"
assert carte["signature"] == ""          # QUANTUM fills this

rec = verifier(Path("doc.pdf.unforge.json"), Path("doc.pdf.retrait.json"))
assert rec["ok"] is True                 # binding, not a file match
assert rec["geste"] == "retract"
assert rec["signature_ouverte"] is False
schema()                                 # retract.v0
```

`materiau_retrait`, `resoudre`, `voisin_retrait`, `inscrire` stay importable.

## Exit

| Code | Meaning |
|---|---|
| 0 | recorded or bound (`ok: true`) |
| 1 | refuse (format, itinerary, liaison, materiau, already there) |
| 2 | unreadable (missing path, bad JSON) |

`ok: true` is a **withdrawal binding**. It is not a file match ([unforge-check](https://github.com/carllaliberte/unforge-check) `VERT`). It is not a print ([unforge-press](https://github.com/carllaliberte/unforge-press) `IMPRIMÉ`). A trail itinerary is refused here — retract one card.

## Record

JSON on stdout. Shape: `schema/retract.v0.json`. Stable keys: `ok`, `geste`, `schema`, `preuve_id`, `card_id`, `token_id`, `empreinte`, `statut`, `histoire`, `signe`, `signature_ouverte`, `marque`, `noeud`, `phrase`. Extra keys may appear. `--human` prints `RETIRÉ` / `BROUILLON` / `REFUS` — not `VERT`, not `IMPRIMÉ`.

`empreinte` and `empreinte_cible` are copied from the card. They are not recomputed.
`materiau` is `RETRAIT|{id}|{card_id}|{empreinte}`. QUANTUM signs it. This repo does not open the signature.

## Card (the join)

A retract file is `UNFORGE-RETRAIT-v1`. Trail looks for `preuve_id`, `card_id`, and `empreinte_cible` (or `empreinte`) beside a stamp. Check may later open `signature` on the same `card_public`. Press prints the proof, not the retract.

## Do not

Stand up a server. Open `quantum.db`. Invent a signature. Call this a coin. Call this a seal. Call this a burn. Vendor famille, garde, check, press, or trail. Merge those repos here.
