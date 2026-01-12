"""LLM client for agent reasoning."""
from typing import List, Dict, Optional
from openai import OpenAI
from anthropic import Anthropic
from src.utils.config import config


class LLMClient:
    """Unified LLM client supporting OpenAI and Anthropic."""
    
    def __init__(self):
        self.provider = config.llm_provider
        self.model = config.llm_model
        
        if self.provider == "openai":
            if not config.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=config.openai_api_key)
        elif self.provider == "anthropic":
            if not config.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self.client = Anthropic(api_key=config.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate_reasoning(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate reasoning using the configured LLM."""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        else:  # anthropic
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
    
    def generate_structured_output(
        self,
        system_prompt: str,
        user_prompt: str,
        output_format: str,
        temperature: float = 0.5
    ) -> Dict:
        """Generate structured output (JSON) from LLM."""
        structured_prompt = f"""{user_prompt}

Please respond in the following JSON format:
{output_format}

Return only valid JSON, no additional text."""
        
        response_text = self.generate_reasoning(
            system_prompt=system_prompt,
            user_prompt=structured_prompt,
            temperature=temperature
        )
        
        import json
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # Fallback: try to find JSON object in text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON from response: {response_text}")
