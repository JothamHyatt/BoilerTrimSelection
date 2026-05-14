
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

REQUIRED_COLUMNS = {
    'component':'','manufacturer':'','system_type':'Any','connection_type':'Any',
    'min_btu':0,'max_btu':0,'pipe_size':'N/A','quantity':1,
    'model_number':'','part_number':'','description':'','notes':''
}
COMPONENT_POSITIONS = {
    'Air Separator': {'cx':395, 'cy':210, 'r':30, 'callout_x':410, 'callout_y':70},
    'Expansion Tank': {'cx':395, 'cy':285, 'r':42, 'callout_x':235, 'callout_y':240},
    # Patch applied: moved onto the right-hand end of the circulator symbol.
    'Pump Isolation Flanges': {'cx':312, 'cy':230, 'r':24, 'callout_x':120, 'callout_y':115},
}
COMPONENT_ORDER = ['Air Separator', 'Expansion Tank', 'Pump Isolation Flanges']

APPLE_II_CSS = '''
<style>
:root {
    --terminal-green: #39ff55;
    --terminal-dim: #8cff98;
    --terminal-bg: #020802;
}
.stApp {
    background: radial-gradient(circle at 50% 10%, #061806 0%, #020802 45%, #000 100%);
}
section[data-testid="stSidebar"] {
    background: #000 !important;
    border-right: 1px solid var(--terminal-green);
    box-shadow: 0 0 18px rgba(57,255,85,.25);
}
/* Target labels/text only; do NOT style every child, because BaseWeb icon fonts can render text such as keyboard_double_arrow_down. */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
.stSelectbox label,
.stNumberInput label,
.stCheckbox label,
h1, h2, h3, .stCaptionContainer {
    font-family: "Courier New", "DejaVu Sans Mono", monospace !important;
    color: var(--terminal-green) !important;
    text-shadow: 0 0 7px rgba(57,255,85,.8);
}
/* Keep icon ligature fonts and SVG icons intact. */
svg,
[data-testid*="icon"],
[class*="icon"],
[class*="Icon"],
.material-icons,
.material-symbols-outlined,
.material-symbols-rounded,
.material-symbols-sharp {
    font-family: initial !important;
    text-shadow: none !important;
}
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
.stNumberInput input {
    background: #000 !important;
    color: var(--terminal-green) !important;
    border: 1px solid var(--terminal-green) !important;
    border-radius: 0 !important;
    box-shadow: inset 0 0 10px rgba(57,255,85,.18), 0 0 8px rgba(57,255,85,.22) !important;
    font-family: "Courier New", "DejaVu Sans Mono", monospace !important;
}
/* Style select/value text, but avoid icon containers. */
div[data-baseweb="select"] span:not([class*="icon"]):not([class*="Icon"]),
div[data-baseweb="select"] input,
div[data-baseweb="input"] input,
.stNumberInput input {
    color: var(--terminal-green) !important;
    -webkit-text-fill-color: var(--terminal-green) !important;
    font-family: "Courier New", "DejaVu Sans Mono", monospace !important;
    text-shadow: 0 0 6px rgba(57,255,85,.75);
}
div[data-baseweb="select"] svg {
    fill: var(--terminal-green) !important;
    color: var(--terminal-green) !important;
}
div[data-baseweb="popover"],
ul[role="listbox"] {
    background: #000 !important;
    border: 1px solid var(--terminal-green) !important;
    box-shadow: 0 0 14px rgba(57,255,85,.45) !important;
}
li[role="option"],
div[role="option"] {
    background: #000 !important;
    color: var(--terminal-green) !important;
    font-family: "Courier New", "DejaVu Sans Mono", monospace !important;
    text-shadow: 0 0 6px rgba(57,255,85,.75);
}
li[role="option"]:hover,
div[role="option"]:hover,
li[aria-selected="true"],
div[aria-selected="true"] {
    background: rgba(57,255,85,.16) !important;
    color: #baffc4 !important;
}
button, .stDownloadButton button {
    background: #000 !important;
    color: var(--terminal-green) !important;
    border: 1px solid var(--terminal-green) !important;
    border-radius: 0 !important;
    font-family: "Courier New", "DejaVu Sans Mono", monospace !important;
    text-shadow: 0 0 6px rgba(57,255,85,.75);
}
</style>
'''
st.markdown(APPLE_II_CSS, unsafe_allow_html=True)

