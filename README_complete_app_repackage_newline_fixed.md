# Hydronic Selector Demo - Streamlit

Complete repackaged app with GIF callout newline fix included.

## Included updates

- Fixes visible `\n` or `/n` text in the animated GIF/SVG callout overlay by converting newline text to HTML line breaks before rendering.
- Corrected Fill Valve / Backflow Preventer highlight to the pressure reducing valve location marked by the user. Coordinates: `cx=178`, `cy=230`, `r=40`.
- Corrected Pump Isolation Flanges highlight to the flange / circulator location marked by the user. Coordinates: `cx=521`, `cy=212`, `r=18`.
- All Fill Valve / Backflow Preventer selections include `1/2 inch` connection size.
- Expansion tank connection sizes: PSHT30/PSHT60/PSHT90 = `1/2 inch`; ASX30V/ASX40V/ASX60V = `1 inch`.
- Automatically adds `[1] WH41672` expansion tank service valve when PSHT30, PSHT60, or PSHT90 is selected.
- Existing green monochrome GIF is referenced only and is not included or overwritten.

## Deployment

Replace or upload these files in your app folder:

- `app.py`
- `hydronic_parts_database.csv`

Keep your existing GIF in place:

- `hot_water_hydronic_system_selector_demo.gif`

Run with:

```bash
streamlit run app.py
```
