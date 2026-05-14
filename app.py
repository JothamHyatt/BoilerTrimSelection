
import base64
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='Hydronic Selector Demo', layout='wide', initial_sidebar_state='expanded')
DATABASE_FILE = Path('hydronic_parts_database.csv')
DIAGRAM_GIF = Path('hot_water_hydronic_system_selector_demo.gif')
IMG_W, IMG_H = 980, 586
FILL_COMPONENT = 'Fill Valve / Backflow Preventer'
COMPONENT_ORDER = ['Boiler', FILL_COMPONENT, 'Air Separator', 'Expansion Tank', 'Pump Isolation Flanges']
COMPONENT_POSITIONS = {
    'Air Separator': {'cx':395, 'cy':210, 'r':30, 'callout_x':410, 'callout_y':70},
    'Expansion Tank': {'cx':395, 'cy':285, 'r':42, 'callout_x':235, 'callout_y':240},
    'Pump Isolation Flanges': {'cx':312, 'cy':230, 'r':24, 'callout_x':120, 'callout_y':115},
    'Boiler': {'cx':335, 'cy':470, 'r':34, 'callout_x':360, 'callout_y':390},
    FILL_COMPONENT: {'cx':230, 'cy':420, 'r':34, 'callout_x':245, 'callout_y':330},
}
REQUIRED_COLUMNS = {'component':'','manufacturer':'','system_type':'Any','connection_type':'Any','fuel_type':'N/A','flue_type':'N/A','tankless_coil':'N/A','selection_option':'N/A','input_mbh':'N/A','min_btu':0,'max_btu':0,'pipe_size':'N/A','quantity':1,'model_number':'','part_number':'','description':'','notes':''}

st.markdown('''
<style>
:root { --terminal-green:#39ff55; --terminal-dim:#8cff98; --terminal-bg:#020802; }
.stApp { background: radial-gradient(circle at 50% 10%, #061806 0%, #020802 45%, #000 100%); }
section[data-testid="stSidebar"] { background:#000 !important; border-right:1px solid var(--terminal-green); box-shadow:0 0 18px rgba(57,255,85,.25); }
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p, .stSelectbox label, .stNumberInput label, .stCheckbox label, h1, h2, h3, .stCaptionContainer { font-family:"Courier New","DejaVu Sans Mono",monospace !important; color:var(--terminal-green) !important; text-shadow:0 0 7px rgba(57,255,85,.8); }
svg, [data-testid*="icon"], [class*="icon"], [class*="Icon"], .material-icons, .material-symbols-outlined, .material-symbols-rounded, .material-symbols-sharp { font-family:initial !important; text-shadow:none !important; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stNumberInput input { background:#000 !important; color:var(--terminal-green) !important; border:1px solid var(--terminal-green) !important; border-radius:0 !important; box-shadow:inset 0 0 10px rgba(57,255,85,.18), 0 0 8px rgba(57,255,85,.22) !important; font-family:"Courier New","DejaVu Sans Mono",monospace !important; }
div[data-baseweb="select"] span:not([class*="icon"]):not([class*="Icon"]), div[data-baseweb="select"] input, div[data-baseweb="input"] input, .stNumberInput input { color:var(--terminal-green) !important; -webkit-text-fill-color:var(--terminal-green) !important; font-family:"Courier New","DejaVu Sans Mono",monospace !important; text-shadow:0 0 6px rgba(57,255,85,.75); }
div[data-baseweb="select"] svg { fill:var(--terminal-green) !important; color:var(--terminal-green) !important; }
div[data-baseweb="popover"], ul[role="listbox"] { background:#000 !important; border:1px solid var(--terminal-green) !important; box-shadow:0 0 14px rgba(57,255,85,.45) !important; }
li[role="option"], div[role="option"] { background:#000 !important; color:var(--terminal-green) !important; font-family:"Courier New","DejaVu Sans Mono",monospace !important; text-shadow:0 0 6px rgba(57,255,85,.75); }
li[role="option"]:hover, div[role="option"]:hover, li[aria-selected="true"], div[aria-selected="true"] { background:rgba(57,255,85,.16) !important; color:#baffc4 !important; }
button, .stDownloadButton button { background:#000 !important; color:var(--terminal-green) !important; border:1px solid var(--terminal-green) !important; border-radius:0 !important; font-family:"Courier New","DejaVu Sans Mono",monospace !important; }
</style>
''', unsafe_allow_html=True)