def load_products():
    # Not cached: prevents stale CSV values from hiding updated flange pipe sizes.
    df = pd.read_csv(DATABASE_FILE)
    for col, default in REQUIRED_COLUMNS.items():
        if col not in df.columns:
            df[col] = default
    df['system_type'] = df['system_type'].fillna('Any')
    df['connection_type'] = df['connection_type'].fillna('Any')
    df['pipe_size'] = df['pipe_size'].fillna('N/A')
    df['part_number'] = df['part_number'].fillna(df['model_number'])
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)
    df['min_btu'] = pd.to_numeric(df['min_btu'], errors='coerce').fillna(0).astype(int)
    df['max_btu'] = pd.to_numeric(df['max_btu'], errors='coerce').fillna(0).astype(int)
    return df

def image_to_base64(path):
    return base64.b64encode(path.read_bytes()).decode('utf-8')

def select_product(df, component, btu, system_type=None, connection_type=None):
    filtered = df[df['component'] == component].copy()
    if component == 'Expansion Tank' and system_type:
        filtered = filtered[filtered['system_type'] == system_type]
    if component == 'Pump Isolation Flanges' and connection_type:
        filtered = filtered[filtered['connection_type'] == connection_type]
    matches = filtered[(filtered['min_btu'] <= btu) & (filtered['max_btu'] >= btu)].copy()
    return matches.sort_values(['min_btu','max_btu'], ascending=[False, True])

def build_selected_equipment(df, btu, expansion_system_type, pump_connection_type):
    selected_rows=[]
    for comp in COMPONENT_ORDER:
        system_type = expansion_system_type if comp == 'Expansion Tank' else None
        connection_type = pump_connection_type if comp == 'Pump Isolation Flanges' else None
        match = select_product(df, comp, btu, system_type, connection_type)
        if match.empty:
            selected_rows.append({'Component':comp,'Qty':'','Manufacturer':'','Connection Type':connection_type or 'Any','System Type':system_type or 'Any','Model #':'No match','Part #':'No match','Pipe Size':'N/A','BTU Range':'No matching range','Description':'Add a matching rule to the product database.'})
        else:
            row=match.iloc[0]
            selected_rows.append({'Component':row['component'],'Qty':int(row['quantity']),'Manufacturer':row['manufacturer'],'Connection Type':row['connection_type'],'System Type':row['system_type'],'Model #':row['model_number'],'Part #':row['part_number'],'Pipe Size':row['pipe_size'],'BTU Range':f"{int(row['min_btu']):,} – {int(row['max_btu']):,} BTU",'Description':row['description']})
    return pd.DataFrame(selected_rows)

def current_ranges(df, component, system_type=None, connection_type=None):
    filtered=df[df['component']==component].copy()
    if component == 'Expansion Tank' and system_type:
        filtered=filtered[filtered['system_type']==system_type]
    if component == 'Pump Isolation Flanges' and connection_type:
        filtered=filtered[filtered['connection_type']==connection_type]
    sort_cols=[c for c in ['connection_type','system_type','min_btu'] if c in filtered.columns]
    return filtered.sort_values(sort_cols) if sort_cols else filtered

products=load_products()
st.title('HOT WATER HYDRONIC SYSTEM SELECTOR')
st.caption('Demo: animated diagram + selected equipment breakdown')
expansion_system_types=sorted(products.loc[products['component']=='Expansion Tank','system_type'].dropna().unique())
expansion_system_types=[s for s in expansion_system_types if s!='Any'] or ['Any']
pump_connection_types=sorted(products.loc[products['component']=='Pump Isolation Flanges','connection_type'].dropna().unique())
pump_connection_types=[s for s in pump_connection_types if s!='Any'] or ['Any']

