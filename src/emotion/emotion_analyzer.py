"""
src/emotion/emotion_analyzer.py - Contextual emotion classification for English & Malayalam.
"""

import re
from typing import Dict, Tuple, List


# English Emotion Lexicon
ENGLISH_EMOTIONS: Dict[str, Dict[str, float]] = {
    "happy": {
        "delighted": 1.0, "joy": 0.9, "joyful": 0.9, "happily": 0.8, "happy": 0.8,
        "laugh": 0.9, "laughed": 0.9, "laughing": 0.8, "smile": 0.7, "smiled": 0.8,
        "smiling": 0.7, "excited": 0.9, "excitement": 0.9, "thrilled": 1.0,
        "cheerful": 0.8, "cheerfully": 0.8, "radiant": 0.8, "celebrate": 0.9,
        "celebrating": 0.9, "victory": 0.8, "wonderful": 0.8, "fantastic": 0.8,
        "brilliant": 0.8, "glad": 0.7, "warmly": 0.7, "glee": 0.9, "chuckle": 0.8,
        "grinned": 0.8, "jubilant": 1.0, "ecstatic": 1.0, "hooray": 1.0, "yay": 0.9,
        "blessed": 0.7, "pleasure": 0.7, "delight": 0.9, "merry": 0.8, "treasure": 0.8,
        "finally": 0.7
    },
    "sad": {
        "sad": 0.8, "sadly": 0.8, "sadness": 0.9, "tears": 0.9, "tearful": 0.9,
        "weep": 0.9, "weeping": 0.9, "wept": 1.0, "cry": 0.8, "cried": 0.8,
        "crying": 0.8, "grief": 1.0, "grieving": 1.0, "sorrow": 0.9, "sorrowful": 0.9,
        "heartbroken": 1.0, "heartbreak": 1.0, "mourn": 0.9, "mourning": 0.9,
        "desolate": 0.9, "lonely": 0.8, "alone": 0.6, "despair": 1.0,
        "miserable": 0.9, "tragedy": 0.9, "tragic": 0.9, "regret": 0.8,
        "regretted": 0.8, "sigh": 0.7, "sighed": 0.8, "unfortunately": 0.7,
        "alas": 0.9, "depressed": 0.9, "gloomy": 0.8, "dejected": 0.9, "hopeless": 0.9,
        "loss": 0.8, "pain": 0.7, "never": 0.5
    },
    "fear": {
        "fear": 0.9, "fearful": 0.9, "afraid": 0.8, "scared": 0.8, "terrify": 1.0,
        "terrified": 1.0, "terrifying": 1.0, "terror": 1.0, "horror": 0.9,
        "dread": 0.9, "dreading": 0.9, "panic": 1.0, "panicked": 1.0,
        "shivering": 0.8, "shiver": 0.8, "tremble": 0.9, "trembling": 0.9,
        "shudder": 0.9, "shuddered": 0.9, "creepy": 0.7, "nightmare": 0.8,
        "danger": 0.8, "dangerous": 0.8, "trapped": 0.8, "paralyzed": 0.9,
        "monster": 0.8, "monstrous": 0.8, "alarmed": 0.8, "frightened": 0.9,
        "run": 0.8, "flee": 0.8, "help": 0.8, "hide": 0.7, "threatened": 0.8
    },
    "anger": {
        "angry": 0.9, "angrily": 0.9, "anger": 0.9, "furious": 1.0, "furiously": 1.0,
        "fury": 1.0, "rage": 1.0, "raging": 1.0, "mad": 0.7, "annoyed": 0.7,
        "irritated": 0.7, "snapped": 0.8, "growled": 0.9, "snarled": 0.9,
        "shouted": 0.8, "yelled": 0.9, "screamed": 0.8, "glared": 0.8,
        "curse": 0.8, "cursed": 0.8, "bitter": 0.7, "bitterly": 0.8, "stern": 0.7,
        "sternly": 0.8, "outrage": 0.9, "outraged": 1.0, "fumed": 0.9, "wrath": 1.0,
        "betray": 0.9, "betrayed": 0.9, "betrayal": 0.9, "dare": 0.8, "stop": 0.6
    },
    "surprise": {
        "surprised": 0.9, "surprise": 0.8, "astonishing": 0.9, "astonished": 1.0,
        "amazement": 0.9, "amazed": 0.9, "shocked": 0.9, "shock": 0.9,
        "stunning": 0.8, "stunned": 0.9, "bewildered": 0.8, "disbelief": 0.9,
        "incredulous": 0.9, "gasp": 0.8, "gasped": 0.8, "breathless": 0.8,
        "unbelievable": 0.9, "incredible": 0.8, "suddenly": 0.7, "abruptly": 0.7
    },
    "suspense": {
        "slowly": 0.6, "cautiously": 0.7, "creeping": 0.8, "crept": 0.8,
        "stealthily": 0.8, "whisper": 0.8, "whispered": 0.8, "silence": 0.7,
        "silent": 0.7, "dark": 0.6, "darkness": 0.7, "hidden": 0.7, "lurking": 0.8,
        "shadow": 0.6, "shadows": 0.6, "hesitated": 0.7, "waiting": 0.6,
        "mysterious": 0.8, "mystery": 0.8, "secret": 0.7, "chill": 0.7,
        "eerie": 0.8, "unseen": 0.8, "approaching": 0.6, "hushed": 0.8
    },
    "curiosity": {
        "wonder": 0.7, "wondered": 0.8, "pondered": 0.8, "curious": 0.9,
        "curiously": 0.9, "questioned": 0.7, "inquired": 0.8, "puzzled": 0.8,
        "perplexed": 0.8, "confused": 0.7, "mystified": 0.8, "intrigued": 0.8,
        "examine": 0.6, "investigate": 0.7, "could": 0.5, "would": 0.4
    },
    "warmth": {
        "love": 0.8, "loved": 0.8, "tender": 0.9, "tenderly": 0.9, "affection": 0.9,
        "affectionate": 0.9, "gentle": 0.8, "gently": 0.8, "kind": 0.7, "kindly": 0.8,
        "softly": 0.8, "caring": 0.8, "comfort": 0.8, "comforting": 0.8,
        "embraced": 0.8, "sweet": 0.7, "sweetly": 0.8, "compassion": 0.9, "kissed": 0.8
    }
}

