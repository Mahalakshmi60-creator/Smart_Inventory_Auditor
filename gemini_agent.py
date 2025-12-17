import google.generativeai as genai

API_KEY = "AIzaSyA7pZ6nYAx5YvqaSfG7NX6CqiW4bFzVOm4"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def audit_item(image):
    prompt = """
You are an inventory auditing agent.

TASK:
- Analyze the image
- Identify the item clearly

RULES (VERY IMPORTANT):
- Respond with ONLY valid JSON
- Do NOT add explanations
- Do NOT use markdown
- Do NOT add extra text

JSON FORMAT (STRICT):
{
  "item": "item_name",
  "category": "category_name"
}
"""

    response = model.generate_content([prompt, image])
    return response.text.strip()
