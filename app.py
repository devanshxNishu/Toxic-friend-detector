# ============================================================
# TOXIC FRIEND DETECTOR - app.py
# A fun NLP-based chat analyzer for college mini-projects
# Tech Stack: Flask + Regex + Rule-based NLP + Embedded HTML/CSS/JS
# ============================================================

import os
import re
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ============================================================
# SAMPLE CHATS - Realistic WhatsApp-style conversations
# ============================================================

SAMPLE_CHATS = {
    "healthy": """Alex: Hey! How are you doing? Been a while 😊
Sam: I'm good! Yeah, missed talking to you. How's your family?
Alex: All good! Hey I wanted to tell you, I got selected for the internship!!
Sam: OMG WHAT! That's amazing!! I'm so proud of you!! 🎉🎉
Alex: Haha thank you!! Couldn't have done it without your support during prep
Sam: Stop it, you did all the hard work. Let's celebrate this weekend?
Alex: YES! Also tell me about your project, how's it going?
Sam: It's going well! Actually wanted your opinion on something
Alex: Of course! Anything for you. Send it over
Sam: You're the best honestly 💙
Alex: Right back at you! Real ones fr""",

    "toxic": """Raj: aye where were you yesterday? I called 10 times
Priya: Sorry I was busy with family
Raj: busy with family lol okay wow thanks
Priya: What happened?
Raj: nothing forget it you clearly don't care
Priya: Don't be like that I was genuinely busy
Raj: you're always busy when it comes to ME
Priya: That's not true at all
Raj: whatever you always take others side
Priya: I didn't take anyone's side??
Raj: you know what I'm done explaining myself to you
Priya: Raj please talk to me
Raj: leave me alone I hate you
Priya: Why are you doing this
Raj: because you make me feel like trash every day""",

    "dry": """Neha: Hey!
Rohan: hi
Neha: How are you?
Rohan: fine
Neha: What did you do today?
Rohan: nothing much
Neha: Oh okay. Did you watch that show I recommended?
Rohan: no
Neha: Okay... Want to hang out this weekend?
Rohan: maybe
Neha: Should I plan something?
Rohan: idk
Neha: Okay lol. Talk later I guess
Rohan: ok
Neha: 😐
Rohan: k""",

    "need_based": """Ankit: hey bro
Dev: hi
Ankit: bro notes bhej plz today's lecture
Dev: ok
Ankit: and assignment bhi bhej bro deadline kal hai
Dev: dude mujhe bhi nahi pata tha
Ankit: arre yaar help karo na plz plz
Dev: okay bhejta hu
Ankit: ty bro best friend tu
Dev: 😐
Ankit: bro pdf bhi chahiye chapter 4 ki
Dev: ...okay
Ankit: aur bro practical file ready hai tera?
Dev: haan
Ankit: bhejna plz kal submit karna hai
Dev: bhai tu kuch khud bhi kar
Ankit: haha bro you're the smartest I trust only you
Dev: 🙄
Ankit: bro ek kaam aur tha...
Dev: kya
Ankit: presentation bana de please bro last time
Dev: this is the 5th last time
Ankit: bro pakka last time I promise bro luv you
Dev: okay fine sending"""
}

# ============================================================
# ANALYSIS ENGINE - Rule-based NLP with Regex
# ============================================================

# --- Toxic Word/Phrase Keywords ---
TOXIC_KEYWORDS = [
    r'\bhate\b', r'\bstupid\b', r'\bidiot\b', r'\bloser\b', r'\bworthless\b',
    r'\bfake\b', r'\blie\b', r'\blied\b', r'\bblame\b', r'\byour fault\b',
    r'\bdone with you\b', r'\bleave me alone\b', r'\bi hate you\b',
    r'\byou never\b', r'\byou always\b', r'\bnobody cares\b',
    r'\btu pagal hai\b', r'\bbekar hai\b', r'\bnikamma\b', r'\bchup kar\b',
    r'\bshut up\b', r'\bgo away\b', r'\bdon\'t talk\b', r'\bfeel like trash\b',
    r'\bmake me feel\b', r'\byou make me\b', r'\byou\'re the worst\b',
]