# Malayalam Emotion Lexicon
MALAYALAM_EMOTIONS: Dict[str, Dict[str, float]] = {
    "happy": {
        "സന്തോഷം": 0.9, "ആനന്ദം": 1.0, "ചിരിച്ചു": 0.9, "ചിരി": 0.8, "വിജയം": 0.9,
        "ആഹ്ലാദം": 1.0, "അതിശയകരം": 0.8, "സുന്ദരം": 0.8, "നല്ല": 0.6, "പ്രിയപ്പെട്ട": 0.8
    },
    "sad": {
        "കണ്ണീർ": 1.0, "കരഞ്ഞു": 0.9, "ദുഃഖം": 1.0, "വേദന": 0.9, "നഷ്ടം": 0.8,
        "വേർപാട്": 0.9, "സങ്കടം": 0.9, "നെടുവീർപ്പ്": 0.8, "ഏകാന്തത": 0.8
    },
    "fear": {
        "ഭയം": 1.0, "പേടി": 0.9, "പേടിച്ചു": 0.9, "വിറച്ചു": 0.9, "നിലവിളിച്ചു": 1.0,
        "അപകടം": 0.9, "ഭീകരം": 0.9, "ഓടി": 0.8, "ഭയന്നു": 0.9
    },
    "anger": {
        "ദേഷ്യം": 0.9, "കോപം": 1.0, "അലറി": 0.9, "ഗർജ്ജിച്ചു": 1.0, "ആക്രോശിച്ചു": 1.0,
        "വെറുപ്പ്": 0.9, "രോഷം": 1.0, "ശകാരിച്ചു": 0.8
    },
    "surprise": {
        "പെട്ടെന്ന്": 0.8, "അത്ഭുതപ്പെട്ടു": 1.0, "സ്തബ്ധനായി": 1.0, "വിസ്മയം": 0.9,
        "ഞെട്ടി": 0.9, "അപ്രതീക്ഷിതമായി": 0.8
    },
    "suspense": {
        "പതുക്കെ": 0.7, "നിശ്ശബ്ദത": 0.8, "ഇരുട്ട്": 0.8, "രഹസ്യം": 0.8, "കാതോർത്തു": 0.8,
        "ഭീതി": 0.8, "മൂടിപ്പുതച്ചു": 0.7
    },
    "curiosity": {
        "എന്ത്": 0.6, "എന്തുകൊണ്ട്": 0.8, "ചോദിച്ചു": 0.7, "സംശയം": 0.8, "ആലോചിച്ചു": 0.7,
        "അന്വേഷിച്ചു": 0.8
    },
    "warmth": {
        "സ്നേഹം": 1.0, "വാത്സല്യം": 1.0, "ആശ്ലേഷിച്ചു": 0.9, "തലോടി": 0.9, "മൃദുവായി": 0.8,
        "കരുണ": 0.9
    }
}

