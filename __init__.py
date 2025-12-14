from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from aqt import mw, gui_hooks
from aqt.qt import (
    QAction,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QEventLoop,
    QInputDialog,
    QMessageBox,
    QKeySequence,
    QShortcut,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QScrollArea,
    QSizePolicy,
    QWidget,
)
from anki.notes import Note

# --- Qt Network imports (prefer Qt6, fall back to Qt5, else None) ---
try:
    # Anki 25 は PyQt6 ベース
    from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest  # type: ignore
    from PyQt6.QtCore import QUrl  # type: ignore
except Exception:
    try:
        from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest  # type: ignore
        from PyQt5.QtCore import QUrl  # type: ignore
    except Exception:
        QNetworkAccessManager = None  # type: ignore
        QNetworkRequest = None  # type: ignore
        QUrl = None  # type: ignore


# ========== Config ==========

DEFAULT_CONFIG: Dict[str, Any] = {
    # which provider to use: "openai" or "gemini"
    "provider": "openai",

    # OpenAI settings
    "openai_model": "gpt-4o-mini",
    "openai_api_base": "https://api.openai.com/v1/chat/completions",
    "openai_api_key_env": "OPENAI_API_KEY",

    # Gemini settings
    # base は v1 / v1beta どちらでも可（models/{model}:generateContent を結合）
    "gemini_model": "gemini-2.5-flash-lite",
    "gemini_api_base": "https://generativelanguage.googleapis.com/v1",
    "gemini_api_key_env": "GEMINI_API_KEY",

    # Languages
    "source_language": "English",
    "target_language": "Japanese",

    # Field mapping
    "question_source_field": "Front",
    "question_target_field": "Front_jp",
    "answer_source_field": "Back",
    "answer_target_field": "Back_jp",

    # What to translate
    "translate_question": True,
    "translate_answer": True,

    # Behaviour
    "max_chars_per_field": 800,  # これを超えたフィールドは翻訳しない（スキップ）
    "temperature": 0.1,
    "batch_query_default": "deck:current",

    # Tags
    "tag_translated": "AI_Translated",
    "tag_error": "AI_TranslateError",

    # Skip rules
    "skip_if_target_not_empty": True,
    "skip_if_has_translated_tag": True,
}


def get_config() -> Dict[str, Any]:
    conf = mw.addonManager.getConfig(__name__) or {}
    merged = DEFAULT_CONFIG.copy()
    merged.update(conf)
    return merged


def save_config(conf: Dict[str, Any]) -> None:
    mw.addonManager.writeConfig(__name__, conf)


# ========== Common helpers ==========

def show_error_dialog(msg: str) -> None:
    QMessageBox.critical(
        mw,
        "AI Card Translator - Error",
        msg,
    )


class ConfigDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AI Card Translator - Settings")
        self.setMinimumWidth(620)

        conf = get_config()

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ★ スクロール領域（中身）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        scroll.setWidget(content)

        # root にはまずスクロール領域を乗せる（伸びるのはここ）
        root.addWidget(scroll, 1)

        # --- Provider ---
        box_provider = QGroupBox("Provider")
        box_provider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_provider = QFormLayout(box_provider)
        form_provider.setVerticalSpacing(10)

        self.provider = QComboBox()
        self.provider.addItems(["openai", "gemini"])
        self.provider.setCurrentText((conf.get("provider") or "openai").lower())
        form_provider.addRow("provider", self.provider)

        content_layout.addWidget(box_provider)

        # --- OpenAI ---
        box_openai = QGroupBox("OpenAI")
        box_openai.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_openai = QFormLayout(box_openai)
        form_openai.setVerticalSpacing(10)

        self.openai_model = QLineEdit(str(conf.get("openai_model", "")))
        self.openai_api_base = QLineEdit(str(conf.get("openai_api_base", "")))
        self.openai_api_key_env = QLineEdit(str(conf.get("openai_api_key_env", "")))

        form_openai.addRow("model", self.openai_model)
        form_openai.addRow("api base", self.openai_api_base)
        form_openai.addRow("api key env", self.openai_api_key_env)

        content_layout.addWidget(box_openai)

        # --- Gemini ---
        box_gemini = QGroupBox("Gemini")
        box_gemini.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_gemini = QFormLayout(box_gemini)
        form_gemini.setVerticalSpacing(10)

        self.gemini_model = QLineEdit(str(conf.get("gemini_model", "")))
        self.gemini_api_base = QLineEdit(str(conf.get("gemini_api_base", "")))
        self.gemini_api_key_env = QLineEdit(str(conf.get("gemini_api_key_env", "")))

        form_gemini.addRow("model", self.gemini_model)
        form_gemini.addRow("api base", self.gemini_api_base)
        form_gemini.addRow("api key env", self.gemini_api_key_env)

        content_layout.addWidget(box_gemini)

        # --- Languages ---
        box_lang = QGroupBox("Languages")
        box_lang.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_lang = QFormLayout(box_lang)
        form_lang.setVerticalSpacing(10)

        self.source_language = QLineEdit(str(conf.get("source_language", "")))
        self.target_language = QLineEdit(str(conf.get("target_language", "")))
        form_lang.addRow("source", self.source_language)
        form_lang.addRow("target", self.target_language)

        content_layout.addWidget(box_lang)

        # --- Field mapping ---
        box_fields = QGroupBox("Field mapping")
        box_fields.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_fields = QFormLayout(box_fields)
        form_fields.setVerticalSpacing(10)

        self.question_source_field = QLineEdit(str(conf.get("question_source_field", "")))
        self.question_target_field = QLineEdit(str(conf.get("question_target_field", "")))
        self.answer_source_field = QLineEdit(str(conf.get("answer_source_field", "")))
        self.answer_target_field = QLineEdit(str(conf.get("answer_target_field", "")))

        form_fields.addRow("question source field", self.question_source_field)
        form_fields.addRow("question target field", self.question_target_field)
        form_fields.addRow("answer source field", self.answer_source_field)
        form_fields.addRow("answer target field", self.answer_target_field)

        content_layout.addWidget(box_fields)

        # --- What to translate / skip rules ---
        box_rules = QGroupBox("Options")
        box_rules.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_rules = QFormLayout(box_rules)
        form_rules.setVerticalSpacing(10)

        self.translate_question = QCheckBox("translate question")
        self.translate_question.setChecked(bool(conf.get("translate_question", True)))
        self.translate_answer = QCheckBox("translate answer")
        self.translate_answer.setChecked(bool(conf.get("translate_answer", True)))

        self.skip_if_target_not_empty = QCheckBox("skip if target field not empty")
        self.skip_if_target_not_empty.setChecked(bool(conf.get("skip_if_target_not_empty", True)))
        self.skip_if_has_translated_tag = QCheckBox("skip if already has translated tag")
        self.skip_if_has_translated_tag.setChecked(bool(conf.get("skip_if_has_translated_tag", True)))

        form_rules.addRow(self.translate_question)
        form_rules.addRow(self.translate_answer)
        form_rules.addRow(self.skip_if_target_not_empty)
        form_rules.addRow(self.skip_if_has_translated_tag)

        content_layout.addWidget(box_rules)

        # --- Behaviour / tags ---
        box_misc = QGroupBox("Behaviour / Tags")
        box_misc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_misc = QFormLayout(box_misc)
        form_misc.setVerticalSpacing(10)

        self.max_chars_per_field = QSpinBox()
        self.max_chars_per_field.setRange(0, 20000)
        self.max_chars_per_field.setValue(int(conf.get("max_chars_per_field", 800)))

        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.0, 2.0)
        self.temperature.setSingleStep(0.05)
        self.temperature.setDecimals(2)
        self.temperature.setValue(float(conf.get("temperature", 0.1)))

        self.batch_query_default = QLineEdit(str(conf.get("batch_query_default", "deck:current")))
        self.tag_translated = QLineEdit(str(conf.get("tag_translated", "")))
        self.tag_error = QLineEdit(str(conf.get("tag_error", "")))

        form_misc.addRow("max chars per field (skip if over)", self.max_chars_per_field)
        form_misc.addRow("temperature", self.temperature)
        form_misc.addRow("default batch query", self.batch_query_default)
        form_misc.addRow("tag: translated", self.tag_translated)
        form_misc.addRow("tag: error", self.tag_error)

        content_layout.addWidget(box_misc)

        # ★ 余った縦スペースはここで吸わせる（潰れを防ぐ）
        content_layout.addStretch(1)

        # --- footer ---
        footer = QHBoxLayout()
        footer.setSpacing(8)

        self.btn_reset = QPushButton("Reset to defaults")
        self.btn_reset.clicked.connect(self._reset_to_defaults)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        footer.addWidget(self.btn_reset)
        footer.addStretch(1)
        footer.addWidget(self.buttons)

        root.addLayout(footer)

        note = QLabel("Tip: API keys are read from environment variables (OpenAI/Gemini).")
        note.setWordWrap(True)
        root.addWidget(note)

    def _reset_to_defaults(self) -> None:
        conf = DEFAULT_CONFIG.copy()
        self.provider.setCurrentText((conf.get("provider") or "openai").lower())
        self.openai_model.setText(str(conf.get("openai_model", "")))
        self.openai_api_base.setText(str(conf.get("openai_api_base", "")))
        self.openai_api_key_env.setText(str(conf.get("openai_api_key_env", "")))
        self.gemini_model.setText(str(conf.get("gemini_model", "")))
        self.gemini_api_base.setText(str(conf.get("gemini_api_base", "")))
        self.gemini_api_key_env.setText(str(conf.get("gemini_api_key_env", "")))
        self.source_language.setText(str(conf.get("source_language", "")))
        self.target_language.setText(str(conf.get("target_language", "")))
        self.question_source_field.setText(str(conf.get("question_source_field", "")))
        self.question_target_field.setText(str(conf.get("question_target_field", "")))
        self.answer_source_field.setText(str(conf.get("answer_source_field", "")))
        self.answer_target_field.setText(str(conf.get("answer_target_field", "")))
        self.translate_question.setChecked(bool(conf.get("translate_question", True)))
        self.translate_answer.setChecked(bool(conf.get("translate_answer", True)))
        self.skip_if_target_not_empty.setChecked(bool(conf.get("skip_if_target_not_empty", True)))
        self.skip_if_has_translated_tag.setChecked(bool(conf.get("skip_if_has_translated_tag", True)))
        self.max_chars_per_field.setValue(int(conf.get("max_chars_per_field", 800)))
        self.temperature.setValue(float(conf.get("temperature", 0.1)))
        self.batch_query_default.setText(str(conf.get("batch_query_default", "deck:current")))
        self.tag_translated.setText(str(conf.get("tag_translated", "")))
        self.tag_error.setText(str(conf.get("tag_error", "")))

    def get_values(self) -> Dict[str, Any]:
        # DEFAULT_CONFIG と同じキーで保存（互換性維持）
        return {
            "provider": self.provider.currentText().strip().lower() or "openai",
            "openai_model": self.openai_model.text().strip(),
            "openai_api_base": self.openai_api_base.text().strip(),
            "openai_api_key_env": self.openai_api_key_env.text().strip(),
            "gemini_model": self.gemini_model.text().strip(),
            "gemini_api_base": self.gemini_api_base.text().strip(),
            "gemini_api_key_env": self.gemini_api_key_env.text().strip(),
            "source_language": self.source_language.text().strip(),
            "target_language": self.target_language.text().strip(),
            "question_source_field": self.question_source_field.text().strip(),
            "question_target_field": self.question_target_field.text().strip(),
            "answer_source_field": self.answer_source_field.text().strip(),
            "answer_target_field": self.answer_target_field.text().strip(),
            "translate_question": bool(self.translate_question.isChecked()),
            "translate_answer": bool(self.translate_answer.isChecked()),
            "max_chars_per_field": int(self.max_chars_per_field.value()),
            "temperature": float(self.temperature.value()),
            "batch_query_default": self.batch_query_default.text().strip() or "deck:current",
            "tag_translated": self.tag_translated.text().strip(),
            "tag_error": self.tag_error.text().strip(),
            "skip_if_target_not_empty": bool(self.skip_if_target_not_empty.isChecked()),
            "skip_if_has_translated_tag": bool(self.skip_if_has_translated_tag.isChecked()),
        }