# --- Positive/Healthy Friendship Keywords ---
POSITIVE_KEYWORDS = [
    r'\bproud of you\b', r'\bso happy for you\b', r'\bcelebrate\b',
    r'\bmissed you\b', r'\bmiss you\b', r'\btake care\b', r'\blove you\b',
    r'\bthank you\b', r'\bthanks\b', r'\bappreciate\b', r'\bhere for you\b',
    r'\bhow are you\b', r'\bhow\'s your\b', r'\bcheck in\b', r'\bcouldn\'t have done\b',
    r'\bso proud\b', r'\byou\'re amazing\b', r'\byou\'re the best\b',
    r'\bbhai proud\b', r'\bkhayal rakhna\b', r'\bshukriya\b', r'\bbest friend\b',
    r'\breal one\b', r'\byou matter\b', r'\bbelieve in you\b',
]

# --- Need-Based / Assignment-Seeker Keywords ---
NEED_KEYWORDS = [
    r'\bnotes bhej\b', r'\bassignment bhej\b', r'\bpdf bhej\b', r'\bpdf bhejna\b',
    r'\bpdf de\b', r'\bnotes de\b', r'\bassignment de\b', r'\bpractical file\b',
    r'\bpresentation bana\b', r'\bhomework\b', r'\bsubmit\b', r'\bdeadline\b',
    r'\blast time\b', r'\bplease bro\b', r'\bplz plz\b', r'\bsend notes\b',
    r'\bsend assignment\b', r'\byaar help\b', r'\bhelp kar\b', r'\bbhej yaar\b',
    r'\bproject bana\b', r'\bkaro na\b', r'\bbhejna\b', r'\bnotes\b',
    r'\bassignment\b', r'\blecture\b', r'\bexam\b', r'\bsyllabus\b',
]

# --- Dry/One-Word Reply Patterns ---
DRY_PATTERNS = [
    r'^ok$', r'^okay$', r'^k$', r'^fine$', r'^hmm+$', r'^hm$',
    r'^no$', r'^yes$', r'^maybe$', r'^idk$', r'^lol$', r'^hi$',
    r'^hey$', r'^nothing much$', r'^busy$', r'^thik hai$', r'^haan$',
    r'^nahi$', r'^ha$', r'^na$', r'^ok\.$', r'^👍$', r'^😐$',
]

# --- Ghosting Indicators ---
GHOST_PATTERNS = [
    r'\bseen\b', r'\bleft on read\b', r'\bno reply\b',
    r'\bnot replying\b', r'\bignoring\b', r'\bignore\b',
    r'\bnever responds\b', r'\bdisappeared\b',
]

# --- Manipulative Language ---
MANIPULATIVE_KEYWORDS = [
    r'\byou never care\b', r'\bnobody loves me\b', r'\bfeel guilty\b',
    r'\bafter everything i did\b', r'\bforgetting me\b', r'\bdon\'t you care\b',
    r'\byou\'re doing this on purpose\b', r'\bi can\'t believe you\b',
    r'\byou always do this\b', r'\bwhy do you hate me\b',
]


def count_keyword_hits(text, patterns):
    """Count how many keyword patterns match in the text."""
    text_lower = text.lower()
    count = 0
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        count += len(matches)
    return count


def extract_messages(chat_text):
    """
    Extract individual messages from chat.
    Supports WhatsApp format: 'Name: message'
    """
    lines = chat_text.strip().split('\n')
    messages = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Match "Name: message" pattern
        match = re.match(r'^[^:]+:\s*(.+)$', line)
        if match:
            messages.append(match.group(1).strip())
        else:
            messages.append(line)
    return messages


def count_dry_replies(messages):
    """Count how many messages are one-word / dry replies."""
    dry_count = 0
    for msg in messages:
        msg_clean = msg.strip().lower()
        for pattern in DRY_PATTERNS:
            if re.fullmatch(pattern, msg_clean):
                dry_count += 1
                break
        # Also check very short messages (1-3 chars)
        if len(msg_clean) <= 3:
            dry_count += 1
    return dry_count


def analyze_message_length(messages):
    """Analyze average message length for effort detection."""
    if not messages:
        return 0
    lengths = [len(msg) for msg in messages]
    return sum(lengths) / len(lengths)


