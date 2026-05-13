
import base64
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='Hydronic Selector Demo', layout='wide', initial_sidebar_state='expanded')
DATABASE_FILE = Path('hydronic_parts_database.csv')
DIAGRAM_GIF = Path('hot_water_hydronic_system_selector_demo.gif')
IMG_W = 980
IMG_H = 586

REQUIRED_COLUMNS = {'component':'','manufacturer':'','system_type':'Any','min_btu':0,'max_btu':0,'pipe_size':'N/A','model_number':'','part_number':'','description':'','notes':''}

# These are center-point coordinates in the resized 980 x 586 diagram.
# Expansion tank is intentionally centered below the air separator on the round tank body,
# not on the arrow/leader next to the tank.
COMPONENT_POSITIONS = {
    'Air Separator': {'cx': 395, 'cy': 210, 'r': 30, 'callout_x': 410, 'callout_y': 70},
    'Expansion Tank': {'cx': 395, 'cy': 285, 'r': 42, 'callout_x': 235, 'callout_y': 240},
}

@st.cache_data
def load_products():
    df = pd.read_csv(DATABASE_FILE)
    for col, default in REQUIRED_COLUMNS.items():
        if col not in df.columns:
            df[col] = default
    df['system_type'] = df['system_type'].fillna('Any')
    df['pipe_size'] = df['pipe_size'].fillna('N/A')
    df['part_number'] = df['part_number'].fillna(df['model_number'])
    df['min_btu'] = pd.to_numeric(df['min_btu'], errors='coerce').fillna(0).astype(int)
    df['max_btu'] = pd.to_numeric(df['max_btu'], errors='coerce').fillna(0).astype(int)
    return df

def image_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode('utf-8')

def select_product(df, component, manufacturer, btu, system_type=None):
    filtered = df[(df['component'] == component) & (df['manufacturer'] == manufacturer)].copy()
    if component == 'Expansion Tank' and system_type:
        filtered = filtered[filtered['system_type'] == system_type]
    matches = filtered[(filtered['min_btu'] <= btu) & (filtered['max_btu'] >= btu)].copy()
    return matches.sort_values(['min_btu', 'max_btu'], ascending=[False, True])

def current_ranges(df, component, manufacturer, system_type=None):
    filtered = df[(df['component'] == component) & (df['manufacturer'] == manufacturer)].copy()
    if component == 'Expansion Tank' and system_type:
        filtered = filtered[filtered['system_type'] == system_type]
    sort_cols = [c for c in ['system_type', 'min_btu'] if c in filtered.columns]
    return filtered.sort_values(sort_cols) if sort_cols else filtered

products = load_products()
st.title('HOT WATER HYDRONIC SYSTEM SELECTOR')
st.caption('Demo: animated diagram + dynamic component callout')

with st.sidebar:
    st.header('System Inputs')
    component = st.selectbox('Component', sorted(products['component'].dropna().unique()))
    manufacturers = sorted(products.loc[products['component'] == component, 'manufacturer'].dropna().unique())
    manufacturer = st.selectbox('Manufacturer', manufacturers)
    system_type = None
    if component == 'Expansion Tank':
        system_types = sorted(products.loc[(products['component'] == component) & (products['manufacturer'] == manufacturer), 'system_type'].dropna().unique())
        system_types = [s for s in system_types if s != 'Any'] or ['Any']
        system_type = st.selectbox('System Type', system_types)
    else:
        st.info('System Type is only required for Expansion Tank selections in this demo.')
    btu = st.number_input('BTU Capacity', min_value=0, max_value=5000000, value=120000, step=5000)

    st.divider()
    calibration_mode = st.checkbox('Show highlight calibration controls', value=False)

matches = select_product(products, component, manufacturer, int(btu), system_type)
if matches.empty:
    selected = None
    callout_title = component.upper()
    callout_body = f'NO MATCH\n{int(btu):,} BTU'
else:
    selected = matches.iloc[0]
    callout_title = str(selected['component']).upper()
    if selected['component'] == 'Air Separator':
        callout_body = f"{selected['manufacturer']} {selected['model_number']}\n{selected['pipe_size']} PIPE\n{int(selected['min_btu']):,}–{int(selected['max_btu']):,} BTU"
    else:
        callout_body = f"{selected['manufacturer']}\n{selected['model_number']}\n{selected['system_type']}\n{int(selected['min_btu']):,}–{int(selected['max_btu']):,} BTU"

pos = COMPONENT_POSITIONS.get(component, COMPONENT_POSITIONS['Air Separator']).copy()