def load_products():
    df = pd.read_csv(DATABASE_FILE)
    for col, default in REQUIRED_COLUMNS.items():
        if col not in df.columns:
            df[col] = default
    for col in ['system_type','connection_type','fuel_type','flue_type','tankless_coil','selection_option','pipe_size','input_mbh']:
        df[col] = df[col].fillna(REQUIRED_COLUMNS.get(col, 'N/A'))
    df['part_number'] = df['part_number'].fillna(df['model_number'])
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)
    df['min_btu'] = pd.to_numeric(df['min_btu'], errors='coerce').fillna(0).astype(int)
    df['max_btu'] = pd.to_numeric(df['max_btu'], errors='coerce').fillna(0).astype(int)
    return df

def select_product(df, component, btu, expansion_system_type=None, pump_connection_type=None, boiler_fuel_type=None, boiler_flue_type=None, boiler_tankless_coil=None, fill_valve_option=None):
    f = df[df['component'] == component].copy()
    if component == 'Expansion Tank': f = f[f['system_type'] == expansion_system_type]
    if component == 'Pump Isolation Flanges': f = f[f['connection_type'] == pump_connection_type]
    if component == 'Boiler':
        f = f[f['fuel_type'] == boiler_fuel_type]
        if boiler_fuel_type == 'Oil':
            f = f[(f['flue_type'] == boiler_flue_type) & (f['tankless_coil'] == boiler_tankless_coil)]
    if component == FILL_COMPONENT: f = f[f['selection_option'] == fill_valve_option]
    f = f[(f['min_btu'] <= btu) & (f['max_btu'] >= btu)].copy()
    return f.sort_values(['min_btu','max_btu'], ascending=[False, True])

def make_selected_row(comp, match, btu, expansion_system_type, pump_connection_type, boiler_fuel_type, boiler_flue_type, boiler_tankless_coil, fill_valve_option):
    if match.empty:
        return {'Component':comp,'Selection Option':fill_valve_option if comp==FILL_COMPONENT else 'N/A','Qty':'','Manufacturer':'','Fuel Type':boiler_fuel_type if comp=='Boiler' else 'N/A','Input MBH':'N/A','Flue Type':boiler_flue_type if comp=='Boiler' and boiler_fuel_type=='Oil' else 'N/A','Tankless Coil':boiler_tankless_coil if comp=='Boiler' and boiler_fuel_type=='Oil' else 'N/A','Connection Type':pump_connection_type if comp=='Pump Isolation Flanges' else 'Any','System Type':expansion_system_type if comp=='Expansion Tank' else 'Any','Model #':'No match','Part #':'No match','Pipe Size':'N/A','BTU Range':'No matching range','Description':'Add a matching rule to the product database.'}
    r = match.iloc[0]
    return {'Component':r['component'],'Selection Option':r['selection_option'],'Qty':int(r['quantity']),'Manufacturer':r['manufacturer'],'Fuel Type':r['fuel_type'],'Input MBH':r['input_mbh'],'Flue Type':r['flue_type'],'Tankless Coil':r['tankless_coil'],'Connection Type':r['connection_type'],'System Type':r['system_type'],'Model #':r['model_number'],'Part #':r['part_number'],'Pipe Size':r['pipe_size'],'BTU Range':f"{int(r['min_btu']):,} – {int(r['max_btu']):,} BTU",'Description':r['description']}

def image_to_base64(path): return base64.b64encode(path.read_bytes()).decode('utf-8')

