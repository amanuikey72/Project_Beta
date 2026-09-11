"""
model.py
--------
AI Complaint Prioritization Engine.

Uses NLP keyword analysis, weighted scoring, and multi-factor
urgency detection to assign a priority level and score to any complaint.

Usage:
    from model import predict_priority
    result = predict_priority(title, description)
    # returns: {"priority": "Critical", "score": 92, "category": "Safety"}
"""

import re
from collections import defaultdict

# ================================================================== #
#  KEYWORD DICTIONARIES WITH WEIGHTS
#  Each keyword maps to a base score contribution.
# ================================================================== #

CRITICAL_KEYWORDS = {
    # Life-threatening / emergency
    "fire": 35, "burning": 32, "explosion": 38, "blast": 36,
    "accident": 28, "fatal": 38, "death": 40, "died": 40, "dead": 38,
    "emergency": 35, "hospital emergency": 38, "ambulance": 30,
    "gas leak": 40, "gas leakage": 40, "lpg leak": 38,
    "electric shock": 36, "electrocution": 40, "electrocuted": 40,
    "violence": 32, "assault": 34, "attack": 30, "murder": 40,
    "life threatening": 40, "life-threatening": 40,
    "building collapse": 40, "structure collapse": 40, "collapse": 32,
    "flood": 28, "drowning": 38, "landslide": 36,
    "chemical spill": 36, "toxic": 30, "poisonous": 34,
    "bomb": 40, "terror": 38, "kidnap": 38,
    "unconscious": 36, "bleeding": 30, "injury": 22, "injured": 22,
    "critical": 30, "urgent": 22, "immediate": 20,
}

HIGH_KEYWORDS = {
    "water leakage": 22, "water leak": 22, "pipe burst": 24,
    "power failure": 20, "power outage": 20, "electricity failure": 22,
    "no power": 18, "blackout": 20,
    "sewage overflow": 24, "sewage": 18, "drainage block": 20,
    "road accident": 22, "major accident": 24,
    "major road damage": 20, "pothole": 14, "road damage": 16,
    "security issue": 20, "security threat": 22, "theft": 20,
    "robbery": 24, "break-in": 22, "trespassing": 18,
    "transformer": 18, "electrical fault": 20, "short circuit": 24,
    "tree fallen": 18, "tree fell": 18, "fallen tree": 18,
    "contaminated water": 24, "polluted water": 22,
    "disease outbreak": 28, "epidemic": 30,
    "dangerous": 18, "hazardous": 20, "severe": 16,
}

MEDIUM_KEYWORDS = {
    "garbage": 12, "waste": 10, "litter": 8, "dumping": 12,
    "street light": 10, "streetlight": 10, "light not working": 12,
    "water supply": 10, "no water": 14, "water shortage": 14,
    "noise complaint": 8, "noise": 6, "loud": 6, "nuisance": 8,
    "road maintenance": 10, "repair road": 10,
    "stray dog": 10, "stray animal": 10, "animal": 6,
    "overgrown": 8, "vegetation": 6,
    "public toilet": 8, "sanitation": 10,
    "parking": 6, "illegal parking": 10,
    "mosquito": 10, "pest": 10, "infestation": 14,
    "traffic signal": 10, "signal not working": 12,
    "construction": 8, "dust": 6, "air quality": 10,
    "blocked road": 14, "encroachment": 12,
}

LOW_KEYWORDS = {
    "general inquiry": 4, "inquiry": 2, "question": 2,
    "minor issue": 4, "minor": 2, "small": 2,
    "suggestion": 3, "feedback": 2, "request": 3,
    "maintenance request": 4, "maintenance": 3,
    "information": 2, "query": 2,
    "footpath": 4, "pavement": 4, "broken footpath": 6,
    "park": 4, "garden": 4, "bench": 3,
    "paint": 3, "graffiti": 5, "vandalism": 8,
    "slow internet": 3, "wifi": 3,
    "complaint": 2,  # generic
}

# ================================================================== #
#  CATEGORY DETECTION KEYWORDS
# ================================================================== #

CATEGORY_KEYWORDS = {
    "Safety": [
        "fire", "explosion", "gas", "leak", "accident", "violence",
        "assault", "murder", "collapse", "emergency", "electric shock",
        "electrocution", "flood", "drowning", "bomb", "terror", "toxic",
        "chemical", "injury", "injured", "bleeding", "unconscious"
    ],
    "Electricity": [
        "electric", "electricity", "power", "light", "street light", "streetlight", "street lights",
        "transformer", "short circuit", "blackout", "outage", "voltage", "wire",
        "bulb", "generator", "meter"
    ],
    "Water": [
        "water", "pipe", "leak", "sewage", "drainage", "flood",
        "contaminated", "drinking", "supply", "borewell", "tank"
    ],
    "Roads": [
        "road", "pothole", "accident", "traffic", "signal", "bridge",
        "highway", "street", "pavement", "footpath", "construction",
        "blockage", "digging"
    ],
    "Sanitation": [
        "garbage", "waste", "litter", "dump", "sanitation", "toilet",
        "sewage", "pest", "mosquito", "rat", "hygiene", "filth"
    ],
    "Security": [
        "theft", "robbery", "crime", "police", "security", "assault",
        "trespass", "break-in", "vandal", "cctv", "patrol"
    ],
    "Environment": [
        "pollution", "noise", "air", "dust", "smoke", "tree",
        "forest", "environment", "green", "park", "plant"
    ],
    "Health": [
        "hospital", "disease", "epidemic", "health", "medical",
        "ambulance", "clinic", "contamination", "outbreak", "doctor"
    ],
    "General": []  # fallback
}