with st.sidebar:
    st.header('System Inputs')
    btu=st.number_input('BTU Capacity', min_value=0, max_value=5000000, value=120000, step=5000)
    expansion_system_type=st.selectbox('Expansion Tank System Type', expansion_system_types)
    pump_connection_type=st.selectbox('Pump Isolation Flange Connection Type', pump_connection_types)
    highlighted_component=st.selectbox('Highlighted Component', COMPONENT_ORDER)
    st.divider()
    calibration_mode=st.checkbox('Show highlight calibration controls', value=False)

selected_equipment=build_selected_equipment(products, int(btu), expansion_system_type, pump_connection_type)
highlight_system_type=expansion_system_type if highlighted_component=='Expansion Tank' else None
highlight_connection_type=pump_connection_type if highlighted_component=='Pump Isolation Flanges' else None
matches=select_product(products, highlighted_component, int(btu), highlight_system_type, highlight_connection_type)

if matches.empty:
    selected=None
    callout_title=highlighted_component.upper()
    callout_body=f'NO MATCH\n{int(btu):,} BTU'
else:
    selected=matches.iloc[0]
    callout_title=str(selected['component']).upper()
    if selected['component']=='Air Separator':
        callout_body=f"{selected['manufacturer']} {selected['model_number']}\n{selected['pipe_size']} PIPE\n{int(selected['min_btu']):,}–{int(selected['max_btu']):,} BTU"
    elif selected['component']=='Expansion Tank':
        callout_body=f"{selected['manufacturer']}\n{selected['model_number']}\n{selected['system_type']}\n{int(selected['min_btu']):,}–{int(selected['max_btu']):,} BTU"
    else:
        callout_body=f"QTY {int(selected['quantity'])}\n{selected['manufacturer']} {selected['model_number']}\n{selected['connection_type']} / {selected['pipe_size']} PIPE\n{int(selected['min_btu']):,}–{int(selected['max_btu']):,} BTU"

pos=COMPONENT_POSITIONS.get(highlighted_component, COMPONENT_POSITIONS['Air Separator']).copy()
if calibration_mode:
    with st.sidebar:
        st.subheader('Highlight Calibration')
        pos['cx']=st.slider('Circle center X', 0, IMG_W, int(pos['cx']))
        pos['cy']=st.slider('Circle center Y', 0, IMG_H, int(pos['cy']))
        pos['r']=st.slider('Circle radius', 10, 120, int(pos['r']))
        pos['callout_x']=st.slider('Callout X', 0, IMG_W, int(pos['callout_x']))
        pos['callout_y']=st.slider('Callout Y', 0, IMG_H, int(pos['callout_y']))
        st.code(f"'{highlighted_component}': {{'cx': {pos['cx']}, 'cy': {pos['cy']}, 'r': {pos['r']}, 'callout_x': {pos['callout_x']}, 'callout_y': {pos['callout_y']}}}")

