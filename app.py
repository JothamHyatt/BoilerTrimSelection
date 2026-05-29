
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
IMG_W, IMG_H = 980, 586
FILL = 'Fill Valve / Backflow Preventer'
PSHT = {'PSHT30', 'PSHT60', 'PSHT90'}
ORDER = ['Boiler', FILL, 'Air Separator', 'Expansion Tank', 'Mixing Valve', 'Pump Isolation Flanges']
POS = {
    'Air Separator': {'cx': 395, 'cy': 210, 'r': 30, 'callout_x': 410, 'callout_y': 70},
    'Expansion Tank': {'cx': 395, 'cy': 285, 'r': 42, 'callout_x': 235, 'callout_y': 240},
    'Pump Isolation Flanges': {'cx': 521, 'cy': 212, 'r': 18, 'callout_x': 555, 'callout_y': 105},
    'Boiler': {'cx': 335, 'cy': 470, 'r': 34, 'callout_x': 360, 'callout_y': 390},
    FILL: {'cx': 178, 'cy': 230, 'r': 40, 'callout_x': 215, 'callout_y': 120},
}

def img64(path):
    return base64.b64encode(path.read_bytes()).decode('utf-8')

def clean(txt):
    return html_lib.escape(str(txt)).replace('\\n', '<br/>').replace('/n', '<br/>').replace('\n', '<br/>')

def options_from(series, exclude=('N/A', 'Any', '', 'nan')):
    vals = []
    for x in series.dropna().unique():
        s = str(x).strip()
        if s not in exclude:
            vals.append(s)
    return sorted(vals)

def selectbox_cascade(label, options, key_base, disabled_when_single=True):
    # Key changes when the option set changes, preventing stale Streamlit selections.
    options = [str(x).strip() for x in options if str(x).strip() not in ('', 'nan')]
    if not options:
        st.selectbox(label, ['No valid options'], index=0, disabled=True, key=f'{key_base}_none')
        return None
    key = key_base + '_' + str(abs(hash(tuple(options))))
    return st.selectbox(label, options, index=0, disabled=(disabled_when_single and len(options) == 1), key=key)

def filt(df, comp, btu, sys_type, conn, fuel, flue, coil, fillopt,
         boiler_manufacturer=None, air_sep_manufacturer=None,
         mix_mfr=None, mix_size=None, mix_type=None, draft_hood_style=None):
    f = df[df.component == comp].copy()
    if comp == 'Expansion Tank':
        f = f[f.system_type == sys_type]
    if comp == 'Pump Isolation Flanges':
        f = f[f.connection_type == conn]
    if comp == 'Boiler':
        if boiler_manufacturer:
            f = f[f.manufacturer == boiler_manufacturer]
        f = f[f.fuel_type == fuel]
        if fuel == 'Natural Gas' and draft_hood_style and 'draft_hood_style' in f.columns:
            f = f[f.draft_hood_style == draft_hood_style]
        if fuel == 'Oil':
            f = f[(f.flue_type == flue) & (f.tankless_coil == coil)]
    if comp == 'Air Separator' and air_sep_manufacturer:
        f = f[f.manufacturer == air_sep_manufacturer]
    if comp == 'Mixing Valve':
        if mix_mfr:
            f = f[f.manufacturer == mix_mfr]
        if mix_size:
            f = f[f.pipe_size == mix_size]
        if mix_type:
            f = f[f.connection_type == mix_type]
    if comp == FILL:
        f = f[f.selection_option == fillopt]
    f = f[(pd.to_numeric(f.min_btu, errors='coerce') <= btu) & (pd.to_numeric(f.max_btu, errors='coerce') >= btu)].copy()
    return f.sort_values(['min_btu', 'max_btu'], ascending=[False, True])

if not DB.exists():
    st.error('Missing hydronic_parts_database.csv')
    st.stop()

df = pd.read_csv(DB)
df.columns = df.columns.str.strip()
if 'draft_hood_style' not in df.columns:
    df['draft_hood_style'] = 'N/A'
for col in ['component','manufacturer','system_type','connection_type','fuel_type','flue_type','tankless_coil','selection_option','pipe_size','draft_hood_style','model_number','part_number','description']:
    if col in df.columns:
        df[col] = df[col].fillna('N/A').astype(str).str.strip()
for col in ['min_btu','max_btu','quantity','input_mbh']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

st.title('THE BOILER WIZARD')
st.caption('A Mystical, Magical, Hot Water Hydronic equipment selection application for residential applications')
st.caption('Scroll down for selections')

