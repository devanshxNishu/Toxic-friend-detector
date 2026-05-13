from flask import Flask, request, render_template_string
import re
import os

app = Flask(__name__)

healthy = """
Aman: Bro proud of you
Rahul: Thanks bhai ❤️
Aman: Always there for you
Rahul: Lucky to have you
"""

toxic = """
Rohit: Tu pagal hai
Vikas: Kya hua
Rohit: Useless banda
Vikas: Sorry bhai
"""

dry = """
Aman: Kal aa raha?
Raj: Hmm
Aman: Match khelenge?
Raj: Dekhte
"""

need = """
Karan: Assignment bhej
Aryan: Hello?
Karan: PDF bhejna
Aryan: 🙂
"""

def analyze(chat):

    text = chat.lower()

    toxic_words = ["pagal","useless","hate","idiot","gadha"]
    positive_words = ["proud","thanks","bhai","love","support"]
    dry_words = ["hmm","ok","dekhte","haan"]
    need_words = ["assignment","pdf","notes","bhej","attendance"]

    toxic = 0
    positive = 0
    dry = 0
    need = 0

    for i in toxic_words:
        toxic += len(re.findall(i,text))

    for i in positive_words:
        positive += len(re.findall(i,text))

    for i in dry_words:
        dry += len(re.findall(i,text))

    for i in need_words:
        need += len(re.findall(i,text))

    toxicity = min(toxic * 20,100)
    friendship = min(positive * 20,100)
    dryness = min(dry * 20,100)
    neediness = min(need * 20,100)
    positivity = min((positive * 15) + 20,100)

    result = "Balanced Friendship 🙂"

    if toxicity > 60:
        result = "Extreme Toxic Friend ☠️"

    elif neediness > 60:
        result = "Need-Based Friendship 📚"

    elif dryness > 60:
        result = "Dry Friendship 🥶"

    elif friendship > 60:
        result = "Healthy Friendship ✅"

    advice = []

    if neediness > 50:
        advice.append("📚 Friend appears only during assignment season")

    if dryness > 50:
        advice.append("📶 Communication weaker than hostel WiFi")

    if toxicity > 50:
        advice.append("☠️ Friendship survival chances critical")

    if friendship > 50:
        advice.append("❤️ Good supportive friendship detected")

    if not advice:
        advice.append("🙂 Friendship looks normal")

    return {
        "result": result,
        "toxicity": toxicity,
        "friendship": friendship,
        "dryness": dryness,
        "neediness": neediness,
        "positivity": positivity,
        "advice": advice
    }

@app.route("/",methods=["GET","POST"])
def home():

    output = None
    chat = ""

    if request.method == "POST":
        chat = request.form.get("chat")

        if chat.strip():
            output = analyze(chat)

    page = """

<!DOCTYPE html>
<html>
<head>

<title>Toxic Friend Detector</title>

<style>

body{
background:#111827;
font-family:Arial;
color:white;
padding:20px;
}

.container{
max-width:900px;
margin:auto;
}

.card{
background:#1f2937;
padding:20px;
border-radius:12px;
margin-top:20px;
}

textarea{
width:100%;
height:250px;
background:#111827;
color:white;
border:1px solid gray;
padding:10px;
border-radius:10px;
}

button{
padding:10px 18px;
border:none;
border-radius:8px;
margin:5px;
cursor:pointer;
}

.analyze{
background:#2563eb;
color:white;
}

.clear{
background:#dc2626;
color:white;
}

.sample{
background:#374151;
color:white;
}

.bar{
height:20px;
background:#374151;
border-radius:20px;
overflow:hidden;
margin-bottom:15px;
}

.fill{
height:100%;
text-align:center;
line-height:20px;
}

.red{background:red;}
.green{background:green;}
.yellow{background:orange;}
.blue{background:blue;}
.pink{background:deeppink;}

</style>

</head>

<body>

<div class="container">

<h1>☠️ Toxic Friend Detector</h1>

<div class="card">

<form method="POST">

<textarea id="chat" name="chat">{{chat}}</textarea>

<br><br>

<button class="sample" type="button" onclick="healthyChat()">Healthy Chat</button>

<button class="sample" type="button" onclick="toxicChat()">Toxic Chat</button>

<button class="sample" type="button" onclick="dryChat()">Dry Chat</button>

<button class="sample" type="button" onclick="needChat()">Need Chat</button>

<br><br>

<button class="analyze" type="submit">Analyze</button>

<button class="clear" type="button" onclick="clearBox()">Clear</button>

</form>

</div>

{% if output %}

<div class="card">

<h2>{{output.result}}</h2>

<p>☠️ Toxicity Score</p>
<div class="bar">
<div class="fill red" style="width:{{output.toxicity}}%">
{{output.toxicity}}%
</div>
</div>

<p>❤️ Friendship Score</p>
<div class="bar">
<div class="fill green" style="width:{{output.friendship}}%">
{{output.friendship}}%
</div>
</div>

<p>🥶 Dryness Score</p>
<div class="bar">
<div class="fill yellow" style="width:{{output.dryness}}%">
{{output.dryness}}%
</div>
</div>

<p>📚 Neediness Score</p>
<div class="bar">
<div class="fill blue" style="width:{{output.neediness}}%">
{{output.neediness}}%
</div>
</div>

<p>😊 Positivity Score</p>
<div class="bar">
<div class="fill pink" style="width:{{output.positivity}}%">
{{output.positivity}}%
</div>
</div>

<h3>Funny AI Advice</h3>

<ul>
{% for i in output.advice %}
<li>{{i}}</li>
{% endfor %}
</ul>

</div>

{% endif %}

</div>

<script>

function healthyChat(){
document.getElementById("chat").value = `""" + healthy + """`;
}

function toxicChat(){
document.getElementById("chat").value = `""" + toxic + """`;
}

function dryChat(){
document.getElementById("chat").value = `""" + dry + """`;
}

function needChat(){
document.getElementById("chat").value = `""" + need + """`;
}

function clearBox(){
document.getElementById("chat").value = "";
}

</script>

</body>
</html>

"""

    return render_template_string(page,output=output,chat=chat)

if __name__ == "__main__":

    port = int(os.environ.get("PORT",5000))

    app.run(host="0.0.0.0",port=port)
