TRANSLATIONS = {
    "hi": {
        "Suspicious Transaction Blocked": "संदिग्ध लेनदेन रोका गया",
        "Transaction Needs Confirmation": "लेनदेन की पुष्टि आवश्यक है",
        "Reply YES if this was you.": "यदि यह आपने किया है तो YES भेजें।",
        "Reply NO if this was NOT you.": "यदि यह आपने नहीं किया है तो NO भेजें।"
    },
    "ta": {
        "Suspicious Transaction Blocked": "சந்தேகமான பரிவர்த்தனை தடுக்கப்பட்டது",
        "Transaction Needs Confirmation": "பரிவர்த்தனை உறுதிப்படுத்தல் தேவை",
        "Reply YES if this was you.": "இது நீங்கள் செய்தது என்றால் YES அனுப்பவும்.",
        "Reply NO if this was NOT you.": "இது நீங்கள் செய்யவில்லை என்றால் NO அனுப்பவும்."
    }
}

def translate_text(text, language="en"):
    if language == "en":
        return text

    translated = text
    for eng, local in TRANSLATIONS.get(language, {}).items():
        translated = translated.replace(eng, local)

    return translated