with st.sidebar:
    if BANNER_GIF.exists():
        st.image(str(BANNER_GIF), use_container_width=True)
    else:
        st.info('Boiler Wizard banner GIF not found in this folder.')
    st.header('System Inputs')
    btu = st.number_input('BTU Capacity / Boiler Output BTU', 0, 5000000, 120000, 5000)

    boiler_rows = df[df.component == 'Boiler'].copy()
    boiler_manufacturer = st.selectbox('Boiler Manufacturer', options_from(boiler_rows.manufacturer, exclude=('N/A','','nan')), key='boiler_manufacturer_selector')

    # Correct top-level boiler cascade: Manufacturer -> Fuel.
    # This does not use sys_type/conn/fillopt, so it cannot trigger NameError.
    # US Boiler will show Oil only if an actual US Boiler Oil boiler row exists in the CSV.
    boiler_base = boiler_rows[boiler_rows.manufacturer == boiler_manufacturer].copy()
    fuel = selectbox_cascade('Boiler Fuel Type', options_from(boiler_base.fuel_type, exclude=('N/A','','nan')), 'fuel_selector')

    flue = 'N/A'
    coil = 'N/A'
    draft_hood_style = None

    if fuel == 'Natural Gas':
        gas_df = boiler_base[boiler_base.fuel_type == 'Natural Gas'].copy()
        dh_options = options_from(gas_df.draft_hood_style, exclude=('N/A','Any','','nan'))
        if dh_options:
            draft_hood_style = selectbox_cascade('Boiler Draft Hood Style', dh_options, 'draft_hood_style_selector')

    if fuel == 'Oil':
        oil_df = boiler_base[boiler_base.fuel_type == 'Oil'].copy()
        flue = selectbox_cascade('Boiler Flue Type', options_from(oil_df.flue_type, exclude=('N/A','Any','','nan')), 'boiler_flue_selector') or 'N/A'
        coil_df = oil_df[oil_df.flue_type == flue].copy()
        coil = selectbox_cascade('Tankless Coil', options_from(coil_df.tankless_coil, exclude=('N/A','Any','','nan')), 'tankless_coil_selector') or 'N/A'

    air_sep_manufacturer = st.selectbox('Air Separator Manufacturer', options_from(df[df.component == 'Air Separator'].manufacturer, exclude=('N/A','','nan')), key='air_separator_manufacturer_selector')
    fillopt = st.selectbox('Fill Valve / Backflow Preventer', options_from(df[df.component == FILL].selection_option, exclude=('N/A','','nan')), key='fill_valve_selector')
    sys_type = st.selectbox('Expansion Tank System Type', options_from(df[df.component == 'Expansion Tank'].system_type, exclude=('Any','N/A','','nan')), key='expansion_tank_system_type_selector')
    conn = st.selectbox('Pump Isolation Flange Connection Type', options_from(df[df.component == 'Pump Isolation Flanges'].connection_type, exclude=('Any','N/A','','nan')), key='pump_flange_connection_selector')

    mixing_valve_manufacturer = None
    mixing_valve_connection_size = None
    mixing_valve_connection_type = None
    if coil == 'With Tankless Coil':
        st.subheader('DHW Mixing Valve')
        mv = df[df.component == 'Mixing Valve'].copy()
        if mv.empty:
            st.warning('No Mixing Valve rows found in hydronic_parts_database.csv')
        else:
            mixing_valve_manufacturer = st.selectbox('Mixing Valve Manufacturer', options_from(mv.manufacturer, exclude=('N/A','','nan')), key='mixing_valve_manufacturer_selector')
            mv = mv[mv.manufacturer == mixing_valve_manufacturer]
            mixing_valve_connection_size = st.selectbox('Mixing Valve Connection Size', options_from(mv.pipe_size, exclude=('N/A','','nan')), key='mixing_valve_connection_size_selector')
            mv = mv[mv.pipe_size == mixing_valve_connection_size]
            mixing_valve_connection_type = st.selectbox('Mixing Valve Connection Type', options_from(mv.connection_type, exclude=('N/A','Any','','nan')), key='mixing_valve_connection_type_selector')

    visible_order = [c for c in ORDER if not (c == 'Mixing Valve' and coil != 'With Tankless Coil')]
    hi = st.selectbox('Highlighted Component', visible_order, key='highlighted_component_selector')

rows = []
for comp in visible_order:
    m = filt(df, comp, int(btu), sys_type, conn, fuel, flue, coil, fillopt, boiler_manufacturer, air_sep_manufacturer, mixing_valve_manufacturer, mixing_valve_connection_size, mixing_valve_connection_type, draft_hood_style)
    if m.empty:
        rows.append({'Component': comp, 'Qty': '', 'Manufacturer': '', 'Model #': 'No match', 'Part #': 'No match', 'Pipe Size': 'N/A', 'BTU Range': 'No matching range', 'Description': 'Add a matching rule.'})
    else:
        r = m.iloc[0]
        rows.append({'Component': r.component, 'Qty': int(r.quantity) if pd.notna(r.quantity) else '', 'Manufacturer': r.manufacturer, 'Model #': r.model_number, 'Part #': r.part_number, 'Pipe Size': r.pipe_size, 'BTU Range': f'{int(r.min_btu):,} - {int(r.max_btu):,} BTU', 'Description': r.description})

