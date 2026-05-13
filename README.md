# Hydronic Selector Demo - Streamlit

Expansion tank highlight correction:

- Expansion Tank circle is now centered on the round tank body directly below the air separator.
- The GIF and the highlight circle are now rendered in the same SVG coordinate system, preventing scaling drift.
- The circle no longer targets the leader arrow next to the tank.
- Calibration controls remain available in the sidebar for fine-tuning.

Replace these files in the repo:

- `app.py`
- `hydronic_parts_database.csv`
- `hot_water_hydronic_system_selector_demo.gif`
