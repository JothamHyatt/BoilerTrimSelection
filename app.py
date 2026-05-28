
import base64
import html as html_lib
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='The Boiler Wizard', layout='wide', initial_sidebar_state='expanded')
DB=Path('hydronic_parts_database.csv')
BANNER_GIF=Path('boiler_wizard_shimmer.gif')
DIAGRAM_GIF=Path('hot_water_hydronic_system_selector_demo.gif')
IMG_W,IMG_H=980,586
FILL='Fill Valve / Backflow Preventer'
PSHT={'PSHT30','PSHT60','PSHT90'}
ORDER=['Boiler',FILL,'Air Separator','Expansion Tank','Mixing Valve','Pump Isolation Flanges']
POS={'Air Separator':{'cx':395,'cy':210,'r':30,'callout_x':410,'callout_y':70},'Expansion Tank':{'cx':395,'cy':285,'r':42,'callout_x':235,'callout_y':240},'Pump Isolation Flanges':{'cx':521,'cy':212,'r':18,'callout_x':555,'callout_y':105},'Boiler':{'cx':335,'cy':470,'r':34,'callout_x':360,'callout_y':390},FILL:{'cx':178,'cy':230,'r':40,'callout_x':215,'callout_y':120}}

st.markdown('''<style>.stApp{background:#000}section[data-testid="stSidebar"]{background:#000!important;border-right:1px solid #39ff55}h1,h2,h3,label,.stCaptionContainer{font-family:"Courier New",monospace!important;color:#39ff55!important}div[data-baseweb="select"]>div,div[data-baseweb="input"]>div,.stNumberInput input{background:#000!important;color:#39ff55!important;border:1px solid #39ff55!important;border-radius:0!important;font-family:"Courier New",monospace!important}button{background:#000!important;color:#39ff55!important;border:1px solid #39ff55!important}</style>''', unsafe_allow_html=True)

def img64(path):
    return base64.b64encode(path.read_bytes()).decode('utf-8')

def clean(txt):
    return html_lib.escape(str(txt)).replace('\\n','<br/>').replace('/n','<br/>').replace('\n','<br/>')

def filt(df,comp,btu,sys_type,conn,fuel,flue,coil,fillopt,boiler_manufacturer=None,air_sep_manufacturer=None,mix_mfr=None,mix_size=None,mix_type=None,draft_hood_style=None):
    f=df[df.component==comp].copy()
    if comp=='Expansion Tank': f=f[f.system_type==sys_type]
    if comp=='Pump Isolation Flanges': f=f[f.connection_type==conn]
    if comp=='Boiler':
        if boiler_manufacturer: f=f[f.manufacturer==boiler_manufacturer]
        f=f[f.fuel_type==fuel]
        if fuel=='Natural Gas' and draft_hood_style:
            f=f[f.draft_hood_style==draft_hood_style]
        if fuel=='Oil': f=f[(f.flue_type==flue)&(f.tankless_coil==coil)]
    if comp=='Air Separator':
        if air_sep_manufacturer: f=f[f.manufacturer==air_sep_manufacturer]
    if comp=='Mixing Valve':
        if mix_mfr: f=f[f.manufacturer==mix_mfr]
        if mix_size: f=f[f.pipe_size==mix_size]
        if mix_type: f=f[f.connection_type==mix_type]
    if comp==FILL: f=f[f.selection_option==fillopt]
    f=f[(f.min_btu<=btu)&(f.max_btu>=btu)].copy()
    return f.sort_values(['min_btu','max_btu'],ascending=[False,True])

df=pd.read_csv(DB)
# Normalize text fields to prevent hidden whitespace from breaking exact-match filters.
df.columns=df.columns.str.strip()
for _col in ['component','manufacturer','system_type','connection_type','fuel_type','flue_type','tankless_coil','selection_option','pipe_size']:
    if _col in df.columns:
        df[_col]=df[_col].astype(str).str.strip()
st.title('THE BOILER WIZARD')
st.caption('A Mystical, Magical, Hot Water Hydronic equipment selection application for residential applications')
st.caption('Scroll down for selections')