# ================================================================== #
#  URGENCY AMPLIFIER PHRASES
#  These multiply the final score upward when detected.
# ================================================================== #

URGENCY_AMPLIFIERS = [
    "please help", "very urgent", "immediately", "right now",
    "asap", "as soon as possible", "dying", "no time",
    "people are", "children are", "elderly", "baby", "infant",
    "many people", "crowd", "public place", "school", "hospital",
    "spreading", "getting worse", "since many days", "for weeks",
    "nobody is helping", "ignored", "emergency situation",
]

# ================================================================== #
#  MAIN PREDICTION FUNCTION
# ================================================================== #

def predict_priority(title: str, description: str) -> dict:
    """
    Analyze a complaint and predict its priority level, score, and category.

    Parameters
    ----------
    title       : Complaint title (string)
    description : Complaint description (string)

    Returns
    -------
    dict : {
        "priority"  : "Critical" | "High" | "Medium" | "Low",
        "score"     : int (0–100),
        "category"  : str
    }
    """
    # Combine and normalize text
    combined = f"{title} {description}".lower()
    combined = re.sub(r'[^\w\s]', ' ', combined)  # remove punctuation
    combined = re.sub(r'\s+', ' ', combined).strip()

    # ---- Step 1: Keyword scoring ----------------------------------- #
    raw_score = 0
    matched_categories = defaultdict(int)

    for keyword, weight in CRITICAL_KEYWORDS.items():
        if keyword in combined:
            raw_score += weight
            matched_categories["Safety"] += weight

    for keyword, weight in HIGH_KEYWORDS.items():
        if keyword in combined:
            raw_score += weight

    for keyword, weight in MEDIUM_KEYWORDS.items():
        if keyword in combined:
            raw_score += weight

    for keyword, weight in LOW_KEYWORDS.items():
        if keyword in combined:
            raw_score += weight

    # ---- Step 2: Urgency amplifier --------------------------------- #
    urgency_bonus = 0
    for phrase in URGENCY_AMPLIFIERS:
        if phrase in combined:
            urgency_bonus += 8

    raw_score += min(urgency_bonus, 20)  # cap urgency bonus at 20

    # ---- Step 3: Length & detail bonus ----------------------------- #
    word_count = len(combined.split())
    if word_count > 50:
        raw_score += 5   # detailed complaints signal seriousness
    elif word_count > 100:
        raw_score += 8

    # ---- Step 4: Category detection -------------------------------- #
    category = _detect_category(combined, matched_categories)

    # ---- Step 5: Category-based multiplier ------------------------- #
    if category == "Safety":
        raw_score = int(raw_score * 1.20)
    elif category == "Health":
        raw_score = int(raw_score * 1.10)
    elif category == "Security":
        raw_score = int(raw_score * 1.05)

    # ---- Step 6: Clamp to 0–100 ------------------------------------ #
    score = max(1, min(100, raw_score))

    # ---- Step 7: Score → Priority label ---------------------------- #
    if score >= 81:
        priority = "Critical"
    elif score >= 61:
        priority = "High"
    elif score >= 31:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "priority": priority,
        "score": score,
        "category": category,
    }


def _detect_category(text: str, matched_safety: dict) -> str:
    """
    Determine the most likely category based on keyword frequency and weight.

    Parameters
    ----------
    text           : Normalized complaint text
    matched_safety : Accumulated safety-category weights

    Returns
    -------
    str : Category name
    """
    scores = defaultdict(int)

    # Use matched safety score if significant
    if matched_safety.get("Safety", 0) >= 30:
        scores["Safety"] += matched_safety["Safety"]

    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "General":
            continue
        for kw in keywords:
            if kw in text:
                # Give higher weight to multi-word matches
                weight = 3 if ' ' in kw else 1
                scores[category] += weight

    if not scores:
        return "General"

    best = max(scores, key=scores.get)
    return best


# ================================================================== #
#  STANDALONE TEST (run: python model.py)
# ================================================================== #

if __name__ == "__main__":
    test_cases = [
        ("Gas leakage near houses", "There is a severe gas leakage near residential houses. People are unable to breathe. Please help immediately."),
        ("Street light not working", "The street light on main road is not working since 3 days."),
        ("Garbage not collected", "Garbage has not been collected from our area for a week."),
        ("Water pipe burst", "A major water pipe has burst near the market area, causing flooding on the road."),
        ("Suggest a park bench", "I would like to request a new bench in the local park for elderly people."),
        ("Building collapse risk", "An old building is showing cracks and may collapse anytime. There are families living inside."),
    ]

    print(f"\n{'='*65}")
    print(f"  AI COMPLAINT PRIORITIZATION ENGINE — TEST RESULTS")
    print(f"{'='*65}\n")

    for title, desc in test_cases:
        result = predict_priority(title, desc)
        print(f"  Complaint : {title}")
        print(f"  Category  : {result['category']}")
        print(f"  Priority  : {result['priority']}")
        print(f"  Score     : {result['score']}/100")
        print(f"  {'-'*55}")
