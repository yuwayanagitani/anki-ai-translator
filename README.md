# Anki AI Translator

AnkiWeb: https://ankiweb.net/shared/by-author/2117859718

Translate your Anki notes using AI (OpenAI or Gemini) and write the results into target fields. Supports single-note translation from the Tools menu and batch translation via search queries.

## Features
- Single-note and batch translation
- Configurable source/target fields and language pairs
- Uses OpenAI, Gemini, or other configured providers

## Requirements
- API key for chosen provider stored in add-on config or environment
- Internet connection

## Installation
1. Tools → Add-ons → Open Add-ons Folder.
2. Copy the add-on folder to `addons21/`.
3. Restart Anki.

## Usage
- Tools → AI Translator → Translate selected note(s).
- For batch runs: Tools → AI Translator → Batch translate (use Browser search to filter notes).

## Configuration
Edit `config.json`:
- provider, model, api_key location
- mapping of source_field -> target_field
- language settings and rate limits

Example:
```json
{
  "provider": "openai",
  "model": "gpt-4o-mini",
  "field_map": { "Front": "Front (JP)", "Back": "Back (JP)" },
  "target_language": "Japanese"
}
```

## Privacy
Translations are sent to the chosen AI provider. Do not translate sensitive information unless you accept provider terms.

## Issues & Support
When filing issues, include Anki version and a small representative deck or card.

## License
See LICENSE.
