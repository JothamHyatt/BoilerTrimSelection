
import base64
import html as html_lib
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='The Boiler Wizard', layout='wide', initial_sidebar_state='expanded')

DB = Path('hydronic_parts_database.csv')
BANNER_GIF = Path('boiler_wizard_shimmer.gif')
HOT_WATER_DIAGRAM_GIF = Path('hot_water_hydronic_system_selector_demo.gif')
STEAM_DIAGRAM_GIF = Path('steam_heating_system_green_bubbles_return_point_lowered.gif')

IMG_W, IMG_H = 980, 586
FILL = 'Fill Valve / Backflow Preventer'
PSHT = {'PSHT30', 'PSHT60', 'PSHT90'}
HOT_WATER_ORDER = ['Boiler', FILL, 'Air Separator', 'Expansion Tank', 'Mixing Valve', 'Pump Isolation Flanges']
STEAM_ORDER = ['Boiler', 'Steam Water Feeder', 'Backflow Preventer']

POS = {
    'Air Separator': {'cx': 395, 'cy': 210, 'r': 30, 'callout_x': 410, 'callout_y': 70},
    'Expansion Tank': {'cx': 395, 'cy': 285, 'r': 42, 'callout_x': 235, 'callout_y': 240},
    'Pump Isolation Flanges': {'cx': 521, 'cy': 212, 'r': 18, 'callout_x': 555, 'callout_y': 105},
    'Boiler': {'cx': 335, 'cy': 470, 'r': 34, 'callout_x': 360, 'callout_y': 390},
    FILL: {'cx': 178, 'cy': 230, 'r': 40, 'callout_x': 215, 'callout_y': 120},
}

st.markdown('''
<style>
.stApp{background:#000}
section[data-testid="stSidebar"]{background:#000!important;border-right:1px solid #39ff55}
h1,h2,h3,label,.stCaptionContainer{font-family:"Courier New",monospace!important;color:#39ff55!important}
div[data-baseweb="select"]>div,div[data-baseweb="input"]>div,.stNumberInput input{background:#000!important;color:#39ff55!important;border:1px solid #39ff55!important;border-radius:0!important;font-family:"Courier New",monospace!important}
button{background:#000!important;color:#39ff55!important;border:1px solid #39ff55!important}
</style>
''', unsafe_allow_html=True)


def img64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode('utf-8')


def clean(txt) -> str:
    return html_lib.escape(str(txt)).replace('\\n', '<br/>').replace('/n', '<br/>').replace('\n', '<br/>')


