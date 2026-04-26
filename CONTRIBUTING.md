### Submitting a new entry

Open an issue with the [New entry form](https://github.com/EdOverflow/can-i-take-over-xyz/issues/new?template=new-entry.yml). The form prompts for the exact fields the parser consumes — service, status, domains, fingerprint, proof, documentation. A maintainer adds the row to `README.md`; CI does the rest.

### Local development

Regenerate `fingerprints.json` and the README table from the README's source rows:

```bash
pip install -r scripts/requirements.txt
python3 scripts/gen_fingerprints.py overwrite_json overwrite_readme
```

Other modes: `json` and `readme` print to stdout without overwriting; useful for diffing.

Run the unit test suite:

```bash
pip install -r scripts/requirements-dev.txt
pytest tests/
```

`validate_pr` runs the same tests plus an end-to-end parser run on every PR that touches `README.md`, `scripts/**`, `tests/**`, or `conftest.py`.

### Prettifying Markdown

```bash
npm install --save-dev --save-exact prettier
npx prettier --write .
```

### Fingerprint Contributors Over Time

[Muhammad Khizer Javed](https://github.com/MuhammadKhizerJaved)\
[Evgeniy Yakovchuk](https://github.com/sp1d3r)\
[Avileox](https://github.com/Avileox)\
[AmanShahid](https://github.com/AmanShahid)\
[The Mysterious Cyber Warriors](https://github.com/gauravdrago)\
[m7mdharoun](https://github.com/m7mdharoun)\
[Mohamed Elbadry](https://github.com/melbadry9)\
[Talksec](https://github.com/TakSec)\
[Rajat Moury](https://github.com/messi96)\
[Spam404](https://github.com/Spam404)\
[r0hack](https://github.com/r0hack)\
[Quinten](https://github.com/Quikko)\
[jatoch](https://github.com/jatoch)\
[itachi73](https://github.com/itachi73)\
[LinuxSec](https://github.com/linuxsec)\
[Patrik Hudak](https://github.com/PatrikHudak)