with st.sidebar:
    if BANNER_GIF.exists():
        st.image(str(BANNER_GIF), use_container_width=True)
    else:
        st.error('Missing boiler_wizard_shimmer.gif')
    st.header('System Inputs')
    btu=st.number_input('BTU Capacity / Boiler Output BTU',0,5000000,120000,5000)
    boiler_manufacturer=st.selectbox('Boiler Manufacturer',sorted([x for x in df[df.component=='Boiler'].manufacturer.dropna().unique() if x!='N/A']),key='boiler_manufacturer_selector')
    fuel=st.selectbox('Boiler Fuel Type',['Natural Gas','Oil'])
    flue='N/A'; coil='N/A'; draft_hood_style=None
    if fuel=='Oil':
        flue=st.selectbox('Boiler Flue Type',['Top Flue','Rear Flue'])
        coil=st.selectbox('Tankless Coil',['Without Tankless Coil','With Tankless Coil'])
    if fuel=='Natural Gas':
        gas_df = df[(df.component=='Boiler') & (df.fuel_type=='Natural Gas') & (df.manufacturer==boiler_manufacturer)]
        if 'draft_hood_style' in gas_df.columns:
            options = sorted(gas_df.draft_hood_style.dropna().unique())
        else:
            options = ['Low-profile','Standard Draft Hood']
        if len(options)==1:
            draft_hood_style = options[0]
            st.selectbox('Boiler Draft Hood Style', options, index=0, disabled=True)
        else:
            draft_hood_style = st.selectbox('Boiler Draft Hood Style', options)

    air_sep_manufacturer=st.selectbox('Air Separator Manufacturer',sorted([x for x in df[df.component=='Air Separator'].manufacturer.dropna().unique() if x!='N/A']),key='air_separator_manufacturer_selector')
    fillopt=st.selectbox('Fill Valve / Backflow Preventer',sorted([x for x in df[df.component==FILL].selection_option.dropna().unique() if x!='N/A']))
    sys_type=st.selectbox('Expansion Tank System Type',sorted([x for x in df[df.component=='Expansion Tank'].system_type.dropna().unique() if x!='Any']))
    conn=st.selectbox('Pump Isolation Flange Connection Type',['Press','Sweat','Threaded'])
    mixing_valve_manufacturer=None
    mixing_valve_connection_size=None
    mixing_valve_connection_type=None

    if coil=='With Tankless Coil':
        st.subheader('DHW Mixing Valve')
        _mv=df[df.component=='Mixing Valve'].copy()
        if _mv.empty:
            st.warning('No Mixing Valve rows found in hydronic_parts_database.csv')
        else:
            mixing_valve_manufacturer=st.selectbox('Mixing Valve Manufacturer',sorted(_mv.manufacturer.dropna().unique()),key='mixing_valve_manufacturer_selector')
            _mv=_mv[_mv.manufacturer==mixing_valve_manufacturer]
            mixing_valve_connection_size=st.selectbox('Mixing Valve Connection Size',sorted(_mv.pipe_size.dropna().unique()),key='mixing_valve_connection_size_selector')
            _mv=_mv[_mv.pipe_size==mixing_valve_connection_size]
            mixing_valve_connection_type=st.selectbox('Mixing Valve Connection Type',sorted(_mv.connection_type.dropna().unique()),key='mixing_valve_connection_type_selector')

    visible_order=[c for c in ORDER if not (c=='Mixing Valve' and coil!='With Tankless Coil')]
    hi=st.selectbox('Highlighted Component',visible_order,key='highlighted_component_selector')

rows=[]
for comp in visible_order:
    m=filt(df,comp,int(btu),sys_type,conn,fuel,flue,coil,fillopt,boiler_manufacturer,air_sep_manufacturer,mixing_valve_manufacturer,mixing_valve_connection_size,mixing_valve_connection_type,draft_hood_style)
    if m.empty:
        rows.append({'Component':comp,'Qty':'','Manufacturer':'','Model #':'No match','Part #':'No match','Pipe Size':'N/A','BTU Range':'No matching range','Description':'Add a matching rule.'})
    else:
        r=m.iloc[0]
        rows.append({'Component':r.component,'Qty':int(r.quantity),'Manufacturer':r.manufacturer,'Model #':r.model_number,'Part #':r.part_number,'Pipe Size':r.pipe_size,'BTU Range':f'{int(r.min_btu):,} - {int(r.max_btu):,} BTU','Description':r.description})
