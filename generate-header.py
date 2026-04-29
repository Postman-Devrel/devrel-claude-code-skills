import json, base64, urllib.request, os

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not set. Add it to ~/.claude/settings.json under 'env'")
MODEL = "gemini-3-pro-image-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

prompt = (
    "A wide landscape 2D illustration for a blog header about API performance testing with Postman Collections.\n\n"
    "MANDATORY RULES:\n"
    "1. The ENTIRE Postmanaut CHARACTER is ONLY black outlines and white fill. NO grey areas, NO colored areas, NO shading on the character body, suit, helmet, backpack, or limbs. The ONLY exception is the orange antenna: a thin black stick extends UPWARD from the TOPMOST POINT of the helmet with a small solid orange dot at its tip. The antenna MUST be the highest point on the character. The stick MUST be visible. NOTE: Other elements in the scene CAN and SHOULD use full color from the Postman palette.\n"
    "2. The character has ABSOLUTELY NO HANDS and NO FEET. Every arm ends in a smooth rounded sausage tip. Every leg ends in a smooth rounded sausage tip. There are ZERO lines at the wrists or ankles. Each limb is one single unbroken tube from body to rounded tip.\n"
    "3. The ground shadow beneath each character MUST be a small narrow pill/capsule shape in light grey (#E6E6E6) ONLY.\n"
    "4. There must be a small empty outlined rectangle (no fill) on the LEFT chest as a patch.\n"
    "5. Two backpack straps MUST be visible, each a SINGLE thin black line.\n"
    "6. The helmet visor MUST be COMPLETELY BLANK. NO eyes, NO dots, NO mouth, NO facial features.\n\n"
    "The scene shows a Postmanaut standing in the lower-left area, looking up at a large colorful speedometer/performance gauge in the upper-right. The gauge needle points to the green/fast zone. Between the Postmanaut and the gauge, there are floating elements: a rounded rectangle card showing horizontal bar charts in purple and orange (representing response time metrics), a small circular checkmark icon in Flora Green, and a stopwatch outline icon. To the far right, a small collection folder icon in Postman Orange. The Postmanaut holds an outline-only clipboard, observing the performance results. Small 4-point star sparkles are scattered in the background. The Postman logo (orange circle with rocket mark) floats near the top-left corner. The background contains only simple geometric shapes like circles, diamonds, and rounded rectangles. No code symbols, no brackets, no arrows, no curly braces, no angle brackets, no terminal prompts.\n\n"
    "The character is a Postmanaut with natural balanced proportions. The ENTIRE character is drawn ONLY in black outlines and white fill. The only color on the character is the orange antenna dot at the tip of a thin black vertical stick extending from the TOPMOST POINT of the helmet.\n\n"
    "The Postmanaut must be SMALL, no taller than 35 percent of the image height, occupying the lower portion with plenty of space above.\n\n"
    "Postmanaut design specification:\n"
    "1. HELMET: Rounded smooth helmet with COMPLETELY BLANK white visor. NO facial features.\n"
    "2. ANTENNA: Thin black vertical stick from the TOPMOST POINT of the helmet with orange circle at tip.\n"
    "3. BODY: Natural balanced proportions. Uniform thin black outline strokes with solid white fill ONLY.\n"
    "4. BACKPACK: Rectangular backpack on the back, black outline, white fill.\n"
    "5. STRAPS: Two backpack straps, each a SINGLE thin black line.\n"
    "6. CHEST PATCH: Small rectangular patch on the LEFT chest, thin black outline rectangle ONLY, no fill.\n"
    "7. ARMS AND LEGS: NO hands and NO feet. All limbs are simple tubes ending in smooth rounded tips. NO lines at wrists or ankles.\n"
    "8. SHADOW: Small narrow pill-shaped ground shadow in light grey (#E6E6E6) beneath feet.\n\n"
    "Style: geometric, clean, modern 2D flat illustration. Uniform thin stroke weights.\n"
    "Background: smooth gradient from Teal 20 #D0F9FD at top to white #FFFFFF at bottom. Scene elements use FULL COLOR from Postman palette: Orange (#FF6C37), Yellow (#FFDE83), Green (#A4EEC4), Blue (#ADCDFB), Purple (#784FA9).\n\n"
    "CRITICAL REMINDERS:\n"
    "- Postmanaut CHARACTER ONLY is black outlines and white fill. Everything else CAN use full color.\n"
    "- NO hands, NO feet. All limbs are tubes ending in rounded tips.\n"
    "- NO text anywhere except short acronyms like API.\n"
    "- Shadow is a small narrow pill, NOT a wide ellipse.\n"
    "- Character is SMALL, no more than 35 percent of the image height."
)

payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "responseModalities": ["IMAGE"],
        "imageConfig": {
            "aspectRatio": "16:9",
            "imageSize": "2K"
        }
    }
}

req = urllib.request.Request(
    URL,
    data=json.dumps(payload).encode(),
    headers={
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json"
    }
)

try:
    resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
    for part in resp["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            img_data = base64.b64decode(part["inlineData"]["data"])
            out_path = "/tmp/blog-header-raw.png"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"Image saved to {out_path}")
            break
    else:
        print("No image data found in response")
        print(json.dumps(resp, indent=2)[:2000])
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
