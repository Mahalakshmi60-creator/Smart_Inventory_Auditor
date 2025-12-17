import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import os
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
# BACKGROUND IMAGE
# ==========================================================
def set_bg(image_path):
    if not os.path.exists(image_path):
        return
    with open(image_path, "rb") as f:
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

# Put bg.jpg in same folder
set_bg("bg.jpg")

# ==========================================================
# STYLES + ANIMATIONS
# ==========================================================
st.markdown("""
<style>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-6px); }
  100% { transform: translateY(0px); }
}

.glass {
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(14px);
  border-radius: 22px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  animation: fadeIn 1.2s ease-in;
  color: white;
}

.card {
  background: rgba(0,0,0,0.35);
  border-radius: 18px;
  padding: 15px;
  animation: float 4s ease-in-out infinite;
}

.badge {
  padding: 8px 18px;
  border-radius: 20px;
  font-weight: bold;
  color: black;
  display: inline-block;
  margin-top: 12px;
}

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# GEMINI CONFIG (STREAMLIT CLOUD SAFE)
# ==========================================================
API_KEY = os.getenv("AIzaSyBCuOYAkp9YUyvTYc-GIRWmLjU8DkozI2o")

if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found. Add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ==========================================================
# MOCK INVENTORY DATABASE
# ==========================================================
INVENTORY_DB = {
    "bottle": {"stock": "Low", "count": 3},
    "laptop": {"stock": "High", "count": 24},
    "phone": {"stock": "Medium", "count": 12},
    "mouse": {"stock": "High", "count": 40},
    "keyboard": {"stock": "Low", "count": 5}
}

def check_inventory(item):
    return INVENTORY_DB.get(item.lower(), {
        "stock": "Unknown",
        "count": 0
    })

# ==========================================================
# GEMINI AGENT (NO IMAGE REOPENING ❗)
# ==========================================================
def audit_item(image):
    prompt = """
You are a smart inventory auditing AI.

Identify the main item in the image.

Respond ONLY in valid JSON:

{
  "item": "item_name",
  "confidence": "short reasoning"
}
"""

    response = model.generate_content([prompt, image])
    raw_text = response.text.strip()

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        st.error("❌ Gemini did not return JSON")
        st.code(raw_text)
        return None

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        st.error("❌ JSON parsing failed")
        st.code(match.group())
        return None

# ==========================================================
# UI
# ==========================================================
st.markdown('<div class="glass">', unsafe_allow_html=True)

st.markdown("""
<h1 style="text-align:center;">📦 Smart Inventory Auditor</h1>
<p style="text-align:center;">
Upload an image → Gemini AI identifies it → Inventory action triggered
</p>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("📸 Upload item image", type=["jpg", "jpeg", "png"])

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
        **🧠 AI Reasoning:** {reason}  
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
st.markdown("""
<div style="text-align:center; color:#ddd; margin-top:30px;">
🚀 Built with Streamlit + Gemini API<br>
Theme 1 – Multimodal Function Calling
</div>
""", unsafe_allow_html=True)
