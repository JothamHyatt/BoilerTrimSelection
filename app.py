import base64
import html as html_lib
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='The Boiler Wizard', layout='wide', initial_sidebar_state='expanded')

DB = Path('hydronic_parts_database.csv')
BANNER_GIF = Path('boiler_wizard_shimmer.gif')
DIAGRAM_GIF = Path('hot_water_hydronic_system_selector_demo.gif')

FILL = 'Fill Valve / Backflow Preventer'
ORDER = ['Boiler', FILL, 'Air Separator', 'Expansion Tank', 'Pump Isolation Flanges']
PSHT = {'PSHT30','PSHT60','PSHT90'}

# ✅ DEFAULTS (prevents ALL NameErrors)
boiler_manufacturer = None
air_sep_manufacturer = None
btu = 120000
fuel = 'Natural Gas'
flue = 'N/A'
coil = 'N/A'
fillopt = None
sys_type = None
conn = 'Press'
hi = 'Boiler'

def filt(df, comp, btu, sys_type, conn, fuel, flue, coil, fillopt,
         boiler_manufacturer=None, air_sep_manufacturer=None):

    f = df[df.component == comp].copy()

    if comp == 'Expansion Tank' and sys_type:
        f = f[f.system_type == sys_type]

    if comp == 'Pump Isolation Flanges':
        f = f[f.connection_type == conn]

    if comp == 'Boiler':
        if boiler_manufacturer:
            f = f[f.manufacturer == boiler_manufacturer]
        f = f[f.fuel_type == fuel]
        if fuel == 'Oil':
            f = f[(f.flue_type == flue) & (f.tankless_coil == coil)]

    if comp == 'Air Separator' and air_sep_manufacturer:
        f = f[f.manufacturer == air_sep_manufacturer]

    if comp == FILL and fillopt:
        f = f[f.selection_option == fillopt]

    f = f[(f.min_btu <= btu) & (f.max_btu >= btu)]

    return f.sort_values(['min_btu','max_btu'], ascending=[False, True])


df = pd.read_csv(DB)

st.title('THE BOILER WIZARD')
st.caption('Hydronic equipment selector')

# ✅ INPUTS FIRST (critical fix)
with st.sidebar:
    if BANNER_GIF.exists():
        st.image(str(BANNER_GIF), use_container_width=True)

    st.header('System Inputs')

    btu = st.number_input('BTU Capacity / Boiler Output BTU', 0, 5000000, 120000, 5000)

    boiler_manufacturer = st.selectbox(
        'Boiler Manufacturer',
        sorted(df[df.component == 'Boiler'].manufacturer.dropna().unique())
    )

    air_sep_manufacturer = st.selectbox(
        'Air Separator Manufacturer',
        sorted(df[df.component == 'Air Separator'].manufacturer.dropna().unique())
    )

    fuel = st.selectbox('Boiler Fuel Type', ['Natural Gas','Oil'])

    if fuel == 'Oil':
        flue = st.selectbox('Boiler Flue Type', ['Top Flue','Rear Flue'])
        coil = st.selectbox('Tankless Coil', ['Without Tankless Coil','With Tankless Coil'])

    fillopt = st.selectbox(
        'Fill Valve / Backflow Preventer',
        sorted([x for x in df[df.component == FILL].selection_option.dropna().unique() if x != 'N/A'])
    )

    sys_type = st.selectbox(
        'Expansion Tank System Type',
        sorted([x for x in df[df.component == 'Expansion Tank'].system_type.dropna().unique() if x != 'Any'])
    )

    conn = st.selectbox('Pump Isolation Flange Connection Type', ['Press','Sweat','Threaded'])

    hi = st.selectbox('Highlighted Component', ORDER)

# ✅ MAIN LOGIC SAFE
rows = []

for comp in ORDER:
    m = filt(df, comp, int(btu), sys_type, conn, fuel, flue, coil,
             fillopt, boiler_manufacturer, air_sep_manufacturer)

    if m.empty:
        rows.append({'Component': comp, 'Model #':'No match'})
    else:
        r = m.iloc[0]
        rows.append({'Component': r.component, 'Model #': r.model_number})

sel = pd.DataFrame(rows)

st.subheader('Selected Equipment')
st.dataframe(sel, use_container_width=True)

if not DIAGRAM_GIF.exists():
    st.warning('Add hydronic system GIF to folder.')
``
