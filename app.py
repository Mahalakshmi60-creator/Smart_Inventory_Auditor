import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os
import re
import base64

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Smart Inventory Auditor",
    page_icon="📦",
    layout="centered"
)

# ==========================================================
# BACKGROUND IMAGE (LOCAL / URL)
# ==========================================================
def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# 🔴 Place a background image named bg.jpg in project folder
set_bg("bg.jpg")

# ==========================================================
# ADVANCED STYLES + ANIMATIONS
# ==========================================================
st.markdown("""
<style>

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

.glass {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(14px);
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.35);
  animation: fadeIn 1.2s ease-in;
  color: white;
}

.card {
  background: rgba(0,0,0,0.35);
  border-radius: 18px;
  padding: 18px;
  animation: float 4s ease-in-out infinite;
}

.badge {
  padding: 8px 20px;
  border-radius: 20px;
  font-weight: bold;
  color: black;
  display: inline-block;
  margin-top: 10px;
}

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# GEMINI CONFIG
# ==========================================================

API_KEY = "AIzaSyA7pZ6nYAx5YvqaSfG7NX6CqiW4bFzVOm4"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ==========================================================
# MOCK INVENTORY DB (Function Calling Simulation)
# ==========================================================
INVENTORY_DB = {
    "bottle": {"stock": "Low", "count": 3},
    "laptop": {"stock": "High", "count": 22},
    "phone": {"stock": "Medium", "count": 11},
    "mouse": {"stock": "High", "count": 40},
    "keyboard": {"stock": "Low", "count": 4},
}

def check_inventory(item):
    return INVENTORY_DB.get(item.lower(), {
        "stock": "Unknown",
        "count": 0
    })

# ==========================================================
# GEMINI AGENT (ROBUST JSON EXTRACTION)
# ==========================================================
def audit_item(image):
    prompt = """
You are an inventory auditing AI.

Identify the main object in the image.

Respond ONLY in valid JSON:

{
  "item": "item_name",
  "confidence": "short reasoning"
}
"""

    response = model.generate_content([prompt, image])
    raw = response.text.strip()

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        st.error("Gemini response invalid")
        st.code(raw)
        return None

    try:
        return json.loads(match.group())
    except:
        st.error("JSON parse failed")
        st.code(match.group())
        return None

# ==========================================================
# UI
# ==========================================================
st.markdown('<div class="glass">', unsafe_allow_html=True)

st.markdown("""
<h1 style="text-align:center;">📦 Smart Inventory Auditor</h1>
<p style="text-align:center;">
Upload an image → Gemini AI identifies → Inventory action triggered
</p>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("📷 Upload Item Image", type=["jpg", "jpeg", "png"])

if uploaded:
    image = Image.open(uploaded)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.image(image, caption="Uploaded Item", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.spinner("🤖 Gemini analyzing inventory..."):
        result = audit_item(image)

    if result:
        item = result["item"]
        reason = result["confidence"]
        inv = check_inventory(item)

        st.success("✅ Item Identified")

        st.markdown(f"""
        **🧾 Item:** `{item}`  
        **🧠 Reasoning:** {reason}  
        **📊 Stock Count:** {inv["count"]}
        """)

        colors = {
            "Low": "#ff4b4b",
            "Medium": "#ffa500",
            "High": "#00ff9c",
            "Unknown": "#cccccc"
        }

        st.markdown(
            f'<span class="badge" style="background:{colors[inv["stock"]]};">'
            f'{inv["stock"]} Stock</span>',
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# FOOTER
# ==========================================================

