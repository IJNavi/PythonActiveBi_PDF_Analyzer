"""Controlador de níveis de resposta e idioma"""

from enum import Enum

class ResponseLevel(Enum):
    CONCISE = "concise"
    STANDARD = "standard"
    COMPLEX = "complex"

class LanguageDetector:
    @staticmethod
    def detect_language(text: str) -> str:
        pt_indicators = ['como', 'qual', 'quais', 'onde', 'quando', 'porque', 
                        'para', 'com', 'sem', 'sobre', 'esse', 'essa', 'isso',
                        'está', 'estão', 'foram', 'será', 'pode']
        
        en_indicators = ['what', 'which', 'where', 'when', 'why', 'how',
                        'for', 'with', 'without', 'about', 'this', 'that',
                        'is', 'are', 'were', 'will', 'can']
        
        text_lower = text.lower()
        pt_count = sum(1 for word in pt_indicators if word in text_lower)
        en_count = sum(1 for word in en_indicators if word in text_lower)
        
        return 'pt' if pt_count > en_count else 'en'

class ResponseController:
    def __init__(self):
        self.language_detector = LanguageDetector()
    
    def get_system_prompt(self, level: ResponseLevel, language: str) -> str:
        if language == 'pt':
            return self._get_prompt_pt(level)
        else:
            return self._get_prompt_en(level)
    
    def _get_prompt_pt(self, level: ResponseLevel) -> str:
        base = """Você é um analista de BI especialista em extrair insights de documentos.
        Responda APENAS com base no documento fornecido.
        Use Markdown para formatar a resposta.
        """
        
        if level == ResponseLevel.CONCISE:
            return base + "FORMATO: Resposta CONCISA - Máximo de 2 parágrafos"
        elif level == ResponseLevel.STANDARD:
            return base + "FORMATO: Resposta PADRÃO - Máximo de 1 página A4 (~500 palavras)"
        else:
            return base + "FORMATO: Análise COMPLEXA - Análise aprofundada e detalhada"
    
    def _get_prompt_en(self, level: ResponseLevel) -> str:
        base = """You are a BI analyst specialized in extracting insights.
        Answer ONLY based on the provided document.
        Use Markdown for formatting.
        """
        
        if level == ResponseLevel.CONCISE:
            return base + "FORMAT: CONCISE - Maximum 2 paragraphs"
        elif level == ResponseLevel.STANDARD:
            return base + "FORMAT: STANDARD - Maximum 1 A4 page (~500 words)"
        else:
            return base + "FORMAT: COMPLEX - In-depth analysis"
    
    def process_question(self, question: str, level: ResponseLevel) -> tuple[str, str]:
        language = self.language_detector.detect_language(question)
        system_prompt = self.get_system_prompt(level, language)
        return language, system_prompt