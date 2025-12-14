# AI Translator for Anki

Translate your Anki notes using AI (OpenAI or Gemini) and write the results into target fields. This add-on supports both single-note translation (from the Tools menu) and batch translation using a search query.

## Features
- Translate one or many notes using AI.
- Write translated text into configurable target fields.
- Supports single-note and batch translation modes.
- Optionally preserve original text and store translations in separate fields.

## Requirements
- Anki 2.1+
- API key for chosen AI provider (OpenAI, Google Gemini) or local translation approach.

## Installation
1. Clone/download the repository.
2. Place the add-on folder into Anki’s add-ons folder.
3. Restart Anki.

## Usage
- Open Browser, select one note or run a search to select multiple notes.
- From the add-on menu, choose “Translate Selected Notes”.
- Configure source and target fields, source and target languages, and run.

## Configuration
Example configuration:
```json
{
  "provider": "openai",
  "source_field": "Front",
  "target_field": "Front (EN)",
  "source_lang": "auto",
  "target_lang": "en"
}
```

Batch mode:
- Use Anki search queries to restrict which notes should be translated.
- The add-on processes notes and writes translations to the configured target fields.

## Privacy & Costs
- Translations are sent to the configured AI provider. Ensure that sending note content is acceptable from a privacy and policy standpoint.

## Troubleshooting
- If translations are not written, check field names and note type consistency.
- If you hit provider rate limits or quotas, throttle batch sizes or split tasks.

## Development
- PRs and issues welcome. Include a sample note for reproducible bugs.

## License
MIT License — see LICENSE file.

## Contact
Author: yuwayanagitani
