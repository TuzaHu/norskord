import requests
import json
import urllib.parse
from typing import Optional

class TranslationService:
    def __init__(self):
        self.cache = {}
        self.fallback_translations = {
            # Common Norwegian words and their English translations
            "Anlegg": "Facility",
            "Avvikshåndtering": "Deviation handling",
            "Betjening": "Operation",
            "Bærekraftig": "Sustainable",
            "Forståelse": "Understanding",
            "Fortjeneste": "Profit",
            "Forurensning": "Pollution",
            "Færre": "Fewer",
            "Gjeldende": "Current",
            "Gjennomføre": "Implement",
            "Instilling": "Setting",
            "Jakter": "Hunting",
            "Kjerneelementet": "Core element",
            "Klargjøre": "Prepare",
            "Kvalitetskrav": "Quality requirements",
            "Kvalitetsstyringssystem": "Quality management system",
            "Kvalitetstester": "Quality tests",
            "Lønnsomhet": "Profitability",
            "Måter": "Ways",
            "Nedstengningsprosedyrer": "Shutdown procedures",
            "Oppstart": "Startup",
            "Optimalisering": "Optimization",
            "Planlegge": "Plan",
            "Ressursutnyttelse": "Resource utilization",
            "Risikovurdere": "Risk assessment",
            "Ryddighet": "Tidiness",
            "Råvarene": "Raw materials",
            "Tilhørende": "Belonging",
            "Ulik": "Different",
            "Utarbeide": "Develop",
            "Verdikjeden": "Value chain",
            "Vurdere": "Assess",
            "dermed": "thereby",
            "dessuten": "moreover",
            "egnet": "suitable",
            "etterspør": "demand",
            "forurensing": "pollution",
            "føre": "lead",
            "grunnleggende": "fundamental",
            "inntjening": "earnings",
            "ledelse": "management",
            "lokalene": "premises",
            "markedsføring": "marketing",
            "omstillingen": "restructuring",
            "overordnet": "overall",
            "regne": "calculate",
            "rengjøring": "cleaning",
            "rimeligere": "cheaper",
            "rådighet": "availability",
            "samfunnet": "society",
            "tilgang": "access",
            "tilpasset": "adapted",
            "trekker": "attracts",
            "ukentlige": "weekly",
            "underveis": "underway",
            "utslipp": "emissions",
            "utstyret": "equipment",
            "vedlikehold": "maintenance",
            # Phrases
            "Anlegg for produkthåndtering": "Facility for product handling",
            "Betjening av styresystemer": "Operation of control systems",
            "Forståelse for orden": "Understanding of order",
            "Gjeldende retningslinjer": "Current guidelines",
            "Instilling av driftparametere": "Setting of operating parameters",
            "Klargjøre materialer": "Prepare materials",
            "Nedstengningsprosedyrer": "Shutdown procedures",
            "Oppstart og nedstenging": "Startup and shutdown",
            "Ressursutnyttelse": "Resource utilization",
            "Ut fra hensikten": "Based on the purpose",
            "Videre handler om": "Further deals with",
            "Færre enheter": "Fewer units",
            "Har nytte av hverande": "Has use of each other",
            "Hva er kapasiteten": "What is the capacity",
            "I Hviken retning": "In which direction",
            "I forbindelse": "In connection",
            "Innsatsfaktorer": "Input factors",
            "Kjente begrep": "Known concepts",
            "Kort sagt": "In short",
            "Kreve endring": "Require change",
            "Mange reklamasjoner": "Many complaints",
            "Redusere behovet": "Reduce the need",
            "Resirkulering og gjenbruk": "Recycling and reuse",
            "Skarpe konkurrent": "Sharp competitor",
            "Som kan utnyttes ut fra tankem": "Which can be utilized based on thinking",
            "etterspørselen blir borte": "the demand disappears",
            "gjennomføringen av": "the implementation of",
            "markedet forandrer seg": "the market changes",
            "produksjonsinnsatsfaktorer": "production input factors",
            "skape flaskehalse": "create bottlenecks",
            "støttefuksjoner": "support functions",
            "trekker til seg": "attracts",
            "å tåle problemer underveis": "to tolerate problems along the way"
        }
    
    def get_translation(self, norwegian_word: str) -> str:
        """Get English translation for Norwegian word"""
        # Check cache first
        if norwegian_word in self.cache:
            return self.cache[norwegian_word]
        
        # Try exact match in fallback translations
        if norwegian_word in self.fallback_translations:
            translation = self.fallback_translations[norwegian_word]
            self.cache[norwegian_word] = translation
            return translation
        
        # Try partial match in fallback translations
        for key, value in self.fallback_translations.items():
            if key.lower() in norwegian_word.lower() or norwegian_word.lower() in key.lower():
                self.cache[norwegian_word] = value
                return value
        
        # Try Google Translate API (free version)
        translation = self._try_google_translate(norwegian_word)
        if translation:
            self.cache[norwegian_word] = translation
            return translation
        
        # Fallback message
        translation = f"Translation for '{norwegian_word}' not available"
        self.cache[norwegian_word] = translation
        return translation
    
    def _try_google_translate(self, norwegian_word: str) -> Optional[str]:
        """Try to get translation from Google Translate API"""
        try:
            # Using Google Translate API (free version)
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "no",  # Norwegian
                "tl": "en",  # English
                "dt": "t",
                "q": norwegian_word
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0 and len(data[0]) > 0:
                    translation = data[0][0][0]
                    if translation and translation != norwegian_word:
                        return translation
            
        except Exception as e:
            print(f"Error with Google Translate for '{norwegian_word}': {e}")
        
        return None
    
    def clear_cache(self):
        """Clear the translation cache"""
        self.cache.clear()
    
    def add_translation(self, norwegian_word: str, english_translation: str):
        """Add a custom translation to the fallback dictionary"""
        self.fallback_translations[norwegian_word] = english_translation
        self.cache[norwegian_word] = english_translation 