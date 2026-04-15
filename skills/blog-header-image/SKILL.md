---
name: blog-header-image
description: "Generate a Postman-branded blog header image (2560×1355 PNG, no text) using the Gemini image generation API (nanobanana). Analyzes reference images and follows the Postman design system for consistent brand visuals."
argument-hint: "[blog topic or path to blog post] (e.g. 'OAuth 2.0 in Postman' or 'blog-output/my-post.md')"
---

# Blog Header Image Generator

Generate on-brand Postman blog header images using the Gemini image generation API (nanobanana). Produces 2560×1355 PNG images with no text, following the Postman design system and matching the visual style of existing blog headers.

## Input Handling

This skill accepts flexible input:

- **A topic string** (e.g., "Testing OAuth 2.0 flows in Postman") — generate a header image for this topic
- **A file path** (e.g., `blog-output/my-post.md`) — read the blog post and generate a matching header image
- **No argument** — ask the user what blog topic the header image is for

If a file path is provided, read the file first and extract the topic, key themes, and any relevant context to inform the image prompt.

## Workflow

### Step 1: Understand the Visual Style

Read the Postman design system and study reference images to understand the brand visual language:

1. Read `blog-header-image/postman-design-system.md` — internalize brand colors, illustration style, and design principles
2. Read `blog-header-image/manifest.json` — scan the reference image catalog to understand existing header image patterns
3. View 3-5 reference images from `blog-header-image/images/` that are most relevant to the blog topic's category. Use the Read tool to view the images directly. Pick images from the category that best matches the topic (e.g., `ai-and-agents/` for AI topics, `api-architecture/` for API design topics, `authentication-and-security/` for security topics).
4. **Analyze the reference images carefully** — pay close attention to layout, composition, character placement, background element density and arrangement, use of whitespace, and how the Postmanaut interacts with surrounding objects. Your generated image should feel like it belongs in the same collection as these reference images. Note specific patterns: where the character sits in the frame, how large background shapes are relative to the character, the balance between decorative elements and empty space.

**Available categories:**
- `ai-and-agents/` — AI, agents, Claude, LLMs
- `api-architecture/` — REST, GraphQL, microservices, API design
- `api-testing-and-monitoring/` — Testing, monitoring, assertions
- `authentication-and-security/` — OAuth, JWT, encryption, security
- `building-apis/` — SDK generation, API creation, mocking
- `data-formats-and-protocols/` — JSON, XML, protocols
- `developer-experience/` — Workflows, collaboration, productivity
- `enterprise-and-governance/` — Enterprise features, compliance
- `events-and-community/` — Conferences, events, meetups
- `graphql/` — GraphQL-specific content
- `http-and-web-fundamentals/` — HTTP basics, status codes
- `integrations-and-partnerships/` — CI/CD, GitHub, Slack
- `product-updates/` — New releases, features
- `workspaces-and-collaboration/` — Team features, Git integration

### Step 2: Craft the Image Prompt

Build a detailed image generation prompt that combines what you learned from studying the reference images with the topic and brand guidelines:

1. **Topic context** — What the blog post is about, translated into visual concepts
2. **Postman brand style** — Based on the design system and **specifically what you observed in the reference images you just studied**. Your prompt should reproduce the same layout patterns, composition style, and element density you saw in those images:
   - Geometric, simple, concise illustration style
   - 2D plane with depth conveyed through hierarchy and shadows
   - Clean, modern aesthetic with Postman's visual language
   - Background elements without strokes
   - Pill-shaped ground shadows
   - White fill on illustrations for dark background compatibility
