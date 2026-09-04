# Example

Withdrawal beside the card. The retract fixture is an unsigned brouillon.

```bash
python3 retract.py examples/bienvenue.txt.unforge.json
python3 retract.py examples/bienvenue.txt
python3 retract.py examples/bienvenue.txt.unforge.json examples/bienvenue.txt.retrait.json
```

Same demo card as [unforge-check](https://github.com/carllaliberte/unforge-check) / [unforge-press](https://github.com/carllaliberte/unforge-press) / [unforge-trail](https://github.com/carllaliberte/unforge-trail): `QT-PR-DEMO0001`.
Ed25519-only so CI stays small. Not Carl's node.
The retract fixture is an unsigned brouillon. QUANTUM signs the materiau. This repo does not.
