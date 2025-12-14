# AI Card Translator – Configuration Guide

This document explains all configuration options available in `config.json` for the **AI Card Translator** add-on.

> You can open this config from:  
> `Tools → Add-ons → ai_card_translator → Config`

---

## 1. Provider selection

```jsonc
"provider": "openai"
```

- `"openai"` → Use OpenAI Chat Completions API.
- `"gemini"` → Use Google Gemini API.
- This only switches which backend is used. All other settings are interpreted accordingly.

---

## 2. OpenAI settings

```jsonc
"openai_model": "gpt-4o-mini",
"openai_api_base": "https://api.openai.com/v1/chat/completions",
"openai_api_key_env": "OPENAI_API_KEY"
```

- **`openai_model`**  
  Model name used with the Chat Completions API.  
  Examples: `"gpt-4o-mini"`, `"gpt-4o"`, `"gpt-4.1-mini"`.

- **`openai_api_base`**  
  Base URL for the Chat Completions endpoint.  
  Normally keep the default.

- **`openai_api_key_env`**  
  Name of the *environment variable* that stores your OpenAI API key.  
  - Default: `OPENAI_API_KEY`  
  - On Windows (PowerShell):  
    ```powershell
    setx OPENAI_API_KEY "sk-..."
    ```

---

## 3. Gemini settings

```jsonc
"gemini_model": "gemini-2.5-flash-lite",
"gemini_api_base": "https://generativelanguage.googleapis.com/v1",
"gemini_api_key_env": "GEMINI_API_KEY"
```

- **`gemini_model`**  
  Model name for Gemini. Recommended:  
  - `"gemini-2.5-flash-lite"` – best cost-performance for translation.  
  - `"gemini-2.5-flash"` – higher quality, more expensive.

- **`gemini_api_base`**  
  Base URL for the Gemini REST API.  
  Normally keep:  
  ```text
  https://generativelanguage.googleapis.com/v1
  ```

- **`gemini_api_key_env`**  
  Name of the environment variable that stores your Gemini API key.  
  Default: `GEMINI_API_KEY`.

---

## 4. Language settings

```jsonc
"source_language": "English",
"target_language": "Japanese"
```

- **`source_language`**  
  Human-readable description of your original card language.  
  Used inside the prompt (not for automatic detection).

- **`target_language`**  
  Target language for translation.  
  Examples: `"Japanese"`, `"English"`, `"German"`.

These values are used to tell the model *how* to translate, but they do not need to be exact language codes.

---

## 5. Field mapping

```jsonc
"question_source_field": "Front",
"question_target_field": "Front_jp",
"answer_source_field": "Back",
"answer_target_field": "Back_jp"
```

- **`question_source_field`**  
  Name of the field that contains the original question (e.g. `"Front"`).

- **`question_target_field`**  
  Field to store the translated question (e.g. `"Front_jp"`).  
  - Must exist in the note type.  
  - Leave empty (`""`) if you do not want to translate questions.

- **`answer_source_field`**  
  Field that contains the original answer (e.g. `"Back"`).

- **`answer_target_field`**  
  Field to store the translated answer (e.g. `"Back_jp"`).  
  - Must exist in the note type.  
  - Leave empty (`""`) if you do not want to translate answers.

> ⚠ If a target field does not exist in a note type, that note will raise an error for that field.

---

## 6. What to translate

```jsonc
"translate_question": true,
"translate_answer": true
```

- **`translate_question`**  
  - `true` → Send the question field to the AI and write the translation into `question_target_field`.  
  - `false` → Do not translate questions at all.

- **`translate_answer`**  
  - `true` → Translate the answer field.  
  - `false` → Do not translate answers.

You can combine these, e.g. only translate answers, or only questions.

---

## 7. Behaviour and limits

```jsonc
"max_chars_per_field": 800,
"temperature": 0.1,
"batch_query_default": "deck:current"
```

- **`max_chars_per_field`**  
  Maximum number of characters per field that will be sent to the API.  
  - If the original field length exceeds this value, that field will be **skipped** for translation.  
  - This is primarily for cost control and to avoid huge prompts.

- **`temperature`**  
  Controls randomness/creativity in the model.  
  - Recommended range for translation: `0.0`–`0.3`.  
  - Higher values → more creative but less consistent translations.

- **`batch_query_default`**  
  Default search query for the **Tools → Translate Cards with AI** dialog.  
  - Example: `"deck:current"` (current deck)  
  - You can change this to limit translation to specific tags, decks, or note types.  
    Example: `"deck:Renal tag:en"`.

---

## 8. Tags

```jsonc
"tag_translated": "AI_Translated",
"tag_error": "AI_TranslateError"
```

- **`tag_translated`**  
  Tag automatically added to notes that were successfully translated.  
  - Used by skip rules (see below).  
  - You can search later with `tag:AI_Translated`.

- **`tag_error`**  
  Tag added to notes that failed during translation (e.g. network error, JSON parse error).  
  - You can search later with `tag:AI_TranslateError` to retry only failed notes.

---

## 9. Skip rules

```jsonc
"skip_if_target_not_empty": true,
"skip_if_has_translated_tag": true
```

- **`skip_if_target_not_empty`**  
  - `true` → If the target field already contains any non-empty text, the note is skipped.  
  - This prevents overwriting manual translations.

- **`skip_if_has_translated_tag`**  
  - `true` → If the note already has `tag_translated` (e.g. `"AI_Translated"`), it will be skipped.  
  - Useful to avoid re-sending already-translated notes.

If you want to force re-translation, you can:

1. Remove the translated tag from the note(s), and/or  
2. Clear the target field(s).

---

## 10. Recommended minimal setup

For a typical “English → Japanese” translation deck:

```jsonc
{
  "provider": "openai",

  "openai_model": "gpt-4o-mini",
  "openai_api_base": "https://api.openai.com/v1/chat/completions",
  "openai_api_key_env": "OPENAI_API_KEY",

  "gemini_model": "gemini-2.5-flash-lite",
  "gemini_api_base": "https://generativelanguage.googleapis.com/v1",
  "gemini_api_key_env": "GEMINI_API_KEY",

  "source_language": "English",
  "target_language": "Japanese",

  "question_source_field": "Front",
  "question_target_field": "Front_jp",
  "answer_source_field": "Back",
  "answer_target_field": "Back_jp",

  "translate_question": true,
  "translate_answer": true,

  "max_chars_per_field": 800,
  "temperature": 0.1,
  "batch_query_default": "deck:current",

  "tag_translated": "AI_Translated",
  "tag_error": "AI_TranslateError",

  "skip_if_target_not_empty": true,
  "skip_if_has_translated_tag": true
}
```

You can adjust **fields, languages, and model** as needed, but the above is a safe default to start with.
