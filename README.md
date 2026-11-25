# SightAssist

README prose word count: 235

AI-assisted image descriptions for blind and low-vision users. Prototype for Assignment 2.

## Project status
- **Implemented:** image upload, Concise/Detailed description, follow-up questions about the same image, AI-error warning on every description.
- **Simulated:** Demo mode returns canned responses so the interface can be inspected without an API key. These are not model outputs.
- **Planned (not built):** read-aloud, camera capture, guided retake prompts, "report wrong description" button, saved history.

## Technology stack
- Python and Streamlit: the interface.
- OpenAI API (vision-capable chat model, default `gpt-4o-mini`, set with `OPENAI_MODEL`): generates descriptions and follow-up answers. Model choice is not final.
- A system prompt asks for context and layout first, plain statements of uncertainty, and no medical, legal or financial advice.

## Running it
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your-own-key   # optional; or paste it in the sidebar
streamlit run app.py
```
No key is included. Without one the app starts in Demo mode. The key typed in the sidebar is kept in the session only.

## Development record
Link commits here. Edit this section to match your real history:
- Stage 1: upload and single description. [commit link]
- Stage 2: Concise/Detailed control. [commit link]
- Stage 3: follow-up questions and uncertainty warnings. [commit link]
- Stage 4: Demo mode for key-free inspection. [commit link]

## AI assistance
Claude was used to help draft `app.py` and the storyboards. Edit this to say what you checked or changed (for example: ran the app, tested real images, changed the prompt wording).

## Additional files
Storyboards: `sightassist-storyboards.html` (open in a browser).