3. **Color palette** — Use Postman brand colors from the design system:
   - Primary: Postman Orange (#FF6C37), White (#FFFFFF)
   - Secondary: Background Navy (#01213C), Elemental Yellow (#FFDE83), Flora Green (#A4EEC4), Sky Blue (#ADCDFB), Galaxy Purple (#784FA9)
   - Blog backgrounds: Yellow 20 (#FFF4BE), Orange 20 (#FFD1BE), Blue 20 (#ADCDFB), Purple 20 (#E4D8F6), Teal 20 (#D0F9FD)
4. **Composition** — Wide landscape format suitable for a blog header (roughly 2:1 aspect ratio)
5. **Logos** — If the blog topic mentions specific technology frameworks, products, or companies (e.g., "Claude", "GitHub", "Node.js", "React", "Docker", "Kubernetes", "AWS", "OpenAI", "Anthropic"), include their recognizable logos as floating elements in the scene. Use simplified, iconic logo forms that match the flat illustration style. Postman content should always include the Postman logo (orange rocket/circle mark). If the blog is about a partnership or integration between Postman and another product, both logos must appear. Logos should be clean, recognizable, and sized proportionally to other background elements — not dominating the composition.

**Characters (Postmanauts):**
If the illustration includes a character or figure, it MUST use the Postmanaut style. Before crafting the prompt, view the reference image at `blog-header-image/astronaught-style.png` to study the character style. Postmanauts are:
- Simple line-drawn astronaut characters with rounded helmets and a small orange antenna/dot on top. No other colors on the character besides black outlines and white fill.
- Minimal detail — clean black outlines on white fill, no facial features visible through the visor
- Friendly, approachable poses (waving, holding objects, looking through magnifying glasses, reading tablets)
- Uniform thin stroke weight throughout the character
- Small, pill-shaped ground shadows beneath their feet
- They interact with floating icons, speech bubbles, and brand-colored UI elements around them
- Style is whimsical and sketch-like, not photorealistic
- Arms end in simple rounded stubs — no fingers, no thumbs, no mitten or glove shapes. Can hold outline-only items like magnifying glasses, tablets, or tools
- they have a small rectangular patch on their left chest, above the heart, which is just an outline with no fill

When including a Postmanaut in the prompt, describe it as: "a simple line-drawn astronaut character (Postmanaut) with a rounded helmet, thin black antenna stick extending straight up from the topmost point (apex) of the helmet with orange dot at the tip, rectangular backpack, two vertical straps one on each shoulder (black outline, no fill), small outline-only rectangular patch on the left chest (no fill), clean black outlines, white fill, no visible face, arms ending in simple rounded stubs with no fingers or thumbs, pill-shaped Shadow Grey (#E6E6E6) ground shadow, in a friendly pose — may hold outline-only items"

**Prompt construction rules:**
- **NO TEXT** in the image — explicitly state "no text, no words, no letters, no labels, no captions, no code, no terminal output, no UI text, no symbols that resemble letters or words" in EVERY prompt. EXCEPTION: short topic-relevant acronyms (e.g., "API", "HTTP", "JSON", "SDK") may appear if they add clarity to the illustration
- Focus on abstract or conceptual illustrations, not photorealistic renders
- Reference specific visual elements, layouts, and compositions from the reference images you studied — describe what you saw (e.g., "character centered in lower third with large geometric shapes in upper corners" or "character off to one side interacting with a floating object")
- Include Postman's illustration style: geometric shapes, clean lines, uniform stroke weights
- Mention the color palette explicitly using hex values or color names
- Describe the composition for a wide banner format
- **Every prompt MUST include the full Postmanaut specification below** — do not abbreviate or omit any detail

**Required prompt template — COPY THIS VERBATIM into the API call, only replacing the [bracketed] sections. Do NOT paraphrase, reword, shorten, or omit ANY line:**
```
A wide landscape 2D illustration for a blog header about [topic].

MANDATORY RULES — if ANY rule is violated, the image is rejected and must be regenerated:
1. The ENTIRE Postmanaut CHARACTER is ONLY black outlines and white fill. NO grey areas, NO colored areas, NO shading on the character body, suit, helmet, backpack, or limbs. The ONLY exception is the orange antenna: a thin black stick/line extends UPWARD from the TOPMOST POINT of the helmet (the very apex/crown — NOT the side, NOT the back, NOT near the visor) with a small solid orange dot at its tip. The antenna MUST be the highest point on the character — nothing else on the helmet is above it. The stick MUST be visible — NOT just a dot sitting on the helmet. NOTE: This rule applies ONLY to the Postmanaut character. Other elements in the scene (background, logos, floating icons, objects, decorations) CAN and SHOULD use full color and fill from the Postman palette.
2. The character has ABSOLUTELY NO HANDS and NO FEET. Every arm ends in a smooth rounded sausage tip — NO fingers, NO thumbs, NO palms, NO mitten shapes. Every leg ends in a smooth rounded sausage tip — NO shoes, NO boots, NO toes, NO soles. There are ZERO lines at the wrists or ankles — no cuffs, no bands, no rings, no separation marks, no creases. Each limb is one single unbroken tube from body to rounded tip. This is the most commonly failed rule — pay extra attention to it.
3. The ground shadow beneath each character MUST be a small narrow pill/capsule shape in light grey (#E6E6E6) ONLY — NOT a wide ellipse, NOT dark grey, NOT black, NOT any other color. The shadow goes directly under the character's feet, not under furniture or objects.
4. There must be a small empty outlined rectangle (no fill) on the LEFT chest as a patch.
5. Two backpack straps MUST be visible — one over each shoulder. Each strap is a SINGLE thin black line. NOT thick bands, NOT filled shapes.
6. The helmet visor MUST be COMPLETELY BLANK — pure white/empty. NO eyes, NO dots, NO mouth, NO facial features of any kind. The Postmanaut has NO face.

The scene shows [visual concept — what the Postmanaut is doing that DIRECTLY relates to the blog topic. The surrounding objects and scene elements must clearly represent the topic. e.g. for "API testing" show test tubes or checklists, for "CLI tools" show a terminal window outline, for "Git integration" show branching lines. The viewer should be able to guess the blog topic from the illustration alone]. [If the topic mentions specific frameworks, products, or companies, include their simplified recognizable logos as floating elements — e.g., Claude/Anthropic starburst, GitHub octocat silhouette, Docker whale, React atom, Node.js hexagon, AWS cube. Always include the Postman logo (orange rocket/circle mark) for Postman content. Logos should be flat, iconic, and proportionally sized.] The Postmanaut can be shown from any angle — front, side, three-quarter view, or from behind. Vary the pose naturally. The background contains only simple geometric shapes like circles, diamonds, and rounded rectangles. No code symbols, no brackets, no arrows, no curly braces, no angle brackets, no terminal prompts.

The character is a Postmanaut — a simple line-drawn astronaut with natural, balanced proportions (not too thin, not too wide — similar to a cartoon character in a spacesuit). The ENTIRE character is drawn ONLY in black outlines and white fill. No orange, no color anywhere on the character body, straps, or suit. The only color on the character is the orange antenna dot: a thin black vertical stick/line extends straight upward from the TOPMOST POINT (apex/crown) of the helmet, with a small solid orange circle at its tip. The antenna must always be at the very top of the helmet — never on the side or offset.

The Postmanaut must be SMALL — no taller than 50% of the image height. The character should be clearly smaller than the surrounding scene, occupying the lower portion with plenty of space above and around it for background elements and decoration. Think of the character as a small figure in a large world.

Postmanaut design specification:
1. HELMET: Rounded smooth helmet with a COMPLETELY BLANK white visor. The visor MUST be empty white — NO eyes, NO mouth, NO nose, NO dots, NO circles, NO facial features of any kind visible through or on the visor. The face area is simply white/empty.
2. ANTENNA: A thin black vertical stick/line extends straight up from the TOPMOST POINT (apex/crown) of the helmet — the very highest center of the dome. The antenna MUST be at the absolute top of the helmet, never on the side, front, or back. A small solid orange circle sits at the tip of the stick. The stick is visible — it is NOT just a dot sitting on the helmet. The antenna must be the highest point on the entire character. This is the ONLY non-black, non-white element on the character.
3. BODY: Natural, balanced proportions — not too thin, not too wide. The character should look like a friendly cartoon astronaut, similar proportions to the reference image. Uniform thin black outline strokes with solid white fill ONLY. No colored areas, no grey areas, no shading, no gradients anywhere on the suit or any part of the character.
4. BACKPACK: A rectangular backpack on the back, black outline, white fill.
5. STRAPS: Two backpack straps, one over each shoulder. Each strap is a SINGLE thin black line — not two parallel lines with fill between them. Just one thin black stroke per strap, like a line drawn with a pen. No fill, no thickness, no color, no grey.
6. CHEST PATCH: A small rectangular patch on the LEFT side of the chest above the heart. It is a thin black outline rectangle ONLY — no fill inside, no color, no icon, just an empty outlined rectangle.
7. ARMS AND LEGS: There are NO hands and NO feet. All four limbs are simple tubes (same width throughout) that end in a smooth rounded tip — like a sausage. There is NO distinct hand shape, NO palm, NO mitten, NO glove, NO heart shape, NO widening at the end. There are NO shoes, NO boots, NO toes. There are NO lines at the wrists or ankles — no cuffs, no bands, no separation marks. Each limb is one continuous tube shape from body to rounded tip. The Postmanaut can hold items (magnifying glass, tablet, tools) by having the arm tip touch or wrap around the object. Any held items must be drawn in black outline only with no fill.
8. SHADOW: A small narrow pill-shaped (capsule) ground shadow directly beneath the feet in light grey (#E6E6E6). The shadow is narrow — no wider than the character's shoulders. NOT a wide ellipse, NOT a circle, NOT an oval. A narrow capsule shape.

Style: geometric, clean, modern 2D flat illustration. Uniform thin stroke weights throughout. Simple and minimal.
Background: [background from Postman palette — can be a solid color (e.g. "soft orange #FFD1BE") OR a smooth gradient between two palette colors (e.g. "a gradient from Orange 20 #FFD1BE to Purple 20 #E4D8F6")]. Background and scene elements can use FULL COLOR and FILL from the Postman palette: Orange (#FF6C37), Navy (#01213C), Yellow (#FFDE83), Green (#A4EEC4), Blue (#ADCDFB), Purple (#784FA9). Background decorations, floating icons, logos, and scene objects CAN be filled with color — only the Postmanaut character itself is restricted to black outlines and white fill. Background shapes are abstract — circles, dots, diamonds, rounded rectangles, stars. Do NOT include any code-related symbols.

CRITICAL REMINDERS (repeat for emphasis):
- The Postmanaut CHARACTER ONLY is restricted to black outlines and white fill with no shading. Background, logos, icons, and other scene elements CAN use full color and fill. The antenna is a thin black STICK extending straight up from the TOPMOST POINT (apex) of the helmet with an orange dot at the tip — NOT a dot sitting directly on the helmet, NOT on the side or back of the helmet. The antenna must always be at the very top center of the dome.
- NO lines at wrists or ankles. Each limb is ONE unbroken tube from body to rounded tip.
- NO hands, NO feet — all limbs are tubes ending in rounded tips. NO fingers, NO thumbs, NO shoes. Held items are outline only.
- Backpack straps are thin black lines ONLY — no grey fill, no color fill.
- NO text, words, sentences, labels, captions, code, terminal symbols, curly braces, angle brackets, or arrow symbols anywhere in the image. Short topic-relevant acronyms (API, HTTP, JSON, SDK, CLI, REST, AI, etc.) are the ONLY text allowed.
- Shadow is a small narrow pill — NOT a wide ellipse.
- Chest has an empty outlined rectangle patch on the LEFT side.
- Character is SMALL — no more than 35% of the image height. The character should occupy the lower portion of the scene with plenty of space above for background elements and decoration.
```

**IMPORTANT: Do NOT modify this template.** Copy it character-for-character into the API request, only filling in the [bracketed] parts. Every failed image has been caused by omitting or rewording parts of this specification.

### Step 3: Generate the Image

**IMPORTANT: Use a Python script, NOT curl.** The prompt contains special characters (parentheses, quotes, etc.) that cause shell escaping issues with curl. Always use the Python approach below.

Write a Python script to `/tmp/generate-header.py` and run it via `python3 /tmp/generate-header.py`:

```python
import json, base64, urllib.request, os

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not set. Add it to ~/.claude/settings.json under 'env'")
MODEL = "gemini-3-pro-image-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

prompt = """YOUR_PROMPT_HERE"""

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

resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
for part in resp["candidates"][0]["content"]["parts"]:
    if "inlineData" in part:
        img_data = base64.b64decode(part["inlineData"]["data"])
        with open("/tmp/blog-header-raw.png", "wb") as f:
            f.write(img_data)
        print("Image saved to /tmp/blog-header-raw.png")
        break
```

Replace `YOUR_PROMPT_HERE` with the full prompt from Step 2 inside the triple-quoted string. This avoids all shell escaping issues.

**Important API details:**
- Model: `gemini-3-pro-image-preview` (nanobanana)
- Aspect ratio: `16:9` (closest standard ratio to the 2560×1355 target)
- Image size: `2K` for high quality output
- Response modalities: `["IMAGE"]` for image-only output

If the API call fails:
- Check the error message in the response
- If the model name is invalid, check available Gemini 3 models
- If the prompt is rejected, simplify it and remove any potentially problematic content
- Retry up to 2 times with adjusted prompts before asking the user for guidance

### Step 4: Resize to Exact Dimensions

Use `sips` (macOS built-in) to resize the generated image to exactly 2560×1355:

```bash
mkdir -p ${CLAUDE_PLUGIN_ROOT}/blog-output/images/header && sips -z 1355 2560 /tmp/blog-header-raw.png --out ${CLAUDE_PLUGIN_ROOT}/blog-output/images/header/FILENAME.png
```

Where `FILENAME` follows the naming convention above: `header-{markdown-basename}.png` if the input was a file path, or `header-{slugified-topic}.png` if the input was a topic string.

If `sips` is not available, fall back to Python:

```bash
python3 -c "
from PIL import Image
img = Image.open('/tmp/blog-header-raw.png')
img = img.resize((2560, 1355), Image.LANCZOS)
import os; os.makedirs('${CLAUDE_PLUGIN_ROOT}/blog-output/images/header', exist_ok=True)
img.save('${CLAUDE_PLUGIN_ROOT}/blog-output/images/header/FILENAME.png', 'PNG')
print('Resized to 2560x1355')
"
```

### Step 5: Verify Dimensions

Verify the output image exists and has the correct dimensions:
```bash
sips -g pixelHeight -g pixelWidth ${CLAUDE_PLUGIN_ROOT}/blog-output/images/header/FILENAME.png
```

### Step 6: Quality Check — Postmanaut Style Verification

Use the Read tool to view the generated image. Then view the reference image at `blog-header-image/astronaught-style.png` side by side for comparison.

**Score the image out of 10** based on these Postmanaut design element criteria:

| Element | Required | Points |
|---------|----------|--------|
| **Rounded helmet** | Smooth, round astronaut helmet with visible visor area | 1 |
| **Orange antenna dot on stick at helmet apex** | A thin black stick/line extends straight up from the TOPMOST POINT (apex/crown) of the helmet with an orange dot at the tip. FAIL if: the orange dot sits directly on the helmet with no visible stick, OR the antenna is on the side/front/back of the helmet instead of the very top | 1 |
| **Backpack** | Rectangular backpack on the character's back, matching the reference style | 1 |
| **Backpack straps** | Two vertical straps, one on each shoulder — each strap is a single thin black line, NOT two parallel lines with fill between them. If the straps appear as thick bands or have any grey/white/colored fill — this is a FAIL | 1 |
| **Chest patch** | A small patch or marking is present on the chest area. It may be subtle at smaller character sizes — pass if any small rectangular detail is visible on the chest, even if faint | 1 |
| **Clean black outlines** | Uniform thin stroke weight, simple line-drawn style, white fill | 1 |
| **Ground shadow** | A narrow pill/capsule-shaped shadow in light grey (#E6E6E6) beneath the character's feet. FAIL if: no shadow present, shadow is a wide ellipse instead of a narrow pill, or shadow is the wrong color (e.g. dark grey, black, or any non-light-grey color) | 1 |
| **No visible face** | The visor must be completely blank/white. FAIL if ANY facial features are visible — eyes, dots for eyes, mouth, nose, smile, or any marks that suggest a face. Even simple dot eyes are a FAIL | 1 |
| **Tube limbs (no hands/feet)** | All limbs must be simple tubes ending in smooth rounded tips. FAIL if: any fingers or thumbs are visible (even partially), any hand/palm/mitten shape exists, any shoes/boots/feet are drawn, or any lines appear at wrists or ankles (cuffs, bands, separation marks). Be strict — if it looks like a hand or foot rather than a rounded tube end, it's a FAIL. Held items must be outline only | 1 |
| **No wrist/ankle lines** | Limbs must be unbroken tubes from body to tip. FAIL if there are any lines, cuffs, bands, or rings at the wrists or ankles that create a separation between the arm and hand area or leg and foot area | 1 |
| **No text in image** | The image contains no text, words, or letters. EXCEPTION: short acronyms (e.g., "API", "HTTP", "JSON", "SDK", "CLI", "REST", "AI") are allowed when they directly relate to the blog topic. FAIL if any full words, sentences, labels, captions, or code appear | 1 |
| **Relevant logos included** | If the blog topic mentions specific frameworks, products, or companies, their recognizable logos appear as floating elements in the scene. Postman content includes the Postman logo. Partnership/integration posts include both logos. FAIL if named products/companies from the topic are absent from the illustration. If the topic mentions NO specific named products, this criterion automatically passes | 1 |

**Score interpretation (100% pass rate required):**
- **12/12 (100%)**: Pass — image meets quality standards, proceed to present results
- **ANY score below 12/12**: Fail — even a single failed criterion means regeneration is required. No partial passes allowed.

### Step 7: Present Results

Present the result to the user:
- Show the generated image (use Read tool so the user can see it)
- Show the file path
- Confirm the dimensions (2560×1355)
- Describe what the image depicts
- **Show the quality score as "Postmanaut Style Score: X/12"**
- List which design elements passed and which failed

**If the score is below 12/12 (any failed criterion):**
1. Tell the user which specific design elements are missing or incorrect
2. Ask: "This image scored X/10. Would you like me to regenerate with a revised prompt to fix: [list missing elements]?"
3. If the user says yes:
   - Delete the failed image: `rm ${CLAUDE_PLUGIN_ROOT}/blog-output/images/header/FILENAME.png`
   - Revise the prompt to emphasize the missing design elements
   - Go back to **Step 3** and regenerate
   - Repeat the quality check on the new image
4. If the user says no, keep the image as-is

## Output

**IMPORTANT: Always write images to `${CLAUDE_PLUGIN_ROOT}/blog-output/images/header/`. Never write to any other directory.**

- **Location:** `${CLAUDE_PLUGIN_ROOT}/blog-output/images/header/header-{slugified-topic}.png`
- **Dimensions:** 2560×1355 pixels
- **Format:** PNG
- **Content:** No text — illustration only

Create the `${CLAUDE_PLUGIN_ROOT}/blog-output/images/header/` directory if it doesn't exist.

## File Naming

**If the input was a file path** (e.g., `blog-output/my-post.md`), name the image to match the markdown file:
- `blog-output/my-post.md` → `header-my-post.png`
- `blog-output/eliminate-context-switching-postman-native-git-mcp.md` → `header-eliminate-context-switching-postman-native-git-mcp.png`

**If the input was a topic string**, use the slugified topic:
- Topic "OAuth 2.0 in Postman" → `header-oauth-2-in-postman.png`
- Topic "Testing MCP Servers" → `header-testing-mcp-servers.png`

## Important Guidelines

- **NEVER include text** in the generated image — no titles, labels, captions, watermarks, or any written words
- **Follow the Postman design system** — use brand colors, illustration style, and visual language
- **Study reference images first** — always view relevant reference images before crafting the prompt to match the established visual style
- **Wide composition** — design for a 2560×1355 banner format, not square or portrait
- **Abstract over literal** — prefer conceptual illustrations over photorealistic renders
- **Clean and simple** — match Postman's geometric, concise illustration style
- **Consistent with existing headers** — the generated image should feel like it belongs alongside existing Postman blog headers
- If the generated image contains text despite the prompt, regenerate with stronger "no text" instructions
- If the image quality is poor or off-brand, adjust the prompt and regenerate
