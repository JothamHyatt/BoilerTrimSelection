# The Boiler Wizard - Complete Streamlit App

This ZIP contains the complete app package, not just a patch.

## Files included

- app.py - full Streamlit application
- hydronic_parts_database.csv - complete equipment database
- boiler_wizard_shimmer.gif - animated Boiler Wizard banner GIF
- hot_water_hydronic_system_selector_demo.gif - animated hydronic system diagram GIF
- README.md - this file
- requirements.txt - Python dependencies
- run_app_windows.bat - Windows launch helper
- run_app_mac_linux.sh - Mac/Linux launch helper

## Recent changes included

- App title changed to THE BOILER WIZARD.
- Boiler Wizard animated banner added above the selection menu.
- Banner uses the uploaded Boiler Wizard artwork, not AI regenerated art.
- Banner animation uses CRT-style shimmer plus localized wand glow.
- Resideo HPV075 added for 0-40,000 BTU with 3/4 inch connection.
- Resideo HPV100 moved to 40,000-80,000 BTU with 1 inch connection.
- Selection sorting corrected so 39,999 BTU selects HPV075 and 40,000 BTU selects HPV100.
- Existing selected equipment breakdown retained.
- Existing component highlighting retained.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```
