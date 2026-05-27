# The Boiler Wizard - Patched Working App

This package contains your uploaded app.py with targeted fixes only. It is not a completely new app.

Included:
- app.py
- README.md

Not included:
- hydronic_parts_database.csv
- boiler_wizard_shimmer.gif
- hot_water_hydronic_system_selector_demo.gif

Keep your existing CSV and GIF assets in the same folder as this app.py.

Fixes included:
- Restored/kept Boiler Manufacturer dropdown.
- Restored/kept Air Separator Manufacturer dropdown.
- Boiler selection is locked to the selected boiler manufacturer before BTU sorting.
- Air Separator selection is locked to selected air separator manufacturer.
- Mixing Valve remains conditional for With Tankless Coil.
- Mixing Valve filters by Manufacturer, Connection Size, and Connection Type.
- Highlighted Component dropdown uses visible_order and a unique key to avoid Streamlit duplicate element errors.
- Caption changed to Hydronic equipment selector.
- Text columns are stripped after CSV load to avoid trailing-space filter bugs.
