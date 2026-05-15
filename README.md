# Hydronic Selector Demo - Streamlit

This is the complete repackaged app.

Included:
- app.py
- hydronic_parts_database.csv
- README.md

Important: keep `hot_water_hydronic_system_selector_demo.gif` in the same folder as `app.py`.

Run:

```bash
streamlit run app.py
```

Latest update:
- Added Resideo HPV075 air eliminator for 0-40,000 BTU with 3/4 inch connection.
- Moved Resideo HPV100 range to 40,000-80,000 BTU with 1 inch connection.
- Corrected selection sorting so BTU below 40,000 selects HPV075.
- At exactly 40,000 BTU, the app selects HPV100 because the higher/tighter range wins at the boundary.

Previous fixes included:
- GIF callout newline fix for visible `\n` or `/n` text.
- Fill Valve / Backflow Preventer highlight at cx=178, cy=230, r=40.
- Pump Isolation Flanges highlight at cx=521, cy=212, r=18.
- PSHT expansion tanks automatically include [1] WH41672 service valve.
