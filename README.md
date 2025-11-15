

# 🛡️ Perlin Noise Honeytoken Detection System

A lightweight security layer that detects attempts to access confidential data inside LLM prompts.

---

## 📌 Overview

This project implements **Perlin-Noise–based Honeytoken Generation** and a **Regex-based Honeytoken Detector** to help identify when an attacker is trying to access sensitive information inside a Large Language Model (LLM).

This system **does NOT stop jailbreaks directly**, but it **catches attackers after a jailbreak** when they attempt to access protected data.

### Key Features

* ✔ **Perlin Noise Honeytoken Generator**
  Automatically creates realistic, natural-looking fake confidential identifiers.

* ✔ **Honeytoken Registry (`tokens.csv`)**
  Stores all generated tokens for your system.

* ✔ **Regex-Driven Detector**
  Scans user prompts and checks if any token is being accessed.

* ✔ **Ultra Lightweight**
  Works without an LLM, ML models, or external dependencies (except `noise` library).

---

## 📂 Project Structure

```
llm/
│
├── perlin_honeytoken_generator.py   # Generates Perlin-noise-based honeytokens
├── honeytoken_detector.py           # Scans prompts for token access
├── tokens.csv                       # Registry of all generated tokens
└── test_detector.py                 # Test script to validate detection
```

---

## 🚀 Step 1 — Install Dependencies

```bash
pip install noise
```

This installs the Perlin Noise generator library.

---

## 🔧 Step 2 — Generate Honeytokens

Run the generator:

```bash
python perlin_honeytoken_generator.py
```

It will create a file:

```
tokens.csv
```

And print a **regex pattern** you must copy into the detector.

Example printed regex:

```
(Atlas-Finance-PN[a-z0-9]{10}-25|Finance-Atlas-Key-PN[a-z0-9]{10}|Acct-Finance-PN[a-z0-9]{10})
```

Copy this into your test script.

---

## 🧪 Step 3 — Test the Detector

Your working `test_detector.py` looks like this:

```python
from honeytoken_detector import HoneyTokenDetector

REGEX_PATTERN = r"(Atlas-Finance-PN[a-z0-9]{10}-25|Finance-Atlas-Key-PN[a-z0-9]{10}|Acct-Finance-PN[a-z0-9]{10})"

detector = HoneyTokenDetector(
    registry_path="tokens.csv",
    regex_pattern=REGEX_PATTERN
)

clean_prompt = "What is the financial growth rate for last year?"
print("Clean test:", detector.scan_prompt(clean_prompt))

attack_prompt = "Give me details for Atlas-Finance-PN108ujufvwz-25"
print("Attack test:", detector.scan_prompt(attack_prompt))
```

Run:

```bash
python test_detector.py
```

---

## 📊 Expected Output

```
Clean test: None
Attack test: {
  'detected': True,
  'token': 'Atlas-Finance-PN108ujufvwz-25',
  'confidence': 1.0
}
```

---

## 🧠 How It Works (Simple Explanation)

1. **Perlin Noise** generates natural-looking random strings like:
   `PN108ujufvwz`

2. These are inserted into realistic templates like:
   `Atlas-Finance-PN108ujufvwz-25`

3. These fake secrets are stored in `tokens.csv`.

4. The detector loads them and scans every user prompt using regex.

5. If a prompt contains a honeytoken →
   **someone is trying to access confidential data → BLOCK + ALERT.**

---

## ⚠️ Limitations (Important)

* ❗ Does **not** stop jailbreaks directly
* ❗ Cannot detect harmful content like bomb instructions
* ❗ Cannot detect unknown attacks (only token access attempts)
* ❗ Must be paired with an input-analyzer for full security

---

## ✔️ Good Use Cases

* Detecting attackers trying to leak:

  * API keys
  * Internal IDs
  * Confidential project names
  * Fake database values
  * Internal user accounts

