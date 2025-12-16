# AI Card Translator

**AI Card Translator** is an Anki add-on that allows you to **translate the currently displayed card instantly using AI**, directly from the Reviewer screen.  
It is designed for situations where you suddenly want to understand a card in another language *during review*, without breaking your learning flow.

---

## 🔗 AnkiWeb Page

This add-on is officially published on **AnkiWeb**:

👉 https://ankiweb.net/shared/info/728208605

Installing from AnkiWeb is recommended for the easiest setup and automatic updates.

---

## 🎯 Key Features

- 🌍 Translate the **currently reviewed card** with one action  
- 🧠 Uses AI for **context-aware, natural translations**  
- 🔁 Supports multiple providers:
  - OpenAI
  - Google Gemini  
- 🪶 Minimal UI — no interruption to review flow  
- 🧩 Works with any note type and any language pair  

---

## 🚀 How It Works

1. You are reviewing a card in Anki  
2. Trigger **AI Card Translator** from the Reviewer menu  
3. The card’s content is sent to the selected AI model  
4. The translated text is generated  
5. The translation is written back to the configured field

This makes it ideal for:
- Language learning  
- Translating medical / technical terms  
- Understanding foreign-language source material during review  

---

## 📦 Installation

### ✅ From AnkiWeb (Recommended)

1. Open Anki  
2. Go to **Tools → Add-Ons → Browse & Install**  
3. Search for **AI Card Translator**  
4. Install and restart Anki

### 📁 Manual Installation (GitHub)

1. Download or clone this repository  
2. Place it into:  
   `Anki2/addons21/anki-ai-translator`  
3. Restart Anki

---

## 🔑 API Key Setup

This add-on requires an API key for the selected provider.

| Provider | Environment Variable |
|--------|----------------------|
| OpenAI | `OPENAI_API_KEY` |
| Gemini | `GEMINI_API_KEY` |

API keys can be set via:
- System environment variables, or  
- The add-on’s configuration dialog

---

## ⚙️ Configuration

Open:

**Tools → Add-Ons → AI Card Translator → Config**

Main options include:

- AI provider selection (OpenAI / Gemini)  
- Model name  
- Source language (auto-detect supported)  
- Target language  
- Output field (where the translation is written)  
- Overwrite behavior (skip / append / replace)

---

## 🧪 Usage

### Translate the current card

While reviewing a card:

**More → AI Card Translator**

The translation is generated instantly and written to the specified field.

This allows you to:
- Translate only *when needed*  
- Keep original cards untouched  
- Add translations incrementally during normal review  

---

## ⚠️ Privacy Notes

Card contents are sent to external AI services.  
Avoid translating cards containing sensitive or personal information unless you understand the data handling policies of the selected provider.

---

## 🛠 Troubleshooting

| Problem | Solution |
|-------|----------|
| “No current card.” | Run from the Reviewer screen |
| Translation not written | Check output field name |
| API error | Verify API key and model |
| Unexpected language | Set target language explicitly |

---

## 📜 License

MIT License

---

## 🔧 Related Add-ons

- **AI Card Explainer** — Generate explanations for cards  
- **AI Card Splitter** — Split large cards into smaller ones  
- **HTML Exporter for Anki** — Export cards to HTML / PDF  

These add-ons are designed to work together as a modular, AI-powered Anki workflow.
