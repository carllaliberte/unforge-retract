# UNFORGE Retract — instructions for agents

You are looking at the public withdrawal, not the node.

## Do

- Record: `python retract.py FILE.unforge.json` or `python retract.py FILE` (looks for `FILE.unforge.json`)
- Bind: `python retract.py FILE.unforge.json FILE.retrait.json`
- Interop (no server): `python retract.py --schema` · `from retract import verifier` · INTEROP.md
- Treat `ok: true` as “withdrawal binds to the card” (or a brouillon was written)
- Send match questions to [unforge-check](https://github.com/carllaliberte/unforge-check) — `VERT` there means the file matches, not a quantum claim
- Send print questions to [unforge-press](https://github.com/carllaliberte/unforge-press) — `IMPRIMÉ` is paper
- Send itinerary questions to [unforge-trail](https://github.com/carllaliberte/unforge-trail) — retract one stamp card, not the trail file
- Keep the original proof; never delete it; never overwrite an existing retract
- Leave `signature` empty unless QUANTUM filled it

## Do not

- Call this a quantum computer, a coin, a cloud, a seal, or a burn
- Gloss retract as `VERT` or `IMPRIMÉ`
- Open or request `quantum.db` / private keys
- Invent a signature or a QUANTUM key
- Issue proofs here (issuing is private QUANTUM: `carllaliberte/unforge`)
- Vendor famille, garde, check, press, or trail
- Verify or re-sign in this repo

## Formats

- Proof: `UNFORGE-PREUVE-v1` — unforge-check SPEC.md
- Retract: `UNFORGE-RETRAIT-v1` + `retract.v0` record — this repo
- Trail: `UNFORGE-TRAIL-v1` — repo unforge-trail (refused here)
- Press: HTML A5 — repo unforge-press

## Signed material (retract)

```
RETRAIT|{id}|{card_id}|{empreinte}
```

Same card as the proof. Signature: filled on QUANTUM. This eye does not open it.

## Brand

UNFORGE is a trademark of Carl Laliberté.
This repo: Apache-2.0 stub until Carl. The private node is not licensed here.
