# Hydronic Selector Demo - Streamlit

This is the complete repackaged app.

Included:
- app.py
- hydronic_parts_database.csv
- README

Important: keep `hot_water_hydronic_system_selector_demo.gif` in the same folder as `app.py`.

Run:

```bash
streamlit run app.py
```

Fixes included:
- GIF callout newline fix for visible `\n` or `/n` text.
- Fill Valve / Backflow Preventer highlight at cx=178, cy=230, r=40.
- Pump Isolation Flanges highlight at cx=521, cy=212, r=18.
- PSHT expansion tanks automatically include [1] WH41672 service valve.
