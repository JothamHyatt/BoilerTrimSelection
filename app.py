import base64, html as html_lib
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(page_title='Hydronic Selector Demo', layout='wide')
DB=Path('hydronic_parts_database.csv')
GIF=Path('hot_water_hydronic_system_selector_demo.gif')
IMG_W,IMG_H=980,586
FILL='Fill Valve / Backflow Preventer'
PSHT={'PSHT30','PSHT60','PSHT90'}
ORDER=['Boiler',FILL,'Air Separator','Expansion Tank','Pump Isolation Flanges']
POS={'Air Separator':{'cx':395,'cy':210,'r':30,'callout_x':410,'callout_y':70},'Expansion Tank':{'cx':395,'cy':285,'r':42,'callout_x':235,'callout_y':240},'Pump Isolation Flanges':{'cx':521,'cy':212,'r':18,'callout_x':555,'callout_y':105},'Boiler':{'cx':335,'cy':470,'r':34,'callout_x':360,'callout_y':390},FILL:{'cx':178,'cy':230,'r':40,'callout_x':215,'callout_y':120}}
st.markdown('<style>.stApp{background:#000}h1,h2,h3,label,.stCaptionContainer{font-family:Courier New,monospace!important;color:#39ff55!important}button{background:#000!important;color:#39ff55!important;border:1px solid #39ff55!important}</style>', unsafe_allow_html=True)

def clean(txt):
    return html_lib.escape(str(txt)).replace('\\n','<br/>').replace('/n','<br/>').replace('\n','<br/>')

def img64(p):
    return base64.b64encode(p.read_bytes()).decode('utf-8')

def filt(df,comp,btu,sys,conn,fuel,flue,coil,fillopt):
    f=df[df.component==comp].copy()
    if comp=='Expansion Tank': f=f[f.system_type==sys]
    if comp=='Pump Isolation Flanges': f=f[f.connection_type==conn]
    if comp=='Boiler':
        f=f[f.fuel_type==fuel]
        if fuel=='Oil': f=f[(f.flue_type==flue)&(f.tankless_coil==coil)]
    if comp==FILL: f=f[f.selection_option==fillopt]
    return f[(f.min_btu<=btu)&(f.max_btu>=btu)].sort_values(['min_btu','max_btu'])

df=pd.read_csv(DB)
st.title('HOT WATER HYDRONIC SYSTEM SELECTOR')
st.caption('Animated diagram + selected equipment breakdown')

with st.sidebar:
    btu=st.number_input('BTU Capacity / Boiler Output BTU',0,5000000,120000,5000)
    fuel=st.selectbox('Boiler Fuel Type',['Natural Gas','Oil'])
    flue='N/A'; coil='N/A'
    if fuel=='Oil':
        flue=st.selectbox('Boiler Flue Type',['Top Flue','Rear Flue'])
        coil=st.selectbox('Tankless Coil',['Without Tankless Coil','With Tankless Coil'])
    fillopt=st.selectbox('Fill Valve / Backflow Preventer',sorted([x for x in df[df.component==FILL].selection_option.unique() if x!='N/A']))
    sys=st.selectbox('Expansion Tank System Type',sorted([x for x in df[df.component=='Expansion Tank'].system_type.unique() if x!='Any']))
    conn=st.selectbox('Pump Isolation Flange Connection Type',['Press','Sweat','Threaded'])
    hi=st.selectbox('Highlighted Component',ORDER)

rows=[]
for comp in ORDER:
    m=filt(df,comp,int(btu),sys,conn,fuel,flue,coil,fillopt)
    if m.empty:
        rows.append({'Component':comp,'Qty':'','Manufacturer':'','Model #':'No match','Part #':'No match','Pipe Size':'N/A','BTU Range':'No matching range','Description':'Add a matching rule.'})
    else:
        r=m.iloc[0]
        rows.append({'Component':r.component,'Qty':int(r.quantity),'Manufacturer':r.manufacturer,'Model #':r.model_number,'Part #':r.part_number,'Pipe Size':r.pipe_size,'BTU Range':f'{int(r.min_btu):,} - {int(r.max_btu):,} BTU','Description':r.description})
