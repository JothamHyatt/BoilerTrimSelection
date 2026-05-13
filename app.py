
import base64
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='Hydronic Selector Demo', layout='wide', initial_sidebar_state='expanded')
DATABASE_FILE = Path('hydronic_parts_database.csv')
DIAGRAM_GIF = Path('hot_water_hydronic_system_selector_demo.gif')

REQUIRED_COLUMNS = {'component':'','manufacturer':'','system_type':'Any','min_btu':0,'max_btu':0,'pipe_size':'N/A','model_number':'','part_number':'','description':'','notes':''}
COMPONENT_POSITIONS = {
    'Air Separator': {'callout_left':'37.5%','callout_top':'12.5%','highlight_left':'39.2%','highlight_top':'28.0%','highlight_size':'46px','pointer_width':'90px','pointer_height':'48px'},
    'Expansion Tank': {'callout_left':'14.0%','callout_top':'35.0%','highlight_left':'21.5%','highlight_top':'43.0%','highlight_size':'58px','pointer_width':'78px','pointer_height':'42px'},
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

pos = COMPONENT_POSITIONS.get(component, COMPONENT_POSITIONS['Air Separator'])
left, right = st.columns([1.65, 1])
with left:
    if not DIAGRAM_GIF.exists():
        st.warning('Diagram GIF is missing. The selector will still work, but the animated diagram will not display until hot_water_hydronic_system_selector_demo.gif is added to the app folder.')
    else:
        gif64 = image_to_base64(DIAGRAM_GIF)
        html = f'''
        <style>
            .diagram-wrap {{ position: relative; width: 100%; background: #000; border: 1px solid #00cc44; box-shadow: 0 0 18px rgba(0,255,80,0.35); overflow: hidden; font-family: "Courier New", monospace; }}
            .diagram-wrap img {{ display: block; width: 100%; height: auto; }}
            .component-highlight {{ position: absolute; left: {pos['highlight_left']}; top: {pos['highlight_top']}; width: {pos['highlight_size']}; height: {pos['highlight_size']}; border: 2px solid #39ff55; border-radius: 50%; box-shadow: 0 0 10px #39ff55, inset 0 0 10px rgba(57,255,85,0.35); animation: pulse 1.1s infinite; pointer-events: none; }}
            @keyframes pulse {{ 0% {{ transform: scale(0.92); opacity: 0.45; }} 50% {{ transform: scale(1.15); opacity: 1.0; }} 100% {{ transform: scale(0.92); opacity: 0.45; }} }}
            .callout {{ position: absolute; left: {pos['callout_left']}; top: {pos['callout_top']}; color: #39ff55; background: rgba(0,0,0,0.82); border: 1px solid #39ff55; padding: 8px 11px; line-height: 1.15; font-size: clamp(10px, 1.05vw, 16px); text-shadow: 0 0 7px #39ff55; box-shadow: 0 0 12px rgba(57,255,85,0.55); white-space: pre-line; max-width: 270px; }}
            .callout::after {{ content: ""; position: absolute; left: 28px; top: 100%; width: {pos['pointer_width']}; height: {pos['pointer_height']}; border-left: 2px solid #39ff55; border-bottom: 2px solid #39ff55; transform: skewX(-28deg); filter: drop-shadow(0 0 4px #39ff55); }}
            .terminal-line {{ color: #8cff98; font-size: 0.85em; }}
        </style>
        <div class='diagram-wrap'>
            <img src='data:image/gif;base64,{gif64}' />
            <div class='component-highlight'></div>
            <div class='callout'><b>{callout_title}</b>\n{callout_body}\n<span class='terminal-line'>&gt; SELECTED BY BTU</span></div>
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