# English Dialogue Tag Mappings
ENGLISH_DIALOGUE_TAGS: Dict[str, Tuple[str, float]] = {
    "laughed": ("happy", 0.9), "giggled": ("happy", 0.9), "cheered": ("happy", 1.0),
    "sobbed": ("sad", 1.0), "wept": ("sad", 1.0), "sighed": ("sad", 0.7),
    "screamed": ("fear", 0.9), "shrieked": ("fear", 1.0), "gasped": ("surprise", 0.9),
    "whispered": ("suspense", 0.8), "murmured": ("suspense", 0.7),
    "shouted": ("anger", 0.8), "yelled": ("anger", 0.9), "growled": ("anger", 0.9),
    "demanded": ("anger", 0.8), "snarled": ("anger", 1.0),
    "asked": ("curiosity", 0.6), "inquired": ("curiosity", 0.7), "wondered": ("curiosity", 0.7)
}

# Malayalam Dialogue Tag Mappings
MALAYALAM_DIALOGUE_TAGS: Dict[str, Tuple[str, float]] = {
    "ചിരിച്ചു": ("happy", 0.9), "ആഹ്ലാദിച്ചു": ("happy", 1.0),
    "കരഞ്ഞു": ("sad", 0.9), "നെടുവീർപ്പിട്ടു": ("sad", 0.8),
    "നിലവിളിച്ചു": ("fear", 1.0), "ഭയന്നു": ("fear", 0.9),
    "പതുക്കെ പറഞ്ഞു": ("suspense", 0.8), "മന്ത്രിച്ചു": ("suspense", 0.9),
    "അലറി": ("anger", 0.9), "ഗർജ്ജിച്ചു": ("anger", 1.0), "ആക്രോശിച്ചു": ("anger", 1.0),
    "ചോദിച്ചു": ("curiosity", 0.7), "ആലോചിച്ചു": ("curiosity", 0.7)
}


class EmotionAnalyzer:
    """Analyzes text semantics and punctuation to determine sentence emotion and confidence."""

    def __init__(self, lang: str = "en"):
        self.lang = lang.lower()
        if self.lang == "ml":
            self.lexicon = MALAYALAM_EMOTIONS
            self.dialogue_tags = MALAYALAM_DIALOGUE_TAGS
        else:
            self.lexicon = ENGLISH_EMOTIONS
            self.dialogue_tags = ENGLISH_DIALOGUE_TAGS

    def analyze_sentence(self, sentence: str) -> Tuple[str, float]:
        """
        Classifies emotion based on vocabulary matching, dialogue tags, and punctuation.
        Returns: (emotion_label, confidence_score: 0.0 to 1.0)
        """
        lower_sent = sentence.lower()
        words = re.findall(r'\b[\w\u0D00-\u0D7F]+\b', lower_sent)

        # 1. Dialogue tag checking (strongest indicator of character intent)
        for tag, (tag_emotion, tag_weight) in self.dialogue_tags.items():
            if tag in lower_sent:
                return tag_emotion, min(1.0, tag_weight)

        # 2. Score vocabulary matches
        scores: Dict[str, float] = {k: 0.0 for k in self.lexicon.keys()}
        for word in words:
            for em, kw_dict in self.lexicon.items():
                if word in kw_dict:
                    scores[em] += kw_dict[word]

        # 3. Punctuation indicators
        is_exclamation = "!" in sentence
        is_question = "?" in sentence
        is_ellipsis = "..." in sentence

        if is_question and not is_exclamation:
            scores["curiosity"] += 0.8
        elif is_exclamation:
            best_curr = max(scores, key=scores.get)
            if scores[best_curr] > 0.4:
                scores[best_curr] += 0.7
            else:
                scores["surprise"] += 0.5
                scores["happy"] += 0.4

        if is_ellipsis:
            scores["suspense"] += 0.8

        best_emotion, highest_score = max(scores.items(), key=lambda item: item[1])

        if highest_score < 0.45:
            return "neutral", 0.0

        confidence = min(1.0, highest_score / 2.0)
        return best_emotion, confidence