left, right=st.columns([1.65,1])
with left:
    if not DIAGRAM_GIF.exists():
        st.warning('Diagram GIF is missing. The selector will still work, but the animated diagram will not display until hot_water_hydronic_system_selector_demo.gif is added to the app folder.')
    else:
        gif64=image_to_base64(DIAGRAM_GIF)
        html=f'''
        <style>
        .diagram-wrap {{ width:100%; background:#000; border:1px solid #00cc44; box-shadow:0 0 18px rgba(0,255,80,.35); font-family:"Courier New", monospace; }}
        .diagram-svg {{ display:block; width:100%; height:auto; }}
        .pulse-ring {{ fill:none; stroke:#39ff55; stroke-width:3; filter:drop-shadow(0 0 5px #39ff55); animation:pulseStroke 1.1s infinite; }}
        @keyframes pulseStroke {{ 0% {{ opacity:.45; stroke-width:2; }} 50% {{ opacity:1; stroke-width:5; }} 100% {{ opacity:.45; stroke-width:2; }} }}
        .callout-html {{ color:#39ff55; background:rgba(0,0,0,.84); border:1px solid #39ff55; padding:8px 11px; line-height:1.15; font-size:15px; text-shadow:0 0 7px #39ff55; box-shadow:0 0 12px rgba(57,255,85,.55); white-space:pre-line; max-width:300px; }}
        .terminal-line {{ color:#8cff98; font-size:.85em; }}
        </style>
        <div class='diagram-wrap'>
          <svg class='diagram-svg' viewBox='0 0 {IMG_W} {IMG_H}' preserveAspectRatio='xMidYMid meet'>
            <image href='data:image/gif;base64,{gif64}' x='0' y='0' width='{IMG_W}' height='{IMG_H}' />
            <circle class='pulse-ring' cx='{pos['cx']}' cy='{pos['cy']}' r='{pos['r']}' />
            <foreignObject x='{pos['callout_x']}' y='{pos['callout_y']}' width='360' height='180'>
              <div xmlns='http://www.w3.org/1999/xhtml' class='callout-html'><b>{callout_title}</b>\n{callout_body}\n<span class='terminal-line'>&gt; SELECTED BY BTU</span></div>
            </foreignObject>
          </svg>
        </div>
        '''
        components.html(html, height=625, scrolling=False)

with right:
    st.subheader('Highlighted Selection')
    if selected is None:
        st.warning(f'No match found for {highlighted_component}, {int(btu):,} BTU.')
    else:
        st.success(f"{selected['manufacturer']} {selected['model_number']}")
        lines=[f"**Component:** {selected['component']}", f"**Qty:** {int(selected['quantity'])}", f"**Manufacturer:** {selected['manufacturer']}", f"**Model #:** `{selected['model_number']}`", f"**Part #:** `{selected['part_number']}`", f"**BTU Range:** {int(selected['min_btu']):,} – {int(selected['max_btu']):,} BTU"]
        if selected['component']=='Expansion Tank':
            lines.insert(3, f"**System Type:** {selected['system_type']}")
        if selected['component']=='Pump Isolation Flanges':
            lines.insert(3, f"**Connection Type:** {selected['connection_type']}")
            lines.insert(4, f"**Pipe Size:** {selected['pipe_size']}")
        if selected['component']=='Air Separator':
            lines.append(f"**Pipe Size:** {selected['pipe_size']}")
        st.markdown('  \n'.join(lines) + f"\n\n**Description:**  \n{selected['description']}")

st.subheader('Selected Equipment Breakdown')
st.dataframe(selected_equipment, use_container_width=True, hide_index=True)
st.download_button('Download Selected Equipment Breakdown', data=selected_equipment.to_csv(index=False), file_name='selected_equipment_breakdown.csv', mime='text/csv')
with st.expander('Detailed Component Cards', expanded=True):
    for _, row in selected_equipment.iterrows():
        card_lines=[f"### {row['Component']}", f"**Qty:** {row['Qty']}", f"**Manufacturer:** {row['Manufacturer']}", f"**Model #:** `{row['Model #']}`", f"**Part #:** `{row['Part #']}`", f"**Connection Type:** {row['Connection Type']}", f"**System Type:** {row['System Type']}", f"**Pipe Size:** {row['Pipe Size']}", f"**BTU Range:** {row['BTU Range']}", f"**Description:** {row['Description']}"]
        st.markdown('  \n'.join(card_lines))
st.subheader('Available Ranges for Highlighted Component')
st.dataframe(current_ranges(products, highlighted_component, highlight_system_type, highlight_connection_type), use_container_width=True, hide_index=True)
st.caption('Demo only. Final component selections should be verified against manufacturer submittals, flow rate, pressure drop, temperature, system pressure, code requirements, and project conditions.')
