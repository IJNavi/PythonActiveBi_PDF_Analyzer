"""Calculadora de custos baseada em tokens"""

import tiktoken

class CostCalculator:
    PRICING = {
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
        'gpt-4o': {'input': 2.50, 'output': 10.00},
        'gpt-4-turbo': {'input': 10.00, 'output': 30.00},
    }
    
    def __init__(self, model: str = 'gpt-4o-mini'):
        self.model = model
        self.encoder = tiktoken.encoding_for_model(model)
        
        if model not in self.PRICING:
            self.pricing = self.PRICING['gpt-4o-mini']
        else:
            self.pricing = self.PRICING[model]
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        cost_input = (input_tokens / 1_000_000) * self.pricing['input']
        cost_output = (output_tokens / 1_000_000) * self.pricing['output']
        return cost_input + cost_output