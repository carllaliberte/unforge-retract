# UNFORGE Retract

Withdraw a proof without erasing it.

```bash
python3 retract.py brouillon preuve.unforge.json > preuve.retrait.json
# sign materiau on private QUANTUM, same card
python3 retract.py verifier preuve.unforge.json preuve.retrait.json
```

`statut: retiré` — same card, same id, same empreinte.
The original file stays. The retract sits beside it.
Brand UNFORGE reserved. Code: Apache-2.0.
