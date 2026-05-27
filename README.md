# The Boiler Wizard - Oil Filter Update

This app package adds an Oil Filter manufacturer dropdown for oil-fired boilers.

Included:
- app.py
- README.md

Not included:
- hydronic_parts_database.csv
- boiler_wizard_shimmer.gif
- hot_water_hydronic_system_selector_demo.gif

Keep your existing CSV and GIF assets in the same folder as this app.py.

New feature:
- Oil Filter appears only when Boiler Fuel Type = Oil.
- Oil Filter uses Manufacturer dropdown only.
- No Oil Filter connection size/type dropdowns were added.
- Oil Filter appears in Selected Equipment Breakdown and Highlighted Component only for oil boilers.

Existing behavior preserved:
- Boiler Manufacturer filtering.
- Air Separator Manufacturer filtering.
- Air Separator dropdown remains below boiler fuel/flue/tankless coil area.
- Mixing Valve remains conditional for With Tankless Coil.
- Highlighted Component uses visible_order with a unique key.
- Text columns are stripped after CSV load to avoid trailing-space filter bugs.

CSV requirement:
Add Oil Filter rows to hydronic_parts_database.csv with component = Oil Filter.
Use broad BTU ranges, e.g. min_btu = 0 and max_btu = 5000000.
