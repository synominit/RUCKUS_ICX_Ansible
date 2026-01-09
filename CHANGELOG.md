## v3.0.0 (2026-01-09)

### Refactor

- **changes-for-seperate-collection**: made changes needed for uploading as a seperate collection under synominit.icx

## v2.0.0 (2026-01-09)

### Fix

- **plugins/modules/icx_facts.py**: added consideration for the serial number being outside of the expected position and whitespaces being different across versions
- **plugins/modules/icx_vlan.py**: renabled the vlan unit tests, and fixed the failing tests due to set not keeping order and associated checks not considering the added exit to commands
- **ansible_collections/commscope/icx/plugins/modules/icx_facts.py**: fix for the icx facts cannot concatenate nonetype to string error
