"""Cliente para interação com API OpenAI"""

import json
from typing import List
from openai import OpenAI
import tiktoken

class IAClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.encoder = tiktoken.encoding_for_model(model)
    
    def ask_question_with_context(self, context: str, question: str, 
                                   system_prompt: str, metadata: dict) -> tuple[str, dict]:
        
        user_prompt = f"""
        Documento: {metadata.get('filename', 'Documento')}
        
        Contexto relevante do documento:
        {context}
        
        Pergunta do usuário: {question}
        
        IMPORTANTE: Responda APENAS com base no contexto fornecido acima.
        Se a resposta não estiver no contexto, diga claramente que não foi encontrada.
        """
        
        input_tokens = len(self.encoder.encode(system_prompt + user_prompt))
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        response_text = response.choices[0].message.content
        output_tokens = len(self.encoder.encode(response_text))
        
        token_info = {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        }
        
        return response_text, token_info
    
    def get_suggestions(self, context: str, metadata: dict, language: str) -> List[str]:
        if language == 'pt':
            prompt = f"""
            Com base neste documento: {metadata.get('filename', 'Documento')}
            Contexto: {context[:3000]}
            Gere exatamente 3 perguntas de acompanhamento.
            Retorne APENAS as perguntas, uma por linha, numeradas.
            """
        else:
            prompt = f"""
            Based on this document: {metadata.get('filename', 'Documento')}
            Context: {context[:3000]}
            Generate exactly 3 follow-up questions.
            Return ONLY the questions, one per line, numbered.
            """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Generate relevant follow-up questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=300
        )
        
        suggestions_text = response.choices[0].message.content.strip()
        suggestions = []
        
        for line in suggestions_text.split('\n'):
            clean_line = line.strip()
            if clean_line and clean_line[0].isdigit():
                clean_line = clean_line.split('.', 1)[-1].strip()
            if clean_line:
                suggestions.append(clean_line)
        
        defaults_pt = [
            "Quais os principais pontos de atenção não mencionados?",
            "Como esses insights impactam a estratégia do negócio?",
            "Quais ações imediatas podem ser tomadas?"
        ]
        
        defaults_en = [
            "What are the main points not mentioned here?",
            "How do these insights impact business strategy?",
            "What immediate actions can be taken?"
        ]
        
        defaults = defaults_pt if language == 'pt' else defaults_en
        
        while len(suggestions) < 3:
            suggestions.append(defaults[len(suggestions)])
        
        return suggestions[:3]