if any(x['Component'] == 'Expansion Tank' and x['Model #'] in PSHT for x in rows):
    rows.append({'Component': 'Expansion Tank Service Valve', 'Qty': 1, 'Manufacturer': 'Webstone', 'Model #': 'WH41672', 'Part #': 'WH41672', 'Pipe Size': '1/2"', 'BTU Range': 'N/A', 'Description': 'Automatically included with PSHT expansion tank selection.'})

sel = pd.DataFrame(rows)
m = filt(df, hi, int(btu), sys_type, conn, fuel, flue, coil, fillopt, boiler_manufacturer, air_sep_manufacturer, mixing_valve_manufacturer, mixing_valve_connection_size, mixing_valve_connection_type, draft_hood_style)
if m.empty:
    title = hi.upper()
    body = f'NO MATCH\\n{int(btu):,} BTU'
else:
    r = m.iloc[0]
    if hi == FILL:
        title = 'PRESSURE REDUCING VALVE'
        body = f'{r.selection_option}\\n{r.manufacturer}\\nQTY {int(r.quantity)}\\n{r.model_number}\\n{r.pipe_size} CONNECTION'
    elif hi == 'Expansion Tank':
        svc = '\\n+ [1] WH41672 SERVICE VALVE' if r.model_number in PSHT else ''
        title = 'EXPANSION TANK'
        body = f'{r.manufacturer}\\n{r.model_number}\\n{r.system_type}\\n{r.pipe_size} CONNECTION{svc}'
    elif hi == 'Pump Isolation Flanges':
        title = 'PUMP ISOLATION FLANGES'
        body = f'QTY {int(r.quantity)}\\n{r.manufacturer} {r.model_number}\\n{r.connection_type} / {r.pipe_size} PIPE'
    elif hi == 'Boiler':
        title = 'BOILER'
        extra = f'\\n{draft_hood_style}' if fuel == 'Natural Gas' and draft_hood_style else (f'\\n{flue} / {coil}' if fuel == 'Oil' else '')
        body = f'{r.manufacturer}\\n{r.model_number}\\n{r.fuel_type}{extra}\\n{r.input_mbh} MBH IN\\n{int(r.min_btu):,}-{int(r.max_btu):,} BTU OUT'
    elif hi == 'Mixing Valve':
        title = 'DHW MIXING VALVE'
        body = f'{r.manufacturer} {r.model_number}\\n{r.pipe_size} / {r.connection_type}'
    else:
        title = 'AIR SEPARATOR'
        body = f'{r.manufacturer} {r.model_number}\\n{r.pipe_size} PIPE'

left, right = st.columns([1.65, 1])
with left:
    if not DIAGRAM_GIF.exists():
        st.warning('Diagram GIF is missing. Keep hot_water_hydronic_system_selector_demo.gif in this folder.')
    else:
        p = POS[hi]
        gif = img64(DIAGRAM_GIF)
        th = clean(title)
        bh = clean(body)
        html = f'''
<style>
.diagram-wrap {{ background:#000; border:1px solid #00cc44; box-shadow:0 0 12px rgba(57,255,85,.35); max-width:980px; margin:auto; }}
.diagram-svg {{ display:block; width:100%; height:auto; }}
.pulse {{ fill:none; stroke:#39ff55; stroke-width:3; animation:pulse 1.1s infinite; }}
@keyframes pulse {{ 0% {{opacity:.45;stroke-width:2}} 50% {{opacity:1;stroke-width:5}} 100% {{opacity:.45;stroke-width:2}} }}
.callout {{ color:#39ff55; background:rgba(0,0,0,.84); border:1px solid #39ff55; padding:8px 11px; font-family:Courier New,monospace; font-size:15px; }}
</style>
<div class='diagram-wrap'><svg class='diagram-svg' viewBox='0 0 {IMG_W} {IMG_H}'><image href='data:image/gif;base64,{gif}' x='0' y='0' width='{IMG_W}' height='{IMG_H}'/><circle class='pulse' cx='{p['cx']}' cy='{p['cy']}' r='{p['r']}'/><foreignObject x='{p['callout_x']}' y='{p['callout_y']}' width='390' height='230'><div xmlns='http://www.w3.org/1999/xhtml' class='callout'><b>{th}</b><br/>{bh}<br/><span>&gt; SELECTED BY INPUTS</span></div></foreignObject></svg></div>
'''
        components.html(html, height=625, scrolling=False)

with right:
    st.subheader('Highlighted Selection')
    st.dataframe(sel[sel.Component == hi], use_container_width=True, hide_index=True)
    st.subheader('Selected Equipment Breakdown')
    st.dataframe(sel, use_container_width=True, hide_index=True)
    st.download_button('Download Selected Equipment Breakdown', data=sel.to_csv(index=False), file_name='selected_equipment_breakdown.csv', mime='text/csv')
    st.subheader('Available Ranges for Highlighted Component')
    st.dataframe(df[df.component == hi], use_container_width=True, hide_index=True)
