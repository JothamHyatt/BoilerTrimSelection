# Hydronic Selector Demo - Streamlit

Fixed version: prevents `KeyError: system_type` if Streamlit Cloud is using an older CSV.

Replace both files in the repo:

- `app.py`
- `hydronic_parts_database.csv`

The updated CSV includes the new `system_type` column required for Expansion Tank selections.
