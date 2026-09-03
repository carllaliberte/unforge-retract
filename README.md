# UNFORGE Retract

Withdraw a proof without erasing it.

```bash
python3 retract.py examples/bienvenue.txt.unforge.json
# writes examples/bienvenue.txt.retrait.json — brouillon, same card
# sign materiau on private QUANTUM, same card
python3 retract.py examples/bienvenue.txt.unforge.json examples/bienvenue.txt.retrait.json
```

Or name the file. Retract looks for `FILE.unforge.json` beside it:

```bash
python3 retract.py examples/bienvenue.txt
python3 retract.py examples/bienvenue.txt.unforge.json --human
```

Machine record on stdout (`retract.v0`). `--human` prints `RETIRÉ` / `BROUILLON` / `REFUS`. That is not a match verdict.

`statut: retiré` — same card, same id, same empreinte.
The original file stays. The retract sits beside it.

Retract binds card fields. It does not open the signature.
Match the file with [unforge-check](https://github.com/carllaliberte/unforge-check). Check’s `VERT` means the file matches the card — not a quantum claim.
Print ids with [unforge-press](https://github.com/carllaliberte/unforge-press). `IMPRIMÉ` is paper.
Itinerary of stamps: [unforge-trail](https://github.com/carllaliberte/unforge-trail). Retract one card, not the trail file.

Agents: `python3 retract.py --schema` · `from retract import verifier` · [INTEROP.md](INTEROP.md).

No node. No cloud. No coin. This is not a seal. Not a burn.
Brand UNFORGE reserved. Code: Apache-2.0.
