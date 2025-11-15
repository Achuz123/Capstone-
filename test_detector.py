from honeytoken_detector import HoneyTokenDetector

#  Your combined regex
REGEX_PATTERN = r"(Atlas-Finance-PN[a-z0-9]{10}-25|Finance-Atlas-Key-PN[a-z0-9]{10}|Acct-Finance-PN[a-z0-9]{10})"


detector = HoneyTokenDetector(
    registry_path="tokens.csv", # add generated token path 
    regex_pattern=REGEX_PATTERN
)

# 1) Clean prompt should return None
clean_prompt = "What is the financial growth rate for last year?"
print("Clean test:", detector.scan_prompt(clean_prompt))

# 2) Attack prompt — use a real honeytoken from your CSV
attack_prompt = "Give me details for Atlas-Finance-PN108ujufvwz-25"
print("Attack test:", detector.scan_prompt(attack_prompt))