if any(x['Component']=='Expansion Tank' and x['Model #'] in PSHT for x in rows):
    rows.append({'Component':'Expansion Tank Service Valve','Qty':1,'Manufacturer':'Webstone','Model #':'WH41672','Part #':'WH41672','Pipe Size':'1/2"','BTU Range':'N/A','Description':'Automatically included with PSHT expansion tank selection.'})
sel=pd.DataFrame(rows)

m=filt(df,hi,int(btu),sys_type,conn,fuel,flue,coil,fillopt,boiler_manufacturer,air_sep_manufacturer,mixing_valve_manufacturer,mixing_valve_connection_size,mixing_valve_connection_type,draft_hood_style)
if m.empty:
    title=hi.upper(); body=f'NO MATCH\\n{int(btu):,} BTU'
else:
    r=m.iloc[0]
    if hi==FILL:
        title='PRESSURE REDUCING VALVE'; body=f'{r.selection_option}\\n{r.manufacturer}\\nQTY {int(r.quantity)}\\n{r.model_number}\\n{r.pipe_size} CONNECTION'
    elif hi=='Expansion Tank':
        svc='\\n+ [1] WH41672 SERVICE VALVE' if r.model_number in PSHT else ''
        title='EXPANSION TANK'; body=f'{r.manufacturer}\\n{r.model_number}\\n{r.system_type}\\n{r.pipe_size} CONNECTION{svc}'
    elif hi=='Pump Isolation Flanges':
        title='PUMP ISOLATION FLANGES'; body=f'QTY {int(r.quantity)}\\n{r.manufacturer} {r.model_number}\\n{r.connection_type} / {r.pipe_size} PIPE'
    elif hi=='Boiler':
        title='BOILER'; body=f'{r.manufacturer}\\n{r.model_number}\\n{r.fuel_type} / {r.input_mbh} MBH IN\\n{int(r.min_btu):,}-{int(r.max_btu):,} BTU OUT'
    else:
        title='AIR SEPARATOR'; body=f'{r.manufacturer} {r.model_number}\\n{r.pipe_size} PIPE'

left,right=st.columns([1.65,1])
play_game = st.button(
    "🧙‍♂️ Enter the Boiler Wizard Adventure",
    key="play_game_button"
)

