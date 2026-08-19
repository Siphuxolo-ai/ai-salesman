from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head><title>SA Auto + Solar AI Closer - National</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0f0f0f;color:white;font-family:Arial;display:flex;justify-content:center;padding:20px}
.box{width:100%;max-width:430px;background:#1e1e1e;border-radius:15px;padding:15px;border:1px solid #333}
.msg{background:#2d2d2d;padding:10px;border-radius:10px;margin:8px 0;line-height:1.4}
.you{color:#a0ff9e;text-align:right;background:#1a3a1a}
input{width:65%;padding:12px;border-radius:8px;border:none;background:#333;color:white}
button{background:#25D366;color:white;padding:12px 15px;border:none;border-radius:8px;font-weight:bold;cursor:pointer}
a.wa{background:#25D366;display:block;text-align:center;padding:14px;color:white;text-decoration:none;border-radius:8px;margin-top:12px;font-weight:bold;font-size:15px}
small{color:#888}
.badge{background:#25D366;color:black;padding:2px 8px;border-radius:10px;font-size:10px}
</style>
</head>
<body>
<div class="box">
<h3>🇿🇦 SA Auto & Solar AI <span class="badge">LIVE 24/7</span><br><small style="color:#25D366">We close for you - Nationwide</small></h3>
<div id="chat">
<div class="msg">Molo! 👋 I'm your AI Closer.<br><br>🚗 Looking for a car? Tell me: Brand, budget? (Toyota, VW, Ford, BMW, Suzuki etc)<br><br>☀️ Solar? Tell me your Eskom bill - I work for WHOLE SA!</div>
</div>
<div style="display:flex;gap:5px;margin-top:15px">
<input id="inp" placeholder="Type: Ranger R500k or Solar bill R3000...">
<button onclick="send()">Send</button>
</div>
<div id="lead" style="display:none">
<a class="wa" id="walink" target="_blank">✅ CONFIRM ON WHATSAPP: 0689249795</a>
<p style="font-size:11px;text-align:center;color:#aaa">Lead locked! We book Tue 10am / Thu 2pm - National delivery</p>
</div>
</div>
<script>
let step=0; let context=""; let bill="2500";
function add(t,c){let d=document.createElement('div');d.className='msg '+c;d.innerText=t;document.getElementById('chat').appendChild(d);window.scrollTo(0,document.body.scrollHeight)}
function send(){
 let v=document.getElementById('inp').value; if(!v)return;
 add("You: "+v,"you"); document.getElementById('inp').value="";
 fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:v,step:step,context:context,bill:bill})})
 .then(r=>r.json()).then(data=>{add(data.reply,""); step=data.next_step; context=data.context; bill=data.bill;
 if(data.show_wa){document.getElementById('lead').style.display='block';
 document.getElementById('walink').href="https://wa.me/27689249795?text=NEW%20LEAD:%20"+encodeURIComponent(data.wa_text); }});
}
</script>
</body>
</html>
"""

# ALL SA CAR BRANDS DATABASE
CARS_DB = {
 "ranger": "Ford Ranger from R350k - 4x2, 4x4, Wildtrak, Raptor available. What budget?",
 "hilux": "Toyota Hilux from R380k - Legendary, low fuel, best resale! Budget?",
 "corolla": "Corolla Cross / Corolla from R300k - Hybrid available!",
 "polo": "VW Polo from R250k, Polo Vivo from R180k - Most popular in SA!",
 "swift": "Suzuki Swift from R200k - Best budget car, low fuel!",
 "bmw": "BMW 1,2,3 Series from R400k - We have finance for blacklisted too (with deposit)",
 "toyota": "Toyota - Hilux, Corolla, Fortuner, Starlet - Which model you want? Budget?",
 "ford": "Ford - Ranger, Everest, EcoSport - Which one?",
 "vw": "VW - Polo, Golf, T-Cross, Amarok - Which model?",
 "suzuki": "Suzuki - Swift, Baleno, Jimny, Ertiga - Budget?",
}

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    d = request.json
    msg = d.get("message","").lower()
    step = d.get("step",0)
    ctx = d.get("context","")
    bill = d.get("bill","2500")
    
    # SOLAR DETECTION - NATIONWIDE
    if any(x in msg for x in ["bill", "eskom", "solar", "loadshedding", "inverter", "r2", "r3", "r4", "r1"]) or re.search(r'\b[1-9]\d{3}\b', msg):
        m=re.search(r'(\d{3,5})',msg)
        if m: bill=m.group(1)
        if int(bill) >= 800:
            return jsonify(reply=f"Sharp! R{bill} bill qualifies for solar ANYWHERE in SA! 🇿🇦\n\nWe install in JHB, CPT, DBN, EL, PE - all provinces.\n\nOwn house or renting? And city? I book free assessment Tue 10am / Thu 2pm.", next_step=10, context="solar", bill=bill, wa_text=f"Solar Lead - Bill R{bill} - {msg}")
        else:
            return jsonify(reply=f"R{bill} is low for full solar, but we have backup kit from R18k (runs fridge, TV, WiFi) - Nationwide install. City?", next_step=10, context="solar", bill=bill, wa_text=f"Small Solar Lead - R{bill}")

    # CAR DETECTION - ALL BRANDS
    if any(x in msg for x in ["car", "bakkie", "ranger", "hilux", "polo", "budget", "finance", "suzuki", "toyota", "bmw", "vw", "ford", "buy"]) or step==20:
        for brand, reply in CARS_DB.items():
            if brand in msg:
                return jsonify(reply=reply+" Finance available - deposit? And city? We deliver nationwide!", next_step=20, context="car", bill=bill, wa_text=f"Car Lead - {brand.upper()} - {msg}")
        return jsonify(reply="We sell ALL cars in SA! 🚗\nToyota, VW, Ford, Suzuki, BMW, Nissan, Hyundai etc\n\nTell me brand + budget? Eg: Polo R200k or Ranger R500k. We finance + deliver nationwide!", next_step=20, context="car", bill=bill, wa_text=f"Car Lead General - {msg}")

    if step==10: # solar followup
        return jsonify(reply=f"Perfect! Name + WhatsApp to confirm? We cover your area {msg} - Our team comes with assessment. Eg: Mike 0689249795", next_step=11, context="solar", bill=bill, wa_text=f"Solar Lead - City {msg} - Bill R{bill}")
    if step==11:
        return jsonify(reply=f"✅ BOOKED! Address for team? National install team will come Tue 10am. Click WhatsApp below to confirm now!", next_step=12, context="solar", bill=bill, show_wa=True, wa_text=f"SOLAR BOOKED - Bill R{bill} - Details: {msg} - Call NOW 0689249795", slot="Tue 10am")

    if step==20: # car followup
        return jsonify(reply="Nice! What's your name + WhatsApp? I lock that car for you. Eg: Mike 0689249795 - City?", next_step=21, context="car", bill=bill, wa_text=f"Car Lead - Details {msg}")
    if step==21:
        return jsonify(reply="✅ LEAD LOCKED! What city for delivery? We do finance check now. Click WhatsApp below!", next_step=22, context="car", bill=bill, show_wa=True, wa_text=f"CAR BOOKED - {msg} - CALL NOW 0689249795", slot="Tue 10am")

    return jsonify(reply="I handle 2 things for WHOLE SA: 🚗 ALL cars (Toyota, VW, Ford, Suzuki, BMW) and ☀️ Solar for any bill! What you need?", next_step=0, context="", bill=bill)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