def open_settings_dialog() -> None:
    dlg = ConfigDialog(mw)
    res = dlg.exec()

    accepted = False
    if hasattr(QDialog, "DialogCode"):
        accepted = (res == QDialog.DialogCode.Accepted)
    else:
        accepted = (res == QDialog.Accepted)

    if accepted:
        new_conf = DEFAULT_CONFIG.copy()
        new_conf.update(dlg.get_values())
        save_config(new_conf)
        QMessageBox.information(mw, "AI Card Translator", "Settings saved.")



def _post_json(
    url: str,
    headers: Dict[str, str],
    data_bytes: bytes,
    prefer_qt: bool = True,
) -> bytes:
    """
    POST JSON to `url` and return raw response bytes.

    Qt の QNetworkAccessManager が使える場合は Qt 経由、
    そうでない場合は urllib でフォールバックする。
    """

    # ---- Qt Network 経由（あればこちらを優先） ----
    if (
        prefer_qt
        and QNetworkAccessManager is not None
        and QNetworkRequest is not None
        and QUrl is not None
    ):
        manager = QNetworkAccessManager(mw)
        req = QNetworkRequest(QUrl(url))

        for key, value in headers.items():
            req.setRawHeader(key.encode("utf-8"), value.encode("utf-8"))

        reply = manager.post(req, data_bytes)
        loop = QEventLoop()

        def on_finished() -> None:
            loop.quit()

        reply.finished.connect(on_finished)
        loop.exec()

        resp_bytes = bytes(reply.readAll())

        # Qt がエラーを返していても、レスポンスボディがあればそれを優先して使う。
        # （Gemini が 200 を返しているのに Qt 側が Unknown error を出すケースがある）
        if reply.error() and not resp_bytes:
            body_text = resp_bytes.decode("utf-8", "ignore")
            raise RuntimeError(
                f"Network error (Qt): {reply.errorString()}\n{body_text}"
            )

        return resp_bytes

    # ---- フォールバック：urllib 経由 ----
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        raise RuntimeError(f"HTTP error (urllib): {e.code}\n{detail}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connection failed (urllib): {e}") from None
    except Exception as e:
        raise RuntimeError(f"Unexpected error (urllib): {e}") from None