with left:
    if not DIAGRAM_GIF.exists():
        st.warning('Diagram GIF is missing. Keep hot_water_hydronic_system_selector_demo.gif in this folder.')
    else:
        p=POS[hi]; gif=img64(DIAGRAM_GIF); th=clean(title); bh=clean(body)
        html=f'''<style>.diagram-wrap{{background:#000;border:1px solid #00cc44;box-shadow:0 0 12px rgba(57,255,85,.35)}}.diagram-svg{{display:block;width:100%;height:auto}}.pulse{{fill:none;stroke:#39ff55;stroke-width:3;animation:pulse 1.1s infinite}}@keyframes pulse{{0%{{opacity:.45;stroke-width:2}}50%{{opacity:1;stroke-width:5}}100%{{opacity:.45;stroke-width:2}}}}.callout{{color:#39ff55;background:rgba(0,0,0,.84);border:1px solid #39ff55;padding:8px 11px;font-family:Courier New,monospace;font-size:15px}}</style><div class='diagram-wrap'><svg class='diagram-svg' viewBox='0 0 {IMG_W} {IMG_H}'><image href='data:image/gif;base64,{gif}' x='0' y='0' width='{IMG_W}' height='{IMG_H}'/><circle class='pulse' cx='{p['cx']}' cy='{p['cy']}' r='{p['r']}'/><foreignObject x='{p['callout_x']}' y='{p['callout_y']}' width='390' height='230'><div xmlns='http://www.w3.org/1999/xhtml' class='callout'><b>{th}</b><br/>{bh}<br/><span>&gt; SELECTED BY INPUTS</span></div></foreignObject></svg></div>'''
        if play_game:
    components.html(
        '''
<html>
<body style="margin:0;background:black;">
<canvas id="game" width="980" height="500"></canvas>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const AudioCtx = new (window.AudioContext || window.webkitAudioContext)();
function beep(f,d){
  const o=AudioCtx.createOscillator();
  const g=AudioCtx.createGain();
  o.frequency.value=f;
  o.connect(g);
  g.connect(AudioCtx.destination);
  o.start();
  g.gain.exponentialRampToValueAtTime(0.0001,AudioCtx.currentTime+d);
  o.stop(AudioCtx.currentTime+d);
}

let wizard={x:80,y:380,vy:0};
let gravity=0.7;
let frame=0;
let trail=[];
let obstacles=[];
let speed=6;
let score=0;
let gameOver=false;
let explosion=[];

function spawn(){
  let t=Math.random()>0.5?"fire":"water";
  obstacles.push({x:980,y:400,w:35,h:40,type:t});
}

function update(){
  if(gameOver){
    explosion.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.life--;});
    return;
  }

  score++;
  frame++;

  if(score%90===0)spawn();

  wizard.vy+=gravity;
  wizard.y+=wizard.vy;

  if(wizard.y>380){wizard.y=380;wizard.vy=0;}

  if(wizard.y<380){
    trail.push({x:wizard.x,y:wizard.y,life:20});
  }

  trail=trail.filter(t=>--t.life>0);

  obstacles.forEach(o=>o.x-=speed);

  for(let o of obstacles){
    let hitX=wizard.x<o.x+o.w && wizard.x+25>o.x;
    let onGround=wizard.y>360;

    if(hitX && onGround){
      for(let i=0;i<25;i++){
        explosion.push({
          x:wizard.x,
          y:wizard.y,
          vx:(Math.random()-0.5)*6,
          vy:(Math.random()-0.5)*6,
          life:20
        });
      }
      beep(120,0.2);
      gameOver=true;
    }
  }
}

function draw(){
  ctx.fillStyle="black";
  ctx.fillRect(0,0,980,500);

  trail.forEach(t=>{
    ctx.fillStyle="rgba(0,255,0,"+(t.life/20)+")";
    ctx.fillRect(t.x,t.y,12,4);
  });

  let cloak=(frame%20<10)?0:3;

  ctx.fillStyle="#00FF00";
  ctx.fillRect(wizard.x,wizard.y,20,20);
  ctx.fillRect(wizard.x-cloak,wizard.y+10,cloak,10);

  ctx.beginPath();
  ctx.moveTo(wizard.x,wizard.y);
  ctx.lineTo(wizard.x+10,wizard.y-10);
  ctx.lineTo(wizard.x+20,wizard.y);
  ctx.fill();

  ctx.fillRect(wizard.x+22,wizard.y,3,18);

  obstacles.forEach(o=>{
    ctx.fillStyle=(o.type==="fire")?"orange":"cyan";
    ctx.fillRect(o.x,o.y,o.w,o.h);
  });

  explosion.forEach(p=>{
    ctx.fillStyle="orange";
    ctx.fillRect(p.x,p.y,3,3);
  });

  ctx.fillStyle="#00FF00";
  ctx.font="18px monospace";
  ctx.fillText("BTU's Accumulated: "+score,20,30);
  ctx.fillText("PRESS SPACE TO JUMP",650,30);

  if(gameOver){
    ctx.font="36px monospace";
    ctx.fillText("SYSTEM FAILURE",320,200);
    ctx.font="18px monospace";
    ctx.fillText("Press R to Restart",360,240);
  }
}

function loop(){
  update();
  draw();
  requestAnimationFrame(loop);
}

document.addEventListener("keydown",e=>{
  if(e.code==="Space" && wizard.y>=380){
    wizard.vy=-14;
    beep(400,0.1);
  }
  if(e.code==="KeyR"){location.reload();}
});

loop();
</script>
</body>
</html>
        ''',
        height=520
    )
else:
    components.html(html, height=625, scrolling=False)
``
with right:
    st.subheader('Highlighted Selection')
    st.dataframe(sel[sel.Component==hi],use_container_width=True,hide_index=True)

st.subheader('Selected Equipment Breakdown')
st.dataframe(sel,use_container_width=True,hide_index=True)
st.download_button('Download Selected Equipment Breakdown',data=sel.to_csv(index=False),file_name='selected_equipment_breakdown.csv',mime='text/csv')
st.subheader('Available Ranges for Highlighted Component')
st.dataframe(df[df.component==hi],use_container_width=True,hide_index=True)