def analyze_chat(chat_text):
    """
    MAIN ANALYSIS FUNCTION
    Takes raw chat text and returns scores + verdict
    """
    if not chat_text or len(chat_text.strip()) < 10:
        return {"error": "Please enter a valid chat conversation."}

    messages = extract_messages(chat_text)
    total_messages = len(messages)

    if total_messages < 2:
        return {"error": "Need at least a few messages to analyze!"}

    # --- Count keyword hits ---
    toxic_hits = count_keyword_hits(chat_text, TOXIC_KEYWORDS)
    positive_hits = count_keyword_hits(chat_text, POSITIVE_KEYWORDS)
    need_hits = count_keyword_hits(chat_text, NEED_KEYWORDS)
    ghost_hits = count_keyword_hits(chat_text, GHOST_PATTERNS)
    manipulative_hits = count_keyword_hits(chat_text, MANIPULATIVE_KEYWORDS)

    # --- Dry reply analysis ---
    dry_count = count_dry_replies(messages)
    dry_ratio = dry_count / total_messages if total_messages > 0 else 0

    # --- Message effort level ---
    avg_length = analyze_message_length(messages)

    # ============================================================
    # SCORING LOGIC (0 - 100)
    # ============================================================

    # TOXICITY SCORE (higher = more toxic)
    toxicity_score = min(100, (toxic_hits * 12) + (manipulative_hits * 10) + (ghost_hits * 8))

    # POSITIVITY SCORE (higher = more positive)
    positivity_score = min(100, (positive_hits * 10) + (max(0, avg_length - 10) * 0.5))

    # DRYNESS SCORE (higher = more dry/boring)
    dryness_score = min(100, int(dry_ratio * 100) + (max(0, 20 - avg_length) * 2))

    # NEEDINESS SCORE (higher = more need-based)
    neediness_score = min(100, need_hits * 10)

    # FRIENDSHIP SCORE (overall health)
    friendship_score = max(0, min(100,
        50
        + (positive_hits * 5)
        - (toxic_hits * 8)
        - (manipulative_hits * 7)
        - int(dry_ratio * 30)
        - (need_hits * 3)
    ))

    # ============================================================
    # FINAL VERDICT LOGIC
    # ============================================================

    if toxicity_score >= 50 or manipulative_hits >= 3:
        if toxicity_score >= 70:
            verdict = "Extreme Toxic Friend ☠️"
            verdict_class = "extreme-toxic"
        else:
            verdict = "Slightly Toxic 😐"
            verdict_class = "toxic"
    elif neediness_score >= 40 and positive_hits < 3:
        verdict = "Need-Based Friendship 📚"
        verdict_class = "need-based"
    elif dryness_score >= 55 and avg_length < 15:
        verdict = "Dry Friendship 🌵"
        verdict_class = "dry"
    elif friendship_score >= 60 and positivity_score >= 30:
        verdict = "Healthy Friendship ✅"
        verdict_class = "healthy"
    elif friendship_score >= 40:
        verdict = "Average Friendship 🤷"
        verdict_class = "average"
    else:
        verdict = "Fake Friendship 🎭"
        verdict_class = "fake"

    # ============================================================
    # FUNNY AI ADVICE GENERATOR
    # ============================================================

    advice_lines = []

    if need_hits >= 4:
        advice_lines.append("🎓 Academic parasite behavior detected. Your friend surfaces only during exam season.")
    if need_hits >= 2:
        advice_lines.append("📚 This friend appears only during assignment season. Friendship or freelancing?")
    if dry_ratio >= 0.5:
        advice_lines.append("📡 Communication quality lower than hostel WiFi — and that's saying something.")
    if dry_ratio >= 0.3:
        advice_lines.append("💬 Conversation effort level: factory settings. Please update firmware.")
    if toxic_hits >= 4:
        advice_lines.append("☣️ Friendship survival chances: critical. Please contact your nearest therapist.")
    if toxic_hits >= 2:
        advice_lines.append("⚠️ Emotional stability of this friendship is shakier than a 10-year-old ceiling fan.")
    if manipulative_hits >= 2:
        advice_lines.append("🎭 Manipulation index elevated. This friend could win an Oscar for guilt-tripping.")
    if positivity_score >= 60:
        advice_lines.append("💚 This friendship is healthier than your diet. Keep it going!")
    if positivity_score >= 40:
        advice_lines.append("🌱 Genuine support detected. A rare species in today's world.")
    if avg_length < 8 and total_messages > 5:
        advice_lines.append("🧱 Responses shorter than your attention span. Red flag or just bad at texting?")
    if ghost_hits >= 2:
        advice_lines.append("👻 Ghost behavior detected. Friendship may have exited the chat permanently.")
    if friendship_score >= 70:
        advice_lines.append("🏆 This friendship passed the vibe check. Rare W unlocked.")

    # Default advice if nothing triggered
    if not advice_lines:
        advice_lines.append("🤖 Friendship status: Complicated. Like your relationship with deadlines.")

    # ============================================================
    # DETECTED BEHAVIORS (for display)
    # ============================================================

    behaviors = []
    if toxic_hits > 0:
        behaviors.append(f"🔴 Toxic language detected ({toxic_hits} instances)")
    if manipulative_hits > 0:
        behaviors.append(f"🟠 Manipulative phrases found ({manipulative_hits} instances)")
    if positive_hits > 0:
        behaviors.append(f"🟢 Positive/supportive language ({positive_hits} instances)")
    if need_hits > 0:
        behaviors.append(f"🟡 Need-based requests ({need_hits} instances)")
    if dry_count > 0:
        behaviors.append(f"🔵 Dry/one-word replies ({dry_count} out of {total_messages})")
    if ghost_hits > 0:
        behaviors.append(f"👻 Ghosting indicators ({ghost_hits} instances)")

    return {
        "verdict": verdict,
        "verdict_class": verdict_class,
        "scores": {
            "toxicity": toxicity_score,
            "friendship": friendship_score,
            "dryness": dryness_score,
            "neediness": neediness_score,
            "positivity": positivity_score,
        },
        "stats": {
            "total_messages": total_messages,
            "avg_length": round(avg_length, 1),
            "dry_replies": dry_count,
        },
        "behaviors": behaviors,
        "advice": advice_lines,
    }