def _extract_json_from_text(text: str) -> str:
    """Extract JSON object from text that may contain extra text or ``` fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
            text = "\n".join(lines[1:-1]).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


@dataclass
class TranslationResult:
    question: Optional[str]
    answer: Optional[str]


# ========== Provider-specific translation ==========

def _get_env(key_name: str) -> str:
    value = os.environ.get(key_name, "")
    if not value:
        raise RuntimeError(
            f"Environment variable '{key_name}' is not set."
        )
    return value


def call_openai_translate(
    question: Optional[str],
    answer: Optional[str],
    config: Dict[str, Any],
) -> TranslationResult:
    api_key = _get_env(config["openai_api_key_env"])
    model = config["openai_model"]
    api_base = config["openai_api_base"]
    src_lang = config["source_language"]
    tgt_lang = config["target_language"]
    temperature = float(config.get("temperature", 0.1))

    parts: List[str] = []
    parts.append(f"Source language: {src_lang}")
    parts.append(f"Target language: {tgt_lang}")
    parts.append("Translate the following Anki card fields.")
    parts.append("Return ONLY JSON, no extra text, in this format:")
    parts.append('{"question": "...", "answer": "..."}')
    parts.append("")
    if question is not None:
        parts.append("Original QUESTION:")
        parts.append(question)
        parts.append("")
    if answer is not None:
        parts.append("Original ANSWER:")
        parts.append(answer)

    user_prompt = "\n".join(parts)

    system_prompt = (
        "You are a precise bilingual translator for Anki flashcards. "
        "Preserve technical and medical terminology. "
        "Use plain text only (no markdown or HTML)."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }

    data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    resp_bytes = _post_json(api_base, headers, data_bytes, prefer_qt=True)

    try:
        resp_data = json.loads(resp_bytes.decode("utf-8"))
        content = resp_data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(
            f"Failed to parse OpenAI response JSON: {e}\nraw={resp_bytes[:500]!r}"
        ) from None

    if not content:
        raise RuntimeError("OpenAI response was empty.")

    text = _extract_json_from_text(content)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Failed to parse JSON in OpenAI response: {e}\ncontent={content[:500]!r}"
        ) from None

    q = data.get("question")
    a = data.get("answer")
    return TranslationResult(
        question=str(q).strip() if q is not None else None,
        answer=str(a).strip() if a is not None else None,
    )


def call_gemini_translate(
    question: Optional[str],
    answer: Optional[str],
    config: Dict[str, Any],
) -> TranslationResult:
    api_key = _get_env(config["gemini_api_key_env"])
    model = config["gemini_model"]
    base = config["gemini_api_base"].rstrip("/")
    src_lang = config["source_language"]
    tgt_lang = config["target_language"]
    temperature = float(config.get("temperature", 0.1))

    # v1: https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key=...
    url = f"{base}/models/{model}:generateContent?key={api_key}"

    parts: List[str] = []
    parts.append(f"Source language: {src_lang}")
    parts.append(f"Target language: {tgt_lang}")
    parts.append("Translate the following Anki card fields.")
    parts.append("Return ONLY a JSON object in this format:")
    parts.append('{"question": "...", "answer": "..."}')
    parts.append("No extra commentary, no markdown, no HTML.")
    parts.append("")
    if question is not None:
        parts.append("Original QUESTION:")
        parts.append(question)
        parts.append("")
    if answer is not None:
        parts.append("Original ANSWER:")
        parts.append(answer)

    prompt = "\n".join(parts)

    # ★ ここがポイント：余計な response_* 系フィールドは一切入れない
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": temperature,
        },
    }

    data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
    }

    resp_bytes = _post_json(url, headers, data_bytes, prefer_qt=True)

    try:
        resp_data = json.loads(resp_bytes.decode("utf-8"))
        candidates = resp_data.get("candidates") or []
        if not candidates:
            raise RuntimeError("No candidates in Gemini response.")
        parts_out = candidates[0].get("content", {}).get("parts") or []
        if not parts_out:
            raise RuntimeError("No content parts in Gemini response.")
        content = parts_out[0].get("text", "")
    except Exception as e:
        raise RuntimeError(
            f"Failed to parse Gemini response JSON: {e}\nraw={resp_bytes[:500]!r}"
        ) from None

    if not content:
        raise RuntimeError("Gemini response was empty.")

    text = _extract_json_from_text(content)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Failed to parse JSON in Gemini response: {e}\ncontent={content[:500]!r}"
        ) from None

    q = data.get("question")
    a = data.get("answer")
    return TranslationResult(
        question=str(q).strip() if q is not None else None,
        answer=str(a).strip() if a is not None else None,
    )


def call_provider_translate(
    question: Optional[str],
    answer: Optional[str],
    config: Dict[str, Any],
) -> TranslationResult:
    provider = (config.get("provider") or "openai").lower()
    if provider == "gemini":
        return call_gemini_translate(question, answer, config)
    # default: openai
    return call_openai_translate(question, answer, config)


# ========== Note-level logic ==========

def _get_field(note: Note, field_name: str) -> Optional[str]:
    if not field_name:
        return None
    if field_name not in note:
        return None
    return note[field_name]


def _set_field(note: Note, field_name: str, value: Optional[str]) -> None:
    if value is None or not field_name:
        return
    if field_name not in note:
        raise RuntimeError(f"Field '{field_name}' does not exist in note type.")
    note[field_name] = value


def should_skip_note(note: Note, config: Dict[str, Any]) -> bool:
    tag_translated = config["tag_translated"]
    skip_if_target_not_empty = bool(config.get("skip_if_target_not_empty", True))
    skip_if_has_translated_tag = bool(config.get("skip_if_has_translated_tag", True))

    if skip_if_has_translated_tag and tag_translated in note.tags:
        return True

    if skip_if_target_not_empty:
        q_tgt = config["question_target_field"]
        a_tgt = config["answer_target_field"]
        if q_tgt and q_tgt in note and note[q_tgt].strip():
            return True
        if a_tgt and a_tgt in note and note[a_tgt].strip():
            return True

    return False


def translate_note(note: Note, config: Dict[str, Any]) -> bool:
    """
    Translate fields of a single note.
    Returns True if translation was applied, False if skipped.
    Raises on fatal errors.
    """
    if should_skip_note(note, config):
        return False

    translate_question = bool(config.get("translate_question", True))
    translate_answer = bool(config.get("translate_answer", True))
    max_chars = int(config.get("max_chars_per_field", 800))

    q_src_name = config["question_source_field"]
    q_tgt_name = config["question_target_field"]
    a_src_name = config["answer_source_field"]
    a_tgt_name = config["answer_target_field"]

    q_src_text: Optional[str] = None
    a_src_text: Optional[str] = None

    # max_chars_per_field を超える場合はそのフィールドは翻訳しない
    if translate_question and q_src_name and q_src_name in note:
        full = note[q_src_name]
        if len(full) > max_chars:
            q_src_text = None
        else:
            q_src_text = full

    if translate_answer and a_src_name and a_src_name in note:
        full = note[a_src_name]
        if len(full) > max_chars:
            a_src_text = None
        else:
            a_src_text = full

    # 両方とも翻訳対象なしならスキップ
    if q_src_text is None and a_src_text is None:
        return False

    result = call_provider_translate(q_src_text, a_src_text, config)

    # apply results
    if translate_question and result.question is not None:
        _set_field(note, q_tgt_name, result.question)
    if translate_answer and result.answer is not None:
        _set_field(note, a_tgt_name, result.answer)

    # tag note
    tag_translated = config["tag_translated"]
    if tag_translated not in note.tags:
        note.tags.append(tag_translated)

    note.flush()
    return True


# ========== Batch translation (Tools menu) ==========

def translate_batch_for_query() -> None:
    config = get_config()

    default_query = config.get("batch_query_default", "deck:current")
    query, ok = QInputDialog.getText(
        mw,
        "AI Card Translator",
        (
            "Enter the search query for the notes you want to translate.\n"
            "Example: deck:Renal tag:en"
        ),
        text=default_query,
    )
    if not ok or not query.strip():
        return

    note_ids = mw.col.find_notes(query.strip())
    if not note_ids:
        QMessageBox.information(
            mw,
            "AI Card Translator",
            "No notes matched the given search query.",
        )
        return

    total = len(note_ids)
    to_process: List[int] = []

    for nid in note_ids:
        note = mw.col.get_note(nid)
        if note is None:
            continue
        if should_skip_note(note, config):
            continue
        to_process.append(nid)

    if not to_process:
        QMessageBox.information(
            mw,
            "AI Card Translator",
            "All matched notes are already translated or skipped by rules.",
        )
        return

    if (
        QMessageBox.question(
            mw,
            "Confirm",
            f"{total} notes matched the search query.\n"
            f"{len(to_process)} notes will be sent for translation.\n\n"
            "Proceed?",
        )
        != QMessageBox.StandardButton.Yes
    ):
        return

    tag_error = config["tag_error"]
    translated_count = 0
    skipped_count = total - len(to_process)
    error_count = 0
    errors = []  # ← エラー蓄積用


    mw.progress.start(
        max=len(to_process),
        label="Translating cards with AI...",
    )

    try:
        for i, nid in enumerate(to_process, 1):
            mw.progress.update(
                label=f"Translating note {i}/{len(to_process)}...",
                value=i,
            )
            note = mw.col.get_note(nid)
            if note is None:
                continue

            try:
                changed = translate_note(note, config)
            except Exception as e:
                error_count += 1
                if tag_error and tag_error not in note.tags:
                    note.tags.append(tag_error)
                    note.flush()
                # ★ エラーは表示せず蓄積する
                errors.append(f"Note {nid}: {e}")
                continue

            if changed:
                translated_count += 1
            else:
                skipped_count += 1

    finally:
        mw.progress.finish()

    mw.col.save()
    mw.reset()

    msg = (
        "Finished translating notes.\n\n"
        f"Translated: {translated_count}\n"
        f"Skipped by rules: {skipped_count}\n"
        f"Errors: {error_count}"
    )
    QMessageBox.information(
        mw,
        "AI Card Translator",
        msg,
    )

    # ★ エラーまとめ表示
    if errors:
        err_text = "\n\n".join(errors)
        QMessageBox.critical(
            mw,
            "Translation Errors",
            f"Some notes failed during translation:\n\n{err_text}",
        )



# ========== Reviewer hotkey (single-card translate) ==========

def translate_current_card(reviewer) -> None:
    """Translate the current card's note from the Reviewer."""
    config = get_config()
    card = getattr(reviewer, "card", None)
    if card is None:
        return
    note = card.note()
    try:
        changed = translate_note(note, config)
    except Exception as e:
        show_error_dialog(f"Error while translating current note:\n\n{str(e)}")
        return

    if changed:
        mw.reset()
        QMessageBox.information(
            mw,
            "AI Card Translator",
            "Translation applied to the current note.",
        )
    else:
        QMessageBox.information(
            mw,
            "AI Card Translator",
            "Nothing to translate for this note (skipped by rules).",
        )


def on_reviewer_did_init(reviewer) -> None:
    """Add a shortcut (Ctrl+Shift+T) to translate the current card."""
    # In newer Anki versions, Reviewer has no .window(), but has .mw
    parent = getattr(reviewer, "mw", mw)

    shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), parent)
    shortcut.activated.connect(lambda: translate_current_card(reviewer))

    # Keep reference to avoid garbage collection
    reviewer._ai_card_translator_shortcut = shortcut


# ========== Menu registration ==========

def on_profile_did_open() -> None:
    action = QAction("Translate Cards with AI", mw)
    action.triggered.connect(translate_batch_for_query)
    mw.form.menuTools.addAction(action)

    # Add-ons screen "Config" button -> open our custom dialog
    try:
        mw.addonManager.setConfigAction(__name__, open_settings_dialog)
    except Exception:
        # older Anki: ignore
        pass
 

gui_hooks.profile_did_open.append(on_profile_did_open)
gui_hooks.reviewer_did_init.append(on_reviewer_did_init)