if any(x['Component']=='Expansion Tank' and x['Model #'] in PSHT for x in rows):
    rows.append({'Component':'Expansion Tank Service Valve','Qty':1,'Manufacturer':'Webstone','Model #':'WH41672','Part #':'WH41672','Pipe Size':'1/2\"','BTU Range':'N/A','Description':'Automatically included with PSHT expansion tank selection.'})
sel=pd.DataFrame(rows)

m=filt(df,hi,int(btu),sys,conn,fuel,flue,coil,fillopt)
if m.empty:
    title=hi.upper(); body=f'NO MATCH\n{int(btu):,} BTU'
else:
    r=m.iloc[0]
    if hi==FILL:
        title='PRESSURE REDUCING VALVE'; body=f'{r.selection_option}\n{r.manufacturer}\nQTY {int(r.quantity)}\n{r.model_number}\n{r.pipe_size} CONNECTION'
    elif hi=='Expansion Tank':
        svc='\n+ [1] WH41672 SERVICE VALVE' if r.model_number in PSHT else ''
        title='EXPANSION TANK'; body=f'{r.manufacturer}\n{r.model_number}\n{r.system_type}\n{r.pipe_size} CONNECTION{svc}'
    elif hi=='Pump Isolation Flanges':
        title='PUMP ISOLATION FLANGES'; body=f'QTY {int(r.quantity)}\n{r.manufacturer} {r.model_number}\n{r.connection_type} / {r.pipe_size} PIPE'
    elif hi=='Boiler':
        title='BOILER'; body=f'{r.manufacturer}\n{r.model_number}\n{r.fuel_type} / {r.input_mbh} MBH IN\n{int(r.min_btu):,}-{int(r.max_btu):,} BTU OUT'
    else:
        title='AIR SEPARATOR'; body=f'{r.manufacturer} {r.model_number}\n{r.pipe_size} PIPE'

left,right=st.columns([1.65,1])
with left:
    if not GIF.exists():
        st.warning('Diagram GIF is missing. Keep hot_water_hydronic_system_selector_demo.gif in this folder.')
    else:
        p=POS[hi]; gif=img64(GIF); th=clean(title); bh=clean(body)
        cx=p["cx"]; cy=p["cy"]; rr=p["r"]; callx=p["callout_x"]; cally=p["callout_y"]
        html=f"""<style>.diagram-wrap{{background:#000;border:1px solid #00cc44}}.diagram-svg{{display:block;width:100%;height:auto}}.pulse{{fill:none;stroke:#39ff55;stroke-width:3;animation:pulse 1.1s infinite}}@keyframes pulse{{0%{{opacity:.45;stroke-width:2}}50%{{opacity:1;stroke-width:5}}100%{{opacity:.45;stroke-width:2}}}}.callout{{color:#39ff55;background:rgba(0,0,0,.84);border:1px solid #39ff55;padding:8px 11px;font-family:Courier New,monospace;font-size:15px}}</style><div class='diagram-wrap'><svg class='diagram-svg' viewBox='0 0 {IMG_W} {IMG_H}'><image href='data:image/gif;base64,{gif}' x='0' y='0' width='{IMG_W}' height='{IMG_H}'/><circle class='pulse' cx='{cx}' cy='{cy}' r='{rr}'/><foreignObject x='{callx}' y='{cally}' width='390' height='230'><div xmlns='http://www.w3.org/1999/xhtml' class='callout'><b>{th}</b><br/>{bh}<br/><span>&gt; SELECTED BY INPUTS</span></div></foreignObject></svg></div>"""
        components.html(html,height=625,scrolling=False)
with right:
    st.subheader('Highlighted Selection')
    st.dataframe(sel[sel.Component==hi],use_container_width=True,hide_index=True)

st.subheader('Selected Equipment Breakdown')
st.dataframe(sel,use_container_width=True,hide_index=True)
st.download_button('Download Selected Equipment Breakdown',data=sel.to_csv(index=False),file_name='selected_equipment_breakdown.csv',mime='text/csv')
st.subheader('Available Ranges for Highlighted Component')
st.dataframe(df[df.component==hi],use_container_width=True,hide_index=True)