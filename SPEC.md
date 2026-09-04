# UNFORGE-RETRAIT-v1

Withdrawal beside the card.

A retract is a JSON file named `*.retrait.json` sitting beside the `*.unforge.json` it withdraws.

The proof stays. The retract is added. This is a withdrawal, not a delete, not a burn, not a consume.

Card format: `UNFORGE-PREUVE-v1` — see [unforge-check SPEC](https://github.com/carllaliberte/unforge-check/blob/main/SPEC.md).

Required keys on the retract: `format`, `marque`, `preuve_id`, `card_id`, `empreinte_cible`, `materiau`.

`empreinte` is written too — same value — so check and trail can join on either name.

Signed material (UTF-8), other than the proof's `REGISTRE` line:

    RETRAIT|{id}|{card_id}|{empreinte}

QUANTUM signs that materiau with the same card. This repo does not sign. This repo does not open the signature.

Roles:

- QUANTUM signs (private keys stay home). Not this repo.
- Check re-verifies Ed or `UFHY1` + file SHA-256. `VERT` = match.
- Press does not open the signature; it prints ids. `IMPRIMÉ` = paper.
- Trail compares SHAs across one-passage stamps; it does not re-sign. A retract beside a stamp is noted. History stays.
- Retract records the withdrawal and binds card fields. It does not erase the proof.
- `ok: true` is a field bind — card shape holds. Not a QUANTUM signature. QUANTUM fills the signature later.

Do not merge check, press, or trail into this repository. Interop is the card.
