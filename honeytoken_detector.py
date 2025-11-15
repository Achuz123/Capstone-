import re
import csv
from typing import List, Dict

class HoneyTokenDetector:
    def __init__(self, registry_path: str, regex_pattern: str):
        """
        registry_path → Path to tokens.csv generated earlier
        regex_pattern → Pattern printed by generator
        """
        self.registry = self._load_registry(registry_path)
        self.regex = re.compile(regex_pattern, re.IGNORECASE)

    def _load_registry(self, path: str) -> List[Dict]:
        entries = []
        with open(path, "r", encoding="utf8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append(row)
        return entries

    def scan_prompt(self, text: str):
        """
        Scan attacker prompt for honeytokens.
        Returns detection result or None.
        """
        match = self.regex.search(text)
        if not match:
            return None

        matched_token = match.group(0)

        # Find original entry from registry
        entry = next((e for e in self.registry if e["token"].lower() == matched_token.lower()), None)

        return {
            "detected": True,
            "token": matched_token,
            "registry_entry": entry,
        }

    def is_safe(self, text: str) -> bool:
        """Simple boolean check."""
        return self.scan_prompt(text) is None
