import base64
import html as html_lib
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='The Boiler Wizard', layout='wide')

DB = Path('hydronic_parts_database.csv')
df = pd.read_csv(DB)
df.columns = df.columns.str.strip()

# --- Helpers ---
def img64(path):
    return base64.b64encode(path.read_bytes()).decode("utf-8")

def clean(txt):
    return html_lib.escape(str(txt))

# --- UI ---
st.title("THE BOILER WIZARD")
st.caption("Hydronic equipment selector")

btu = st.number_input("BTU", 0, 5000000, 120000)
boiler_manufacturer = st.selectbox("Boiler Manufacturer",
    sorted(df[df.component == 'Boiler'].manufacturer.dropna().unique())
)

fuel = st.selectbox("Fuel", ["Natural Gas", "Oil"])

DIAGRAM_GIF = Path("hot_water_hydronic_system_selector_demo.gif")

# --- Layout ---
left, right = st.columns([2,1])

# ✅ SINGLE BUTTON (with key)
play_game = st.button(
    "🧙‍♂️ Enter the Boiler Wizard Adventure",
    key="play_game_button"
)

with left:
    if play_game:
        components.html('''
<html>
<body style="margin:0;background:black;">
<canvas id="game" width="980" height="500"></canvas>
<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

// AUDIO
const AudioCtx = new (window.AudioContext || window.webkitAudioContext)();
function beep(f,d){
  const o=AudioCtx.createOscillator();
  const g=AudioCtx.createGain();
  o.frequency.value=f;
  o.connect(g); g.connect(AudioCtx.destination);
  o.start();
  g.gain.exponentialRampToValueAtTime(0.0001,AudioCtx.currentTime+d);
  o.stop(AudioCtx.currentTime+d);
}

// PLAYER
let wizard={x:80,y:380,vy:0};
let gravity=0.7;
let frame=0;

// FX
let trail=[];
let explosion=[];

// GAME
let obstacles=[];
let speed=6;
let score=0;
let gameOver=false;

function spawn(){
  let type=Math.random()>0.5?"fire":"water";
  obstacles.push({x:980,y:400,w:35,h:40,type:type});
}

function update(){
  if(gameOver){
    explosion.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.life--;});
    return;
  }

  score++;
  frame++;

  if(score%90===0) spawn();

  wizard.vy+=gravity;
  wizard.y+=wizard.vy;

  if(wizard.y>380){wizard.y=380;wizard.vy=0;}

  if(wizard.y<380){
    trail.push({x:wizard.x,y:wizard.y,life:20});
  }

  trail = trail.filter(t=>--t.life>0);

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

  // trail
  trail.forEach(t=>{
    ctx.fillStyle="rgba(0,255,0,"+(t.life/20)+")";
    ctx.fillRect(t.x,t.y,12,4);
  });

  // wizard
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

  // obstacles
  obstacles.forEach(o=>{
    ctx.fillStyle=(o.type==="fire")?"orange":"cyan";
    ctx.fillRect(o.x,o.y,o.w,o.h);
  });

  // explosion
  explosion.forEach(p=>{
    ctx.fillStyle="orange";
    ctx.fillRect(p.x,p.y,3,3);
  });

  // UI
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
  if(e.code==="Space"){
    if(wizard.y>=380){
      wizard.vy=-14;
      beep(400,0.1);
    }
  }
  if(e.code==="KeyR"){location.reload();}
});

loop();
</script>
</body>
</html>
''', height=520)

    else:
        if not DIAGRAM_GIF.exists():
            st.warning("Diagram GIF missing")
        else:
            gif = img64(DIAGRAM_GIF)

            html = f"""
            <div style='background:black;border:1px solid #39ff55'>
                <img src='data:image/gif;base64,{gif}' width='100%'/>
            </div>
            """

            components.html(html, height=625)

# --- Right panel ---
with right:
    st.subheader("Selections (placeholder)")
    st.write("Your original selection UI remains unchanged here")