if calibration_mode:
    with st.sidebar:
        st.subheader('Highlight Calibration')
        pos['cx'] = st.slider('Circle center X', 0, IMG_W, int(pos['cx']))
        pos['cy'] = st.slider('Circle center Y', 0, IMG_H, int(pos['cy']))
        pos['r'] = st.slider('Circle radius', 10, 120, int(pos['r']))
        pos['callout_x'] = st.slider('Callout X', 0, IMG_W, int(pos['callout_x']))
        pos['callout_y'] = st.slider('Callout Y', 0, IMG_H, int(pos['callout_y']))
        st.code(f"'{component}': {{'cx': {pos['cx']}, 'cy': {pos['cy']}, 'r': {pos['r']}, 'callout_x': {pos['callout_x']}, 'callout_y': {pos['callout_y']}}}")

left, right = st.columns([1.65, 1])
with left:
    if not DIAGRAM_GIF.exists():
        st.warning('Diagram GIF is missing. The selector will still work, but the animated diagram will not display until hot_water_hydronic_system_selector_demo.gif is added to the app folder.')
    else:
        gif64 = image_to_base64(DIAGRAM_GIF)
        html = f'''
        <style>
            .diagram-wrap {{ width: 100%; background: #000; border: 1px solid #00cc44; box-shadow: 0 0 18px rgba(0,255,80,0.35); font-family: "Courier New", monospace; }}
            .diagram-svg {{ display: block; width: 100%; height: auto; }}
            .pulse-ring {{ fill: none; stroke: #39ff55; stroke-width: 3; filter: drop-shadow(0 0 5px #39ff55); animation: pulseStroke 1.1s infinite; }}
            @keyframes pulseStroke {{ 0% {{ opacity: 0.45; stroke-width: 2; }} 50% {{ opacity: 1.0; stroke-width: 5; }} 100% {{ opacity: 0.45; stroke-width: 2; }} }}
            .callout-html {{ color: #39ff55; background: rgba(0,0,0,0.84); border: 1px solid #39ff55; padding: 8px 11px; line-height: 1.15; font-size: 15px; text-shadow: 0 0 7px #39ff55; box-shadow: 0 0 12px rgba(57,255,85,0.55); white-space: pre-line; max-width: 285px; }}
            .terminal-line {{ color: #8cff98; font-size: 0.85em; }}
        </style>
        <div class='diagram-wrap'>
            <svg class='diagram-svg' viewBox='0 0 {IMG_W} {IMG_H}' preserveAspectRatio='xMidYMid meet'>
                <image href='data:image/gif;base64,{gif64}' x='0' y='0' width='{IMG_W}' height='{IMG_H}' />
                <circle class='pulse-ring' cx='{pos['cx']}' cy='{pos['cy']}' r='{pos['r']}' />
                <foreignObject x='{pos['callout_x']}' y='{pos['callout_y']}' width='320' height='160'>
                    <div xmlns='http://www.w3.org/1999/xhtml' class='callout-html'><b>{callout_title}</b>\n{callout_body}\n<span class='terminal-line'>&gt; SELECTED BY BTU</span></div>
                </foreignObject>
            </svg>
        </div>
        '''
        components.html(html, height=625, scrolling=False)

with right:
    st.subheader('Recommendation')
    if selected is None:
        st.warning(f'No match found for {component}, {manufacturer}, {int(btu):,} BTU.')
    else:
        st.success(f"{selected['manufacturer']} {selected['model_number']}")
        lines = [f"**Component:** {selected['component']}", f"**Manufacturer:** {selected['manufacturer']}", f"**Model #:** `{selected['model_number']}`", f"**Part #:** `{selected['part_number']}`", f"**BTU Range:** {int(selected['min_btu']):,} – {int(selected['max_btu']):,} BTU"]
        if selected['component'] == 'Expansion Tank':
            lines.insert(2, f"**System Type:** {selected['system_type']}")
        else:
            lines.append(f"**Pipe Size:** {selected['pipe_size']}")
        st.markdown('  \n'.join(lines) + f"\n\n**Description:**  \n{selected['description']}\n\n**Notes:**  \n{selected['notes']}")
        st.download_button('Download This Selection', data=matches.head(1).to_csv(index=False), file_name='selected_hydronic_component.csv', mime='text/csv')

st.subheader('Available Ranges for Current Selection')
st.dataframe(current_ranges(products, component, manufacturer, system_type), use_container_width=True, hide_index=True)
st.caption('Demo only. Final component selections should be verified against manufacturer submittals, flow rate, pressure drop, temperature, system pressure, code requirements, and project conditions.')
