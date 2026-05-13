
import base64
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='Hydronic Selector Demo', layout='wide', initial_sidebar_state='expanded')
DATABASE_FILE = Path('hydronic_parts_database.csv')
DIAGRAM_GIF = Path('hot_water_hydronic_system_selector_demo.gif')

@st.cache_data
def load_products():
    return pd.read_csv(DATABASE_FILE)

def image_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode('utf-8')

def select_product(df, component, manufacturer, btu):
    matches = df[(df['component'] == component) & (df['manufacturer'] == manufacturer) & (df['min_btu'] <= btu) & (df['max_btu'] >= btu)].copy()
    return matches.sort_values(['min_btu', 'max_btu'], ascending=[False, True])

products = load_products()
st.title('HOT WATER HYDRONIC SYSTEM SELECTOR')
st.caption('Demo: animated diagram + dynamic air separator callout')

with st.sidebar:
    st.header('System Inputs')
    component = st.selectbox('Component', sorted(products['component'].unique()))
    manufacturers = sorted(products.loc[products['component'] == component, 'manufacturer'].unique())
    manufacturer = st.selectbox('Manufacturer', manufacturers)
    btu = st.number_input('BTU Capacity', min_value=0, max_value=5000000, value=120000, step=5000)
    st.caption('For this first demo, only the Air Separator component has rules loaded.')

matches = select_product(products, component, manufacturer, int(btu))
if matches.empty:
    selected = None
    callout_title = 'AIR SEPARATOR'
    callout_body = f'NO MATCH\n{int(btu):,} BTU'
else:
    selected = matches.iloc[0]
    callout_title = 'AIR SEPARATOR'
    callout_body = f"{selected['manufacturer']} {selected['model_number']}\n{selected['pipe_size']} PIPE\n{int(selected['min_btu']):,}–{int(selected['max_btu']):,} BTU"

left, right = st.columns([1.65, 1])
with left:
    if not DIAGRAM_GIF.exists():
        st.error('Diagram GIF is missing. Make sure hot_water_hydronic_system_selector_demo.gif is in the app folder.')
    else:
        gif64 = image_to_base64(DIAGRAM_GIF)
        html = f'''
        <style>
            .diagram-wrap {{ position: relative; width: 100%; background: #000; border: 1px solid #00cc44; box-shadow: 0 0 18px rgba(0,255,80,0.35); overflow: hidden; font-family: "Courier New", monospace; }}
            .diagram-wrap img {{ display: block; width: 100%; height: auto; }}
            .callout {{ position: absolute; left: 37.5%; top: 12.5%; color: #39ff55; background: rgba(0,0,0,0.78); border: 1px solid #39ff55; padding: 8px 11px; line-height: 1.15; font-size: clamp(11px, 1.15vw, 17px); text-shadow: 0 0 7px #39ff55; box-shadow: 0 0 12px rgba(57,255,85,0.55); white-space: pre-line; }}
            .callout::after {{ content: ""; position: absolute; left: 28px; top: 100%; width: 90px; height: 48px; border-left: 2px solid #39ff55; border-bottom: 2px solid #39ff55; transform: skewX(-28deg); filter: drop-shadow(0 0 4px #39ff55); }}
            .terminal-line {{ color: #8cff98; font-size: 0.85em; }}
        </style>
        <div class='diagram-wrap'>
            <img src='data:image/gif;base64,{gif64}' />
            <div class='callout'><b>{callout_title}</b>\n{callout_body}\n<span class='terminal-line'>&gt; SELECTED BY BTU</span></div>
        </div>
        '''
        components.html(html, height=625, scrolling=False)

with right:
    st.subheader('Recommendation')
    if selected is None:
        st.warning(f'No match found for {int(btu):,} BTU.')
    else:
        st.success(f"{selected['manufacturer']} {selected['model_number']}")
        markdown_text = (
            '**Component:** ' + str(selected['component']) + '  \n'
            + '**Manufacturer:** ' + str(selected['manufacturer']) + '  \n'
            + '**Model #:** `' + str(selected['model_number']) + '`  \n'
            + '**Part #:** `' + str(selected['part_number']) + '`  \n'
            + '**Pipe Size:** ' + str(selected['pipe_size']) + '  \n'
            + '**Range:** ' + f"{int(selected['min_btu']):,} – {int(selected['max_btu']):,} BTU" + '  \n\n'
            + '**Description:**  \n' + str(selected['description']) + '\n\n'
            + '**Notes:**  \n' + str(selected['notes'])
        )
        st.markdown(markdown_text)
        st.download_button('Download This Selection', data=matches.head(1).to_csv(index=False), file_name='selected_air_separator.csv', mime='text/csv')

st.subheader('Available Air Separator Ranges')
st.dataframe(products.sort_values(['component', 'manufacturer', 'min_btu']), use_container_width=True, hide_index=True)
st.caption('Demo only. Final component selections should be verified against manufacturer submittals, flow rate, pressure drop, temperature, system pressure, code requirements, and project conditions.')