products = load_products()
st.title('HOT WATER HYDRONIC SYSTEM SELECTOR')
st.caption('Demo: animated diagram + selected equipment breakdown')
with st.sidebar:
    st.header('System Inputs')
    btu = st.number_input('BTU Capacity / Boiler Output BTU', min_value=0, max_value=5000000, value=120000, step=5000)
    boiler_fuel_type = st.selectbox('Boiler Fuel Type', ['Natural Gas','Oil'])
    boiler_flue_type, boiler_tankless_coil = 'N/A', 'N/A'
    if boiler_fuel_type == 'Oil':
        boiler_flue_type = st.selectbox('Boiler Flue Type', ['Top Flue','Rear Flue'])
        boiler_tankless_coil = st.selectbox('Tankless Coil', ['Without Tankless Coil','With Tankless Coil'])
    fill_opts = sorted([x for x in products.loc[products.component==FILL_COMPONENT,'selection_option'].dropna().unique() if x != 'N/A'])
    fill_valve_option = st.selectbox('Fill Valve / Backflow Preventer', fill_opts)
    exp_opts = sorted([x for x in products.loc[products.component=='Expansion Tank','system_type'].dropna().unique() if x != 'Any'])
    expansion_system_type = st.selectbox('Expansion Tank System Type', exp_opts)
    pump_connection_type = st.selectbox('Pump Isolation Flange Connection Type', ['Press','Sweat','Threaded'])
    highlighted_component = st.selectbox('Highlighted Component', COMPONENT_ORDER)
    calibration_mode = st.checkbox('Show highlight calibration controls', value=False)

selected_rows=[]
for comp in COMPONENT_ORDER:
    m = select_product(products, comp, int(btu), expansion_system_type, pump_connection_type, boiler_fuel_type, boiler_flue_type, boiler_tankless_coil, fill_valve_option)
    selected_rows.append(make_selected_row(comp, m, int(btu), expansion_system_type, pump_connection_type, boiler_fuel_type, boiler_flue_type, boiler_tankless_coil, fill_valve_option))
selected_equipment = pd.DataFrame(selected_rows)

matches = select_product(products, highlighted_component, int(btu), expansion_system_type, pump_connection_type, boiler_fuel_type, boiler_flue_type, boiler_tankless_coil, fill_valve_option)
selected = None if matches.empty else matches.iloc[0]
if selected is None:
    callout_title = highlighted_component.upper(); callout_body = f'NO MATCH\n{int(btu):,} BTU'
elif highlighted_component == 'Boiler':
    oil_line = f"\n{selected['flue_type']}\n{selected['tankless_coil']}" if selected['fuel_type']=='Oil' else ''
    callout_title='BOILER'; callout_body=f"{selected['manufacturer']}\n{selected['model_number']}\n{selected['fuel_type']} / {selected['input_mbh']} MBH IN{oil_line}\n{int(selected['min_btu']):,}–{int(selected['max_btu']):,} BTU OUT"
elif highlighted_component == FILL_COMPONENT:
    callout_title='PRESSURE REDUCING VALVE'; callout_body=f"{selected['selection_option']}\n{selected['manufacturer']}\nQTY {int(selected['quantity'])}\n{selected['model_number']}\n{selected['pipe_size']} CONNECTION"
elif highlighted_component == 'Pump Isolation Flanges':
    callout_title='PUMP ISOLATION FLANGES'; callout_body=f"QTY {int(selected['quantity'])}\n{selected['manufacturer']} {selected['model_number']}\n{selected['connection_type']} / {selected['pipe_size']} PIPE"
elif highlighted_component == 'Expansion Tank':
    callout_title='EXPANSION TANK'; callout_body=f"{selected['manufacturer']}\n{selected['model_number']}\n{selected['system_type']}"
else:
    callout_title='AIR SEPARATOR'; callout_body=f"{selected['manufacturer']} {selected['model_number']}\n{selected['pipe_size']} PIPE"