# ============================================================
# HTML TEMPLATE - Fully embedded inside Python
# Dark theme, cards, progress bars, emojis
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Toxic Friend Detector 🔍</title>
<style>
  /* ---- RESET & BASE ---- */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0d0f14;
    --surface: #161b24;
    --card: #1e2533;
    --border: #2a3347;
    --accent: #7c3aed;
    --accent2: #06b6d4;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --green: #22c55e;
    --red: #ef4444;
    --yellow: #f59e0b;
    --orange: #f97316;
    --cyan: #06b6d4;
    --pink: #ec4899;
    --radius: 12px;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, sans-serif;
    min-height: 100vh;
    padding: 20px;
  }

  /* ---- HEADER ---- */
  .header {
    text-align: center;
    padding: 40px 20px 30px;
    position: relative;
  }

  .header-badge {
    display: inline-block;
    background: linear-gradient(135deg, #7c3aed22, #06b6d422);
    border: 1px solid #7c3aed55;
    color: var(--accent2);
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 99px;
    margin-bottom: 16px;
    font-weight: 600;
  }

  .header h1 {
    font-size: clamp(28px, 5vw, 52px);
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #06b6d4, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 10px;
  }

  .header p {
    color: var(--muted);
    font-size: 15px;
    max-width: 500px;
    margin: 0 auto;
  }

  /* ---- CONTAINER ---- */
  .container {
    max-width: 900px;
    margin: 0 auto;
  }

  /* ---- CARD ---- */
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 20px;
  }

  .card-title {
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--muted);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .card-title::before {
    content: '';
    display: block;
    width: 3px;
    height: 14px;
    background: var(--accent);
    border-radius: 99px;
  }

  /* ---- SAMPLE BUTTONS ---- */
  .sample-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 6px;
  }

  .btn {
    padding: 9px 18px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .btn:hover { transform: translateY(-1px); filter: brightness(1.15); }
  .btn:active { transform: translateY(0); }

  .btn-healthy { background: #15803d22; color: #4ade80; border: 1px solid #15803d55; }
  .btn-toxic   { background: #9f121222; color: #f87171; border: 1px solid #9f121255; }
  .btn-dry     { background: #78350f22; color: #fbbf24; border: 1px solid #78350f55; }
  .btn-need    { background: #1e3a5f22; color: #60a5fa; border: 1px solid #1e3a5f55; }
  .btn-analyze {
    background: linear-gradient(135deg, var(--accent), #06b6d4);
    color: white;
    padding: 12px 32px;
    font-size: 15px;
    width: 100%;
    margin-top: 4px;
    border-radius: 10px;
    letter-spacing: 0.5px;
  }
  .btn-clear {
    background: #1e2533;
    color: var(--muted);
    border: 1px solid var(--border);
    padding: 12px 20px;
    font-size: 14px;
    margin-top: 4px;
    border-radius: 10px;
  }

  /* ---- TEXTAREA ---- */
  textarea {
    width: 100%;
    min-height: 220px;
    background: #0d0f14;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.7;
    resize: vertical;
    transition: border-color 0.2s;
    outline: none;
  }

  textarea:focus { border-color: var(--accent); }
  textarea::placeholder { color: #4a5568; }

  .input-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }

  .input-row .btn-analyze { flex: 1; min-width: 200px; }
  .input-row .btn-clear { flex: 0; }

  /* ---- RESULTS ---- */
  #results { display: none; }

  /* ---- VERDICT BANNER ---- */
  .verdict-banner {
    text-align: center;
    padding: 32px 20px;
    border-radius: var(--radius);
    margin-bottom: 20px;
    border: 1px solid;
    position: relative;
    overflow: hidden;
  }

  .verdict-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0.06;
    background: radial-gradient(circle at 50% 0%, white, transparent 60%);
  }

  .verdict-banner .emoji { font-size: 52px; display: block; margin-bottom: 12px; }
  .verdict-banner .label {
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    opacity: 0.7;
    margin-bottom: 6px;
    font-weight: 600;
  }
  .verdict-banner .verdict-text {
    font-size: clamp(22px, 4vw, 36px);
    font-weight: 800;
    margin-bottom: 0;
  }

  .verdict-healthy  { background: #052e16; border-color: #16a34a; color: #4ade80; }
  .verdict-toxic    { background: #450a0a; border-color: #dc2626; color: #f87171; }
  .verdict-extreme-toxic { background: #3b0000; border-color: #7f1d1d; color: #fca5a5; }
  .verdict-dry      { background: #27170a; border-color: #d97706; color: #fbbf24; }
  .verdict-need-based { background: #0c1a2e; border-color: #2563eb; color: #93c5fd; }
  .verdict-average  { background: #1a1a2e; border-color: #7c3aed; color: #c4b5fd; }
  .verdict-fake     { background: #1a0a2e; border-color: #9d174d; color: #f9a8d4; }

  /* ---- SCORES GRID ---- */
  .scores-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  @media (max-width: 500px) { .scores-grid { grid-template-columns: 1fr; } }

  .score-item { }

  .score-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .score-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .score-value {
    font-size: 13px;
    font-weight: 700;
    font-family: monospace;
  }

  .progress-bar {
    height: 8px;
    background: #1e2533;
    border-radius: 99px;
    overflow: hidden;
    border: 1px solid var(--border);
  }

  .progress-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s cubic-bezier(.4,0,.2,1);
    width: 0%;
  }

  /* ---- BEHAVIORS LIST ---- */
  .behavior-item {
    background: #0d0f14;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 13px;
    line-height: 1.5;
  }

  /* ---- ADVICE CARDS ---- */
  .advice-item {
    background: #0d0f1488;
    border-left: 3px solid var(--accent);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text);
  }

  /* ---- STATS ---- */
  .stats-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  .stat-chip {
    background: #0d0f14;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 16px;
    flex: 1;
    min-width: 120px;
    text-align: center;
  }

  .stat-chip .num {
    font-size: 24px;
    font-weight: 800;
    font-family: monospace;
    color: var(--accent2);
    display: block;
  }

  .stat-chip .lbl {
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2px;
  }

  /* ---- LOADER ---- */
  #loader {
    display: none;
    text-align: center;
    padding: 40px;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    margin: 0 auto 16px;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  /* ---- ERROR BOX ---- */
  .error-box {
    background: #450a0a;
    border: 1px solid #dc2626;
    color: #f87171;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    font-size: 14px;
  }

  /* ---- FOOTER ---- */
  .footer {
    text-align: center;
    padding: 30px;
    color: #4a5568;
    font-size: 12px;
  }

  /* ---- FADE IN ANIMATION ---- */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .fade-in { animation: fadeIn 0.4s ease forwards; }
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div class="header-badge">🧠 NLP · Rule-Based · Mini Project</div>
  <h1>Toxic Friend Detector</h1>
  <p>Paste any WhatsApp chat. Our AI will judge your friendship so you don't have to.</p>
</div>

<div class="container">

  <!-- INPUT CARD -->
  <div class="card">
    <div class="card-title">Sample Chats — Auto Fill</div>
    <div class="sample-buttons">
      <button class="btn btn-healthy" onclick="fillSample('healthy')">✅ Healthy Chat</button>
      <button class="btn btn-toxic"   onclick="fillSample('toxic')">☠️ Toxic Chat</button>
      <button class="btn btn-dry"     onclick="fillSample('dry')">🌵 Dry Chat</button>
      <button class="btn btn-need"    onclick="fillSample('need_based')">📚 Need-Based Chat</button>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Paste Your Chat Here</div>
    <textarea id="chatInput" placeholder="Paste your WhatsApp chat here..."></textarea>
    <div class="input-row" style="margin-top:12px;">
      <button class="btn btn-analyze" onclick="analyzeChat()">🔍 Analyze Friendship</button>
      <button class="btn btn-clear"   onclick="clearAll()">🗑️ Clear</button>
    </div>
  </div>

  <!-- LOADER -->
  <div id="loader">
    <div class="spinner"></div>
    <p style="color:var(--muted); font-size:13px;">Analyzing friendship patterns...</p>
  </div>

  <!-- RESULTS -->
  <div id="results"></div>

</div>

<div class="footer">
  Built with 🐍 Python + Flask + Rule-Based NLP &nbsp;·&nbsp; Mini Project Demo
</div>

<script>
// Sample chat data from Python (injected)
const SAMPLES = {{ samples | tojson | safe }};

// Set placeholder via JS to avoid Jinja template conflicts
document.getElementById('chatInput').placeholder =
  "Paste your WhatsApp chat here...\n\nExample:\nAlex: Hey! How are you?\nSam: I'm good! Missed talking to you.\nAlex: Want to hang out this weekend?\nSam: Yes!! Let's do it! 😊";

function fillSample(type) {
  document.getElementById('chatInput').value = SAMPLES[type] || '';
  document.getElementById('results').style.display = 'none';
  document.getElementById('results').innerHTML = '';
}

function clearAll() {
  document.getElementById('chatInput').value = '';
  document.getElementById('results').style.display = 'none';
  document.getElementById('results').innerHTML = '';
}

function getScoreColor(label, value) {
  // Color logic per score type
  if (label === 'Toxicity' || label === 'Dryness' || label === 'Neediness') {
    if (value >= 60) return '#ef4444';
    if (value >= 30) return '#f97316';
    return '#22c55e';
  }
  if (label === 'Friendship' || label === 'Positivity') {
    if (value >= 60) return '#22c55e';
    if (value >= 30) return '#f97316';
    return '#ef4444';
  }
  return '#7c3aed';
}

function renderResults(data) {
  if (data.error) {
    return `<div class="error-box">⚠️ ${data.error}</div>`;
  }

  const s = data.scores;
  const scoreItems = [
    { label: 'Toxicity',   icon: '☠️',  value: s.toxicity   },
    { label: 'Friendship', icon: '💚',  value: s.friendship  },
    { label: 'Dryness',   icon: '🌵',  value: s.dryness    },
    { label: 'Neediness', icon: '📚',  value: s.neediness  },
    { label: 'Positivity',icon: '✨',  value: s.positivity  },
  ];

  const verdictClass = data.verdict_class;
  const verdictEmoji = {
    'healthy': '💚', 'toxic': '😠', 'extreme-toxic': '☠️',
    'dry': '🌵', 'need-based': '📚', 'average': '🤷', 'fake': '🎭'
  }[verdictClass] || '🤖';

  let html = `
  <div class="verdict-banner verdict-${verdictClass} fade-in">
    <span class="emoji">${verdictEmoji}</span>
    <div class="label">Final Verdict</div>
    <div class="verdict-text">${data.verdict}</div>
  </div>

  <div class="card fade-in">
    <div class="card-title">Friendship Scores</div>
    <div class="scores-grid">
      ${scoreItems.map(item => `
        <div class="score-item">
          <div class="score-header">
            <div class="score-label">${item.icon} ${item.label}</div>
            <div class="score-value" style="color:${getScoreColor(item.label, item.value)}">${item.value}/100</div>
          </div>
          <div class="progress-bar">
            <div class="progress-fill"
              id="bar-${item.label}"
              style="width:0%; background:${getScoreColor(item.label, item.value)}">
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  </div>`;

  // Stats
  html += `
  <div class="card fade-in">
    <div class="card-title">Chat Statistics</div>
    <div class="stats-row">
      <div class="stat-chip">
        <span class="num">${data.stats.total_messages}</span>
        <div class="lbl">Total Messages</div>
      </div>
      <div class="stat-chip">
        <span class="num">${data.stats.avg_length}</span>
        <div class="lbl">Avg Msg Length</div>
      </div>
      <div class="stat-chip">
        <span class="num">${data.stats.dry_replies}</span>
        <div class="lbl">Dry Replies</div>
      </div>
    </div>
  </div>`;

  // Detected Behaviors
  if (data.behaviors.length > 0) {
    html += `
    <div class="card fade-in">
      <div class="card-title">Detected Behaviors</div>
      ${data.behaviors.map(b => `<div class="behavior-item">${b}</div>`).join('')}
    </div>`;
  }

  // AI Advice
  html += `
  <div class="card fade-in">
    <div class="card-title">🤖 AI Relationship Advice</div>
    ${data.advice.map(a => `<div class="advice-item">${a}</div>`).join('')}
  </div>`;

  return html;
}

async function analyzeChat() {
  const text = document.getElementById('chatInput').value.trim();
  if (!text) {
    alert('Please paste a chat conversation first!');
    return;
  }

  // Show loader
  document.getElementById('loader').style.display = 'block';
  document.getElementById('results').style.display = 'none';
  document.getElementById('results').innerHTML = '';

  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat: text })
    });

    const data = await response.json();

    document.getElementById('loader').style.display = 'none';
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').innerHTML = renderResults(data);

    // Animate progress bars after render
    if (data.scores) {
      setTimeout(() => {
        const s = data.scores;
        const bars = {
          'Toxicity': s.toxicity, 'Friendship': s.friendship,
          'Dryness': s.dryness,   'Neediness': s.neediness,
          'Positivity': s.positivity
        };
        Object.entries(bars).forEach(([label, value]) => {
          const el = document.getElementById('bar-' + label);
          if (el) el.style.width = value + '%';
        });
      }, 100);
    }

    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch (err) {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').innerHTML =
      `<div class="error-box">❌ Something went wrong. Please try again.</div>`;
  }
}

// Allow Ctrl+Enter to analyze
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') analyzeChat();
});
</script>
</body>
</html>
"""

# ============================================================
# FLASK ROUTES
# ============================================================

@app.route('/')
def index():
    """Render the main page with sample chats injected."""
    return render_template_string(HTML_TEMPLATE, samples=SAMPLE_CHATS)


@app.route('/analyze', methods=['POST'])
def analyze():
    """API endpoint: receives chat text, returns analysis JSON."""
    data = request.get_json()
    if not data or 'chat' not in data:
        return jsonify({"error": "No chat data received."}), 400

    chat_text = data['chat']
    result = analyze_chat(chat_text)
    return jsonify(result)


# ============================================================
# RUN THE APP
# Supports local execution + Railway/cloud deployment
# ============================================================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("=" * 50)
    print("  🔍 Toxic Friend Detector")
    print(f"  Running on http://localhost:{port}")
    print("  Press Ctrl+C to stop")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=True)