def norm_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip()
    text_cols = [
        'component', 'manufacturer', 'system_type', 'connection_type', 'fuel_type',
        'flue_type', 'tankless_coil', 'selection_option', 'pipe_size',
        'draft_hood_style', 'model_number', 'part_number', 'description'
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df


def safe_unique(series):
    vals = []
    for x in series.dropna().unique():
        s = str(x).strip()
        if s and s not in {'N/A', 'nan', 'None'}:
            vals.append(s)
    return sorted(vals)


def first_select(label, options, *, key=None, disabled_if_single=False):
    options = list(options)
    if not options:
        st.warning(f'No available options for {label}.')
        return None
    if disabled_if_single and len(options) == 1:
        return st.selectbox(label, options, index=0, disabled=True, key=key)
    return st.selectbox(label, options, key=key)


def boiler_pool(df: pd.DataFrame, heating_system: str) -> pd.DataFrame:
    pool = df[df.component == 'Boiler'].copy()
    # If the database has system_type values for boilers, use them. If not, fall back gracefully.
    if 'system_type' in pool.columns:
        steam_mask = pool.system_type.astype(str).str.contains('Steam', case=False, na=False)
        hot_water_mask = pool.system_type.astype(str).str.contains('Hot Water|Hydronic|Water', case=False, na=False)
        if heating_system == 'Steam' and steam_mask.any():
            pool = pool[steam_mask]
        elif heating_system == 'Hot Water' and hot_water_mask.any():
            pool = pool[hot_water_mask]
    return pool


def filt(df, comp, btu, sys_type, conn, fuel, flue, coil, fillopt,
         boiler_manufacturer=None, air_sep_manufacturer=None, mix_mfr=None,
         mix_size=None, mix_type=None, draft_hood_style=None, heating_system='Hot Water'):
    if comp == 'Boiler':
        f = boiler_pool(df, heating_system)
    else:
        f = df[df.component == comp].copy()

    if comp == 'Expansion Tank':
        f = f[f.system_type == sys_type]
    if comp == 'Pump Isolation Flanges':
        f = f[f.connection_type == conn]
    if comp == 'Boiler':
        if boiler_manufacturer:
            f = f[f.manufacturer == boiler_manufacturer]
        if fuel:
            f = f[f.fuel_type == fuel]
        if heating_system == 'Hot Water':
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

    if {'min_btu', 'max_btu'}.issubset(f.columns):
        f = f[(f.min_btu <= btu) & (f.max_btu >= btu)].copy()
        return f.sort_values(['min_btu', 'max_btu'], ascending=[False, True])
    return f


def equipment_row_from_match(comp, m):
    if m.empty:
        return {
            'Component': comp, 'Qty': '', 'Manufacturer': '', 'Model #': 'No match',
            'Part #': 'No match', 'Pipe Size': 'N/A', 'BTU Range': 'No matching range',
            'Description': 'Add a matching rule.'
        }
    r = m.iloc[0]
    return {
        'Component': r.component,
        'Qty': int(r.quantity) if 'quantity' in m.columns and pd.notna(r.quantity) else 1,
        'Manufacturer': r.manufacturer if 'manufacturer' in m.columns else '',
        'Model #': r.model_number if 'model_number' in m.columns else '',
        'Part #': r.part_number if 'part_number' in m.columns else '',
        'Pipe Size': r.pipe_size if 'pipe_size' in m.columns else 'N/A',
        'BTU Range': f'{int(r.min_btu):,} - {int(r.max_btu):,} BTU' if {'min_btu','max_btu'}.issubset(m.columns) else 'N/A',
        'Description': r.description if 'description' in m.columns else ''
    }


def steam_accessory_rows(fuel: str):
    if fuel == 'Oil':
        feeder = {
            'Component': 'Steam Water Feeder', 'Qty': 1, 'Manufacturer': 'Hydrolevel',
            'Model #': 'VXT-120', 'Part #': 'H45122', 'Pipe Size': 'N/A',
            'BTU Range': 'N/A', 'Description': 'Automatically included with oil steam boiler selection.'
        }
    else:
        feeder = {
            'Component': 'Steam Water Feeder', 'Qty': 1, 'Manufacturer': 'Hydrolevel',
            'Model #': 'VXT-24', 'Part #': 'H45026', 'Pipe Size': 'N/A',
            'BTU Range': 'N/A', 'Description': 'Automatically included with natural gas steam boiler selection.'
        }
    backflow = {
        'Component': 'Backflow Preventer', 'Qty': 1, 'Manufacturer': 'Watts',
        'Model #': 'W9DM3D', 'Part #': 'W9DM3D', 'Pipe Size': 'N/A',
        'BTU Range': 'N/A', 'Description': 'Automatically included with steam boiler selection.'
    }
    return [feeder, backflow]


def boiler_callout(m, hi, btu, fuel):
    if m.empty:
        return hi.upper(), f'NO MATCH\\n{int(btu):,} BTU'
    r = m.iloc[0]
    if hi == 'Boiler':
        mbh = f' / {r.input_mbh} MBH IN' if 'input_mbh' in m.columns and pd.notna(r.input_mbh) else ''
        return 'BOILER', f'{r.manufacturer}\\n{r.model_number}\\n{fuel}{mbh}\\n{int(r.min_btu):,}-{int(r.max_btu):,} BTU OUT'
    return hi.upper(), ''


def render_hot_water_diagram(diagram_path: Path, hi: str, title: str, body: str):
    if not diagram_path.exists():
        st.warning('Diagram GIF is missing. Keep hot_water_hydronic_system_selector_demo.gif in this folder.')
        return
    p = POS.get(hi, POS['Boiler'])
    gif = img64(diagram_path)
    th = clean(title)
    bh = clean(body)
    html = f'''
    <style>
      .diagram-wrap{{position:relative;background:#000;border:1px solid #00cc44;box-shadow:0 0 12px rgba(57,255,85,.35);width:100%;}}
      .diagram-wrap img{{display:block;width:100%;height:auto;}}
      .pulse{{fill:none;stroke:#39ff55;stroke-width:4;animation:pulse 1.1s infinite;filter:drop-shadow(0 0 6px #39ff55);}}
      @keyframes pulse{{0%{{opacity:.25;stroke-width:2}}50%{{opacity:1;stroke-width:5}}100%{{opacity:.25;stroke-width:2}}}}
      .callout{{position:absolute;left:{p['callout_x']/IMG_W*100:.2f}%;top:{p['callout_y']/IMG_H*100:.2f}%;max-width:260px;color:#39ff55;background:rgba(0,0,0,.86);border:1px solid #39ff55;padding:8px 10px;font:14px Courier New,monospace;text-shadow:0 0 5px #39ff55;}}
      .callout b{{font-size:15px;}}
    </style>
    <div class="diagram-wrap">
      <img src="data:image/gif;base64,{gif}" />
      <svg viewBox="0 0 {IMG_W} {IMG_H}" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;">
        <circle class="pulse" cx="{p['cx']}" cy="{p['cy']}" r="{p['r']}" />
      </svg>
      <div class="callout"><b>{th}</b><br/>{bh}<br/><br/>&gt; SELECTED BY INPUTS</div>
    </div>
    '''
    components.html(html, height=625, scrolling=False)


def render_steam_diagram(diagram_path: Path):
    if not diagram_path.exists():
        st.warning('Steam diagram GIF is missing. Keep steam_heating_system_green_bubbles_return_point_lowered.gif in this folder.')
        return
    gif = img64(diagram_path)
    html = f'''
    <style>
      .steam-wrap{{background:#000;border:1px solid #00cc44;box-shadow:0 0 12px rgba(57,255,85,.35);width:100%;}}
      .steam-wrap img{{display:block;width:100%;height:auto;}}
    </style>
    <div class="steam-wrap"><img src="data:image/gif;base64,{gif}" /></div>
    '''
    components.html(html, height=625, scrolling=False)


if not DB.exists():
    st.error('Missing hydronic_parts_database.csv')
    st.stop()

df = norm_cols(pd.read_csv(DB))

st.title('THE BOILER WIZARD')
st.caption('A Mystical, Magical, Hot Water and Steam Boiler equipment selection application for residential applications')
st.caption('Scroll down for selections')

with st.sidebar:
    if BANNER_GIF.exists():
        st.image(str(BANNER_GIF), use_container_width=True)
    else:
        st.error('Missing boiler_wizard_shimmer.gif')

    st.header('System Inputs')
    heating_system = st.selectbox('Heating System Type', ['Hot Water', 'Steam'], key='heating_system_selector')
    btu = st.number_input('BTU Capacity / Boiler Output BTU', 0, 5000000, 120000, 5000)

    pool = boiler_pool(df, heating_system)
    boiler_mfr_options = safe_unique(pool.manufacturer) if not pool.empty else []
    boiler_manufacturer = first_select('Boiler Manufacturer', boiler_mfr_options, key='boiler_manufacturer_selector')

    mfr_pool = pool[pool.manufacturer == boiler_manufacturer] if boiler_manufacturer else pool
    fuel_options = [x for x in safe_unique(mfr_pool.fuel_type) if x in ['Natural Gas', 'Oil']]
    if not fuel_options:
        fuel_options = ['Natural Gas', 'Oil']
    fuel = first_select('Boiler Fuel Type', fuel_options, key='boiler_fuel_type_selector', disabled_if_single=True)

    flue = 'N/A'
    coil = 'N/A'
    draft_hood_style = None
    air_sep_manufacturer = None
    fillopt = None
    sys_type = None
    conn = None
    mixing_valve_manufacturer = None
    mixing_valve_connection_size = None
    mixing_valve_connection_type = None

    if heating_system == 'Hot Water':
        if fuel == 'Oil':
            oil_base = mfr_pool[mfr_pool.fuel_type == 'Oil']
            flue_options = safe_unique(oil_base.flue_type) or ['Top Flue', 'Rear Flue']
            flue = first_select('Boiler Flue Type', flue_options, key='boiler_flue_type_selector', disabled_if_single=True)
            coil_options = safe_unique(oil_base[oil_base.flue_type == flue].tankless_coil) or ['Without Tankless Coil', 'With Tankless Coil']
            coil = first_select('Tankless Coil', coil_options, key='tankless_coil_selector', disabled_if_single=True)
        if fuel == 'Natural Gas':
            gas_df = mfr_pool[mfr_pool.fuel_type == 'Natural Gas']
            if 'draft_hood_style' in gas_df.columns:
                options = safe_unique(gas_df.draft_hood_style)
            else:
                options = ['Low-profile', 'Standard Draft Hood']
            if options:
                draft_hood_style = first_select('Boiler Draft Hood Style', options, key='draft_hood_style_selector', disabled_if_single=True)

        air_sep_options = safe_unique(df[df.component == 'Air Separator'].manufacturer)
        air_sep_manufacturer = first_select('Air Separator Manufacturer', air_sep_options, key='air_separator_manufacturer_selector')

        fill_options = safe_unique(df[df.component == FILL].selection_option)
        fillopt = first_select('Fill Valve / Backflow Preventer', fill_options, key='fill_option_selector')

        tank_options = [x for x in safe_unique(df[df.component == 'Expansion Tank'].system_type) if x != 'Any']
        sys_type = first_select('Expansion Tank System Type', tank_options, key='expansion_tank_system_type_selector')

        conn = st.selectbox('Pump Isolation Flange Connection Type', ['Press', 'Sweat', 'Threaded'], key='pump_connection_selector')

        if coil == 'With Tankless Coil':
            st.subheader('DHW Mixing Valve')
            _mv = df[df.component == 'Mixing Valve'].copy()
            if _mv.empty:
                st.warning('No Mixing Valve rows found in hydronic_parts_database.csv')
            else:
                mixing_valve_manufacturer = first_select('Mixing Valve Manufacturer', safe_unique(_mv.manufacturer), key='mixing_valve_manufacturer_selector')
                _mv = _mv[_mv.manufacturer == mixing_valve_manufacturer]
                mixing_valve_connection_size = first_select('Mixing Valve Connection Size', safe_unique(_mv.pipe_size), key='mixing_valve_connection_size_selector')
                _mv = _mv[_mv.pipe_size == mixing_valve_connection_size]
                mixing_valve_connection_type = first_select('Mixing Valve Connection Type', safe_unique(_mv.connection_type), key='mixing_valve_connection_type_selector')

        visible_order = [c for c in HOT_WATER_ORDER if not (c == 'Mixing Valve' and coil != 'With Tankless Coil')]
        hi = st.selectbox('Highlighted Component', visible_order, key='highlighted_component_selector')
    else:
        visible_order = STEAM_ORDER
        hi = st.selectbox('Highlighted Component', visible_order, key='highlighted_component_selector')

rows = []
if heating_system == 'Hot Water':
    for comp in visible_order:
        m = filt(df, comp, int(btu), sys_type, conn, fuel, flue, coil, fillopt,
                 boiler_manufacturer, air_sep_manufacturer, mixing_valve_manufacturer,
                 mixing_valve_connection_size, mixing_valve_connection_type,
                 draft_hood_style, heating_system)
        rows.append(equipment_row_from_match(comp, m))

    if any(x['Component'] == 'Expansion Tank' and x['Model #'] in PSHT for x in rows):
        rows.append({
            'Component': 'Expansion Tank Service Valve', 'Qty': 1, 'Manufacturer': 'Webstone',
            'Model #': 'WH41672', 'Part #': 'WH41672', 'Pipe Size': '1/2"',
            'BTU Range': 'N/A', 'Description': 'Automatically included with PSHT expansion tank selection.'
        })
else:
    m = filt(df, 'Boiler', int(btu), None, None, fuel, 'N/A', 'N/A', None,
             boiler_manufacturer, heating_system=heating_system)
    rows.append(equipment_row_from_match('Boiler', m))
    rows.extend(steam_accessory_rows(fuel))

sel = pd.DataFrame(rows)

if heating_system == 'Hot Water':
    m = filt(df, hi, int(btu), sys_type, conn, fuel, flue, coil, fillopt,
             boiler_manufacturer, air_sep_manufacturer, mixing_valve_manufacturer,
             mixing_valve_connection_size, mixing_valve_connection_type,
             draft_hood_style, heating_system)
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
            title, body = boiler_callout(m, hi, btu, fuel)
        else:
            title = 'AIR SEPARATOR'
            body = f'{r.manufacturer} {r.model_number}\\n{r.pipe_size} PIPE'
else:
    m = filt(df, 'Boiler', int(btu), None, None, fuel, 'N/A', 'N/A', None,
             boiler_manufacturer, heating_system=heating_system)
    if hi == 'Boiler':
        title, body = boiler_callout(m, hi, btu, fuel)
    elif hi == 'Steam Water Feeder':
        item = steam_accessory_rows(fuel)[0]
        title = 'STEAM WATER FEEDER'
        body = f"{item['Manufacturer']}\\n{item['Model #']}\\nPART # {item['Part #']}"
    else:
        item = steam_accessory_rows(fuel)[1]
        title = 'BACKFLOW PREVENTER'
        body = f"{item['Manufacturer']}\\n{item['Model #']}\\nPART # {item['Part #']}"

left, right = st.columns([1.65, 1])
with left:
    if heating_system == 'Steam':
        render_steam_diagram(STEAM_DIAGRAM_GIF)
    else:
        render_hot_water_diagram(HOT_WATER_DIAGRAM_GIF, hi, title, body)

with right:
    st.subheader('Highlighted Selection')
    st.dataframe(sel[sel.Component == hi], use_container_width=True, hide_index=True)

st.subheader('Selected Equipment Breakdown')
st.dataframe(sel, use_container_width=True, hide_index=True)
st.download_button(
    'Download Selected Equipment Breakdown',
    data=sel.to_csv(index=False),
    file_name='selected_equipment_breakdown.csv',
    mime='text/csv'
)

st.subheader('Available Ranges for Highlighted Component')
if heating_system == 'Steam' and hi in {'Steam Water Feeder', 'Backflow Preventer'}:
    st.dataframe(sel[sel.Component == hi], use_container_width=True, hide_index=True)
elif hi == 'Boiler':
    st.dataframe(boiler_pool(df, heating_system), use_container_width=True, hide_index=True)
else:
    st.dataframe(df[df.component == hi], use_container_width=True, hide_index=True)
