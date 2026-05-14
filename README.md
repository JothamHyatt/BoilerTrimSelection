# Hydronic Selector Demo - Streamlit

Pipe size display fix only.

## What changed

- `hydronic_parts_database.csv` includes pipe sizes for all Pump Isolation Flange selections.
- `app.py` displays `Pipe Size` in:
  - Selected Equipment Breakdown
  - Highlighted Selection
  - Detailed Component Cards
  - CSV export
- The app still uses your existing `hot_water_hydronic_system_selector_demo.gif` and does **not** overwrite or regenerate the GIF.

## Deployment

Replace only:

- `app.py`
- `hydronic_parts_database.csv`

Keep your existing green monochrome GIF in place.
