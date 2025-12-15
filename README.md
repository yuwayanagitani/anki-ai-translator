# AI Card Translator (Anki Add-on)

AI Card Translator translates Anki card content (question and/or answer) using an AI model, and writes the translated text into **separate target fields** (e.g., `Front_jp`, `Back_jp`).

It’s intended for study workflows where you keep the original text and store the translation alongside it—without manually copying and pasting.

---

## What it does

For each note, the add-on can:

1. Read a **source question field** and/or **source answer field**
2. Send that text to an AI provider (OpenAI or Gemini)
3. Receive a JSON result: `{"question": "...", "answer": "..."}`
4. Write translated text into the configured **target fields**
5. Add a tag to mark the note as translated (and optionally an error tag if something failed)

The add-on can translate:
- only the question
- only the answer
- both

---

## How to use

### 1) Translate many notes (Tools menu / search query mode)

Menu item:
- **Tools → Translate Cards with AI**

Flow:
1. Enter an Anki search query (example: `deck:Renal tag:en`)
2. The add-on selects notes that match the query
3. It skips notes according to your rules (see “Skip rules”)
4. It translates remaining notes with a progress bar
5. It shows a summary (translated / skipped / errors)
6. If there were errors, it shows an error report dialog at the end

---

### 2) Translate the current review card (Reviewer hotkey)

Default hotkey:
- **Ctrl+Shift+T**

When pressed in the Reviewer, the add-on translates the current card’s note (if not skipped by rules), applies the translation, and refreshes Anki.

---

## Setup: API keys (required)

This add-on reads API keys from **environment variables** (by default):

- OpenAI: `OPENAI_API_KEY`
- Gemini: `GEMINI_API_KEY`

If the environment variable is missing, the add-on will raise an error like:
- “Environment variable 'OPENAI_API_KEY' is not set.”

Tip: environment variables must be visible to the **Anki process** (often requires restarting Anki after setting them).

---

## Configuration

Open:
- **Tools → Add-ons → AI Card Translator → Config**

The add-on provides a settings dialog and saves the values into `config.json`.

### Provider

- `provider`: `openai` or `gemini`

OpenAI:
- `openai_model` (default: `gpt-4o-mini`)
- `openai_api_base` (default: `https://api.openai.com/v1/chat/completions`)
- `openai_api_key_env` (default: `OPENAI_API_KEY`)

Gemini:
- `gemini_model` (default: `gemini-2.5-flash-lite`)
- `gemini_api_base` (default: `https://generativelanguage.googleapis.com/v1`)
- `gemini_api_key_env` (default: `GEMINI_API_KEY`)

---

### Languages

- `source_language` (default: `English`)
- `target_language` (default: `Japanese`)

These values are included in the translation prompt, so you can use any language names you prefer.

---

### Field mapping

Default mapping is designed for bilingual note types:

- `question_source_field`: `Front`
- `question_target_field`: `Front_jp`
- `answer_source_field`: `Back`
- `answer_target_field`: `Back_jp`

Make sure your note type actually contains the target fields, otherwise the add-on will error.

---

### What to translate

- `translate_question`: True/False
- `translate_answer`: True/False

---

### Behavior / limits

- `max_chars_per_field` (default: `800`)  
  If a source field exceeds this length, that field is **skipped** (not translated).  
  This prevents huge prompts and accidental expensive runs.

- `temperature` (default: `0.1`)  
  Lower values are more literal/consistent.

- `batch_query_default` (default: `deck:current`)  
  Default query shown in the batch translation dialog.

---

### Tags

- `tag_translated` (default: `AI_Translated`)  
  Added to notes when translation is applied successfully.

- `tag_error` (default: `AI_TranslateError`)  
  Added to notes that fail during batch translation.

---

## Skip rules (important)

These options help prevent overwriting or re-translating notes:

- `skip_if_target_not_empty` (default: True)  
  If either target field already has content, the note is skipped.

- `skip_if_has_translated_tag` (default: True)  
  If the note already has `tag_translated`, it is skipped.

In batch mode, the add-on first filters notes with these rules, then asks for confirmation before sending anything to the AI.

---

## Output format and robustness

Both providers are instructed to return **JSON only**:

```json
{"question":"...","answer":"..."}
```

Because some models may wrap JSON in code fences, the add-on includes a small JSON-extraction helper that can strip ``` fences and pull out the `{...}` object.

---

## Troubleshooting

### “No notes matched the given search query.”
Your Anki search query returned zero results.

### “All matched notes are already translated or skipped by rules.”
Everything matched your skip conditions:
- already has `AI_Translated`, and/or
- target fields are not empty

### “Field 'X' does not exist in note type.”
Your `*_target_field` (or source field) doesn’t exist in the current note type.  
Update field mapping in config or add the missing field to your note type.

### Errors / rate limits
If the provider rejects requests (invalid key, quota, network issues):
- confirm your API key env var is correct
- try fewer notes per run
- try a different model/provider

Batch mode accumulates errors and shows them in one report at the end.

---

## Privacy

This add-on sends your note content (question and/or answer) to an external AI provider (OpenAI or Google Gemini) when enabled.

Do not translate sensitive or private content unless you understand and accept the provider’s data handling policies.

---

## License

See the LICENSE file in this repository.
