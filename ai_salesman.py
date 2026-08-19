from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Add your Gemini key on Render later
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

PROMPTS = {
"solar": """
You are Thandi, elite solar sales qualifier for SunPower EC, East London & Gqeberha.
Goal: Qualify and book FREE site assessment. Be short, professional, friendly (English + a bit Xhosa).
Company: SunPower EC, installs 3kW-15kW systems R45k-R180k, 5yr warranty, covers all EC.
QUALIFYING FLOW:
1. Ask area first (check if EC)
2. Ask monthly Eskom bill? If below R800: "For bills under R800, solar payback is long. We have small backup from R18k - are you interested in backup or full solar?"
3. House or business? Own or rent? (Renters don't qualify)
4. Roof type: tile, IBR (zinc), flat?
5. Then book: "You qualify for free assessment. Our tech can come Tue 10am or Thu 2pm, which suits?"
Always collect Name + Number at end.
If qualified, output at end: [HOT LEAD] summary
""",
"car": """
You are Mike, car sales qualifier for EL Auto, Wilsonia East London.
Goal: Qualify buyer and book test drive. Short, no fluff.
Stock: 2021 Ford Ranger 2.2 XL 45k km R299k, 2020 Toyota Hilux 2.4 GD6 R345k, 2019 Polo TSI R189k.
FLOW:
1. Confirm car still available, give price/km
2. Budget? Trade-in? Cash or finance?
3. Blacklisted? License?
4. Book test drive: "We have slot tomorrow 10am or 3pm, which works? Bring license + 3 months bank statement"
Collect Name + Number.
Output [HOT LEAD] summary when qualified.
"""
}

HTML = """
<!DOCTYPE html>
<html><head><title>EC AutoSolar AI - Live Demo</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Inter,Arial;max-width:480px;margin:0 auto;background:#0a0a0a;color:white;padding:16px}
.card{background:#1a1a1a;border-radius:16px;padding:16px;margin-bottom:12px;border:1px solid #333}
.tabs{display:flex;gap:8px;margin-bottom:12px} .tab{flex:1;padding:12px;border-radius:10px;border:none;font-weight:bold;cursor:pointer}
.active{background:#00ff88;color:black} .inactive{background:#2a2a2a;color:white}
#chat{height:420px;overflow-y:auto;padding:10px;background:black;border-radius:12px}
.user{text-align:right;margin:8px;color:#00ff88} .ai{text-align:left;margin:8px;color:white;background:#222;padding:8px;border-radius:8px}
input{width:70%;padding:14px;border-radius:10px;border:none;background:#222;color:white} button{width:28%;padding:14px;border-radius:10px;border:none;background:#00ff88;font-weight:bold}
.lead{background:#00ff88;color:black;padding:8px;border-radius:8px;margin-top:8px;font-size:12px}
</style></head><body>
<div class="card"><h2>🚀 EC AutoSolar AI</h2><p>R10k+ Client Demo - Works 24/7</p>
<div class="tabs"><button id="tSolar" class="tab active" onclick="setType('solar')">☀️ Solar Bot</button>
<button id="tCar" class="tab inactive" onclick="setType('car')">🚗 Car Bot</button></div>
<p id="desc">Solar: Qualifies Eskom bill, books site visit</p></div>
<div class="card"><div id="chat"><div class="ai">Molo! I'm Thandi/Mike. Ask me about solar or that Ranger? I'll qualify and book you now.</div></div>
<div style="display:flex;gap:8px;margin-top:10px"><input id="msg" placeholder="Hi, saw your solar ad..." onkeypress="if(event.key==='Enter')send()">
<button onclick="send()">Send</button></div></div>
<div class="card"><h4>What owner gets on WhatsApp:</h4><div id="lead" class="lead">🔥 HOT LEAD will appear here after qualification</div></div>
<script>
let type='solar';
function setType(t){type=t;
 document.getElementById('tSolar').className=t=='solar'?'tab active':'tab inactive';
 document.getElementById('tCar').className=t=='car'?'tab active':'tab inactive';
 document.getElementById('desc').innerText=t=='solar'?'Solar: Qualifies Eskom bill, books site visit':'Car: Qualifies budget & books test drive';
 document.getElementById('chat').innerHTML='<div class=ai>Switched to '+(t=='solar'?'Solar Thandi':'Auto Mike')+'. How can I help?</div>';
}
async function send(){
 let m=document.getElementById('msg').value; if(!m) return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class=user>You: ${m}</div>`; document.getElementById('msg').value='';
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m,type:type})});
 let d=await r.json(); c.innerHTML+=`<div class=ai>${d.reply}</div>`;
 if(d.lead) document.getElementById('lead').innerText=d.lead; c.scrollTop=c.scrollHeight;
}
</script></body></html>
"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message","")
    bot_type = data.get("type","solar")
    prompt = PROMPTS.get(bot_type, PROMPTS["solar"])
    
    if not GEMINI_KEY:
        # Demo fallback without key - still shows it works
        if bot_type=="solar":
            reply = "Enkosi! What's your area in EC and monthly Eskom bill? (e.g. Mdantsane, R2500). I'll check if you qualify for free assessment."
            if "R" in msg and any(x in msg for x in ["2000","2500","3000","1500"]):
                reply = "Perfect, you qualify! Own house or renting? And roof type - tile or zinc? I can book Tue 10am or Thu 2pm for free assessment."
                lead = f"🔥 HOT SOLAR LEAD: Bill {msg}, Area EC, Wants site visit"
                return jsonify({"reply": reply, "lead": lead})
        else:
            reply = "Yes Ranger still available! R299k, 45k km. What's your budget and do you have trade-in? Cash or finance?"
            if "finance" in msg.lower() or "budget" in msg.lower():
                reply = "Sharp. Are you blacklisted? License valid? I can book test drive tomorrow 10am Wilsonia - what is your name?"
                lead = "🔥 HOT CAR LEAD: Ranger interest, needs finance, test drive"
                return jsonify({"reply": reply, "lead": lead})
        return jsonify({"reply": reply, "lead": ""})

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"{prompt}\n\nCustomer says: {msg}\n\nReply short:")
        text = response.text
        lead = ""
        if "[HOT LEAD]" in text or "HOT LEAD" in text:
            lead = text.split("[HOT LEAD]")[-1][:200]
        return jsonify({"reply": text, "lead": lead or "Qualified lead captured - check chat"})
    except Exception as e:
        return jsonify({"reply": "I'm here 24/7! Tell me your area and Eskom bill (solar) or which car you want (car). I'll book you now.", "lead": ""})

@app.route("/health")
def health(): return "OK - Bot running 24/7"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
