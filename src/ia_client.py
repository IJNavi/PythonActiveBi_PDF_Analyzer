"""Cliente para interação com API OpenAI"""

import json
import re
from typing import List
from openai import OpenAI
import tiktoken

class IAClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", timeout: float = 60.0):
        self.client = OpenAI(api_key=api_key, timeout=timeout)
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
        """
        Gera 3 perguntas de acompanhamento no idioma especificado (language),
        preservando termos técnicos em inglês quando comum, mas estrutura no idioma alvo.
        Suporta: en, pt, es, fr, zh, hi, ar
        """
        prompts = {
            'en': {
                'system': "You are a BI analyst. Generate follow-up questions STRICTLY in English, preserving technical jargon from other languages only when necessary.",
                'user': f"""
                Based on this document: {metadata.get('filename', 'Documento')}
                Context (summary): {context[:3000]}
            
                Generate exactly 3 follow-up questions in English.
                - The sentence structure must be in English.
                - You may keep technical terms from other languages (e.g., 'dashboard', 'feedback') if they are common.
                - Do not mix languages unnecessarily.
            
                Return ONLY the questions, one per line, numbered (1., 2., 3.).
                """
            },
            'pt': {
                'system': "Você é um analista de BI. Gere perguntas de acompanhamento ESTRITAMENTE em português, preservando apenas jargões técnicos em inglês quando não houver tradução comum.",
                'user': f"""
                Com base neste documento: {metadata.get('filename', 'Documento')}
                Contexto (resumo): {context[:3000]}
            
                Gere exatamente 3 perguntas de acompanhamento em português.
                - A estrutura gramatical deve ser em português.
                - Você pode manter termos técnicos em inglês (ex: ROI, CEO, feedback, dashboard) se eles forem comuns.
                - Não misture idiomas desnecessariamente.
            
                Retorne APENAS as perguntas, uma por linha, numeradas (1., 2., 3.).
                """
            },
            'es': {
                'system': "Eres un analista de BI. Genera preguntas de seguimiento ESTRICTAMENTE en español, conservando solo la jerga técnica en inglés cuando no haya una traducción común.",
                'user': f"""
                Basado en este documento: {metadata.get('filename', 'Documento')}
                Contexto (resumen): {context[:3000]}
            
                Genera exactamente 3 preguntas de seguimiento en español.
                - La estructura gramatical debe ser en español.
                - Puedes mantener términos técnicos en inglés (ej: ROI, CEO, feedback, dashboard) si son comunes.
                - No mezcles idiomas innecesariamente.
            
                Devuelve SOLO las preguntas, una por línea, numeradas (1., 2., 3.).
                """
            },
            'fr': {
                'system': "Vous êtes un analyste BI. Générez des questions de suivi STRICTEMENT en français, en ne conservant que le jargon technique en anglais lorsqu'il n'existe pas de traduction courante.",
                'user': f"""
                Basé sur ce document: {metadata.get('filename', 'Documento')}
                Contexte (résumé): {context[:3000]}
            
                Générez exactement 3 questions de suivi en français.
                - La structure grammaticale doit être en français.
                - Vous pouvez conserver les termes techniques en anglais (ex: ROI, CEO, feedback, dashboard) s'ils sont courants.
                - Ne mélangez pas les langues inutilement.
            
                Retournez UNIQUEMENT les questions, une par ligne, numérotées (1., 2., 3.).
                """
            },
            'zh': {
                'system': "您是一位商业智能分析师。请严格用中文生成后续问题，仅在必要时保留英文技术术语。",
                'user': f"""
                基于此文档: {metadata.get('filename', 'Documento')}
                上下文（摘要）: {context[:3000]}
            
                请生成正好3个中文后续问题。
                - 语法结构必须是中文。
                - 您可以保留常见的英文技术术语（例如 ROI、CEO、feedback、dashboard）。
                - 不要不必要地混合语言。
            
                仅返回问题，每行一个，编号（1.、2.、3.）。
                """
            },
            'hi': {
                'system': "आप एक BI विश्लेषक हैं। केवल आवश्यक होने पर अंग्रेजी तकनीकी शब्दों को बनाए रखते हुए, सख्ती से हिंदी में अनुवर्ती प्रश्न उत्पन्न करें।",
                'user': f"""
                इस दस्तावेज़ के आधार पर: {metadata.get('filename', 'Documento')}
                संदर्भ (सारांश): {context[:3000]}
            
                हिंदी में ठीक 3 अनुवर्ती प्रश्न तैयार करें।
                - व्याकरणिक संरचना हिंदी में होनी चाहिए।
                - आप सामान्य अंग्रेजी तकनीकी शब्दों (जैसे ROI, CEO, feedback, dashboard) को बनाए रख सकते हैं।
                - अनावश्यक रूप से भाषाओं को मिश्रित न करें।
            
                केवल प्रश्न लौटाएं, एक पंक्ति में एक, क्रमांकित (1., 2., 3.)।
                """
            },
            'ar': {
                'system': "أنت محلل BI. قم بإنشاء أسئلة متابعة باللغة العربية بدقة، مع الاحتفاظ بالمصطلحات التقنية الإنجليزية فقط عند الضرورة.",
                'user': f"""
                بناءً على هذا المستند : {metadata.get('filename', 'Documento')}
                السياق (ملخص): {context[:3000]}
            
                قم بإنشاء 3 أسئلة متابعة باللغة العربية.
                - يجب أن يكون التركيب النحوي باللغة العربية.
                - يمكنك الاحتفاظ بالمصطلحات التقنية الإنجليزية الشائعة (مثل ROI، CEO، feedback، dashboard).
                - لا تخلط اللغات دون داع.
            
                قم بإرجاع الأسئلة فقط، سطر واحد لكل سؤال، مرقمة (1.، 2.، 3.).
                """
            }
        }
    
        # Fallback para inglês se o idioma não for suportado
        if language not in prompts:
            language = 'en'
    
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompts[language]['system']},
                {"role": "user", "content": prompts[language]['user']}
            ],
            temperature=0.7,
            max_tokens=400
        )
    
        suggestions_text = response.choices[0].message.content.strip()
        suggestions = []
    
        for line in suggestions_text.split('\n'):
            clean_line = line.strip()
            if clean_line and clean_line[0].isdigit():
                import re
                clean_line = re.sub(r'^\d+[\.\)\-]\s*', '', clean_line)
            if clean_line:
                suggestions.append(clean_line)
    
        # Fallbacks genéricos por idioma (apenas se necessário)
        defaults = {
            'en': [
                "What are the main points not mentioned here?",
                "How do these insights impact business strategy?",
                "What immediate actions can be taken?"
            ],
            'pt': [
                "Quais os principais pontos de atenção não mencionados?",
                "Como esses insights impactam a estratégia do negócio?",
                "Quais ações imediatas podem ser tomadas?"
            ],
            'es': [
                "¿Cuáles son los principales puntos no mencionados?",
                "¿Cómo impactan estos conocimientos en la estrategia empresarial?",
                "¿Qué acciones inmediatas se pueden tomar?"
            ],
            'fr': [
                "Quels sont les principaux points non mentionnés?",
                "Comment ces informations impactent-elles la stratégie d'entreprise?",
                "Quelles actions immédiates peuvent être prises?"
            ],
            'zh': [
                "未提到的主要观点是什么？",
                "这些见解如何影响商业战略？",
                "可以采取哪些立即行动？"
            ],
            'hi': [
                "मुख्य बिंदु क्या हैं जिनका उल्लेख नहीं किया गया है?",
                "ये अंतर्दृष्टि व्यावसायिक रणनीति को कैसे प्रभावित करती हैं?",
                "तत्काल क्या कार्रवाई की जा सकती है?"
            ],
            'ar': [
                "ما هي النقاط الرئيسية غير المذكورة؟",
                "كيف تؤثر هذه الأفكار على استراتيجية العمل？",
                "ما هي الإجراءات الفورية التي يمكن اتخاذها؟"
            ]
        }
    
        while len(suggestions) < 3:
            suggestions.append(defaults[language][len(suggestions)])
    
        return suggestions[:3]
