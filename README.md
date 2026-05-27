# The Boiler Wizard - Air Separator Dropdown Reordered

This package contains the same targeted app with the Air Separator Manufacturer dropdown moved lower in the sidebar.

Included:
- app.py
- README.md

Not included:
- hydronic_parts_database.csv
- boiler_wizard_shimmer.gif
- hot_water_hydronic_system_selector_demo.gif

Keep your existing CSV and GIF assets in the same folder as this app.py.

Change made:
- Air Separator Manufacturer dropdown moved below the boiler fuel/flue/tankless coil section and above Fill Valve / Backflow Preventer.

Existing fixes preserved:
- Boiler Manufacturer filter remains active.
- Air Separator Manufacturer filter remains active.
- Mixing Valve remains conditional for With Tankless Coil.
- Highlighted Component uses visible_order with a unique key.
- Text columns are stripped after CSV load.