pos = COMPONENT_POSITIONS[highlighted_component].copy()
if calibration_mode:
    with st.sidebar:
        st.subheader('Highlight Calibration')
        pos['cx'] = st.slider('Circle center X',0,IMG_W,int(pos['cx']))
        pos['cy'] = st.slider('Circle center Y',0,IMG_H,int(pos['cy']))
        pos['r'] = st.slider('Circle radius',10,120,int(pos['r']))
        pos['callout_x'] = st.slider('Callout X',0,IMG_W,int(pos['callout_x']))
        pos['callout_y'] = st.slider('Callout Y',0,IMG_H,int(pos['callout_y']))
        st.code(f"'{highlighted_component}': {{'cx': {pos['cx']}, 'cy': {pos['cy']}, 'r': {pos['r']}, 'callout_x': {pos['callout_x']}, 'callout_y': {pos['callout_y']}}}")

left,right = st.columns([1.65,1])
with left:
    if not DIAGRAM_GIF.exists():
        st.warning('Diagram GIF is missing. Keep hot_water_hydronic_system_selector_demo.gif in the app folder.')
    else:
        gif64 = image_to_base64(DIAGRAM_GIF)
        html = f'''
        <style>.diagram-wrap {{ width:100%; background:#000; border:1px solid #00cc44; box-shadow:0 0 18px rgba(0,255,80,.35); font-family:"Courier New", monospace; }} .diagram-svg {{ display:block; width:100%; height:auto; }} .pulse-ring {{ fill:none; stroke:#39ff55; stroke-width:3; filter:drop-shadow(0 0 5px #39ff55); animation:pulseStroke 1.1s infinite; }} @keyframes pulseStroke {{ 0% {{ opacity:.45; stroke-width:2; }} 50% {{ opacity:1; stroke-width:5; }} 100% {{ opacity:.45; stroke-width:2; }} }} .callout-html {{ color:#39ff55; background:rgba(0,0,0,.84); border:1px solid #39ff55; padding:8px 11px; line-height:1.15; font-size:15px; text-shadow:0 0 7px #39ff55; box-shadow:0 0 12px rgba(57,255,85,.55); white-space:pre-line; max-width:330px; }} .terminal-line {{ color:#8cff98; font-size:.85em; }}</style>
        <div class='diagram-wrap'><svg class='diagram-svg' viewBox='0 0 {IMG_W} {IMG_H}' preserveAspectRatio='xMidYMid meet'><image href='data:image/gif;base64,{gif64}' x='0' y='0' width='{IMG_W}' height='{IMG_H}' /><circle class='pulse-ring' cx='{pos['cx']}' cy='{pos['cy']}' r='{pos['r']}' /><foreignObject x='{pos['callout_x']}' y='{pos['callout_y']}' width='390' height='230'><div xmlns='http://www.w3.org/1999/xhtml' class='callout-html'><b>{callout_title}</b>\n{callout_body}\n<span class='terminal-line'>&gt; SELECTED BY INPUTS</span></div></foreignObject></svg></div>
        '''
        components.html(html, height=625, scrolling=False)
with right:
    st.subheader('Highlighted Selection')
    if selected is None:
        st.warning(f'No match found for {highlighted_component}, {int(btu):,} BTU.')
    else:
        row = selected_equipment[selected_equipment.Component == highlighted_component].iloc[0]
        st.success(f"{row['Manufacturer']} {row['Model #']}")
        for key,val in row.items():
            st.markdown(f"**{key}:** {val}")

st.subheader('Selected Equipment Breakdown')
st.dataframe(selected_equipment, use_container_width=True, hide_index=True)
st.download_button('Download Selected Equipment Breakdown', data=selected_equipment.to_csv(index=False), file_name='selected_equipment_breakdown.csv', mime='text/csv')
st.subheader('Available Ranges for Highlighted Component')
st.dataframe(products[products.component == highlighted_component], use_container_width=True, hide_index=True)
st.caption('Demo only. Final component selections should be verified against manufacturer submittals, flow rate, pressure drop, temperature, system pressure, code requirements, and project conditions.')
