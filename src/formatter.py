"""Formatador de respostas no padrão JSON"""

class ResponseFormatter:
    def format_response(self, response_text: str, source: str, 
                       suggestions: list, cost_info: dict = None) -> dict:
        result = {
            "type": "text",
            "text": self._ensure_markdown(response_text),
            "source": source,
            "suggestions": self._ensure_three_suggestions(suggestions)
        }
        
        if cost_info:
            result["_metadata"] = cost_info
        
        return result
    
    def _ensure_markdown(self, text: str) -> str:
        if not any(marker in text for marker in ['#', '-', '*', '**']):
            text = f"## Resposta\n\n{text}"
        return text
    
    def _ensure_three_suggestions(self, suggestions: list) -> list:
        defaults = [
            "Quais os principais pontos de atenção?",
            "Como isso impacta o negócio?",
            "Quais ações são recomendadas?"
        ]
        
        while len(suggestions) < 3:
            suggestions.append(defaults[len(suggestions)])
        
        return suggestions[:3]