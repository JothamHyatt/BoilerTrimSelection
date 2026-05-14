# Hydronic Selector Demo - Streamlit

Pressure reducing valve and expansion tank update.

## Updates
- Moved `Fill Valve / Backflow Preventer` highlight target left/up to the pressure reducing valve area rather than the pressure relief valve.
- All `Fill Valve / Backflow Preventer` options carry a `1/2"` connection size.
- Added expansion tank connection sizes: PSHT30/PSHT60/PSHT90 = `1/2"`; ASX30V/ASX40V/ASX60V = `1"`.
- Automatically adds `[1] WH41672` expansion tank service valve to the material list when PSHT30, PSHT60, or PSHT90 is selected.
- Existing green monochrome GIF is referenced only and is not included or overwritten.

## Replace these files
- `app.py`
- `hydronic_parts_database.csv`

Keep `hot_water_hydronic_system_selector_demo.gif` in place.
