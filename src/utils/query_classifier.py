"""
Query Classification Module

Uses LLM to intelligently classify user queries and determine appropriate response strategy.
This is a framework component - users can customize classification logic for their specific agents.
"""

from enum import Enum
from typing import Dict, Any, Optional
import json


class QueryType(Enum):
    """Types of user queries - can be extended by users."""
    GREETING = "greeting"
    SIMPLE_QUESTION = "simple_question"
    COMPLEX_TASK = "complex_task"
    CLARIFICATION = "clarification"


class QueryClassifier:
    """
    LLM-based query classifier for intelligent routing.

    This is a framework component that can be customized for specific agent needs.
    Users can:
    - Extend QueryType enum with custom types
    - Provide custom classification prompts
    - Override classification logic
    """

    DEFAULT_CLASSIFICATION_PROMPT = """You are a query classifier for an AI agent system. Analyze the user's query and classify it into one of these categories:

1. GREETING - Simple greetings, small talk (e.g., "hello", "how are you", "你好")
   → Strategy: Quick friendly response, no planning needed

2. SIMPLE_QUESTION - Single factual questions, definitions (e.g., "What is Python?", "Who invented AI?")
   → Strategy: Direct answer, minimal processing

3. COMPLEX_TASK - Multi-step tasks requiring planning/execution (e.g., "Create a web app", "Analyze data and generate report")
   → Strategy: Full planning-thinking-execution-evaluation workflow

4. CLARIFICATION - User clarifying or confirming something
   → Strategy: Context-aware response

User Query: "{query}"

Respond ONLY with a JSON object in this exact format:
{{
    "type": "GREETING|SIMPLE_QUESTION|COMPLEX_TASK|CLARIFICATION",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "use_full_workflow": true|false
}}"""

    def __init__(self, llm_client=None, custom_prompt: Optional[str] = None):
        """
        Initialize query classifier.

        Args:
            llm_client: LLM client for classification (required for LLM-based classification)
            custom_prompt: Optional custom classification prompt for specialized agents
        """
        self.llm_client = llm_client
        self.classification_prompt = custom_prompt or self.DEFAULT_CLASSIFICATION_PROMPT

    def classify(self, query: str) -> Dict[str, Any]:
        """
        Classify a user query using LLM.

        Args:
            query: The user's query string

        Returns:
            Dict with classification results:
            {
                "type": QueryType,
                "confidence": float,
                "use_full_workflow": bool,
                "reasoning": str,
                "suggested_response_strategy": str
            }
        """
        if self.llm_client is None:
            # Fallback: assume complex task if no LLM client
            return self._fallback_classification(query)

        try:
            # Use LLM to classify
            prompt = self.classification_prompt.format(query=query)

            response = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=200
            )

            # Parse LLM response
            result_text = response.get('content', '').strip()

            # Extract JSON from response
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()

            classification = json.loads(result_text)

            # Convert to QueryType enum
            query_type_str = classification.get('type', 'COMPLEX_TASK').upper()
            try:
                query_type = QueryType[query_type_str]
            except KeyError:
                query_type = QueryType.COMPLEX_TASK

            return {
                "type": query_type,
                "confidence": classification.get('confidence', 0.8),
                "use_full_workflow": classification.get('use_full_workflow', True),
                "reasoning": classification.get('reasoning', ''),
                "suggested_response_strategy": self._get_strategy(query_type)
            }

        except Exception as e:
            # Fallback on error
            print(f"Classification error: {e}, using fallback")
            return self._fallback_classification(query)

    def _fallback_classification(self, query: str) -> Dict[str, Any]:
        """
        Simple fallback classification when LLM is not available.

        Args:
            query: User query

        Returns:
            Classification result
        """
        # Very basic heuristics
        query_lower = query.lower().strip()

        # Check for obvious greetings
        greetings = ['hello', 'hi', 'hey', '你好', '您好', 'hola', 'bonjour']
        if any(greet in query_lower for greet in greetings) and len(query.split()) <= 3:
            return {
                "type": QueryType.GREETING,
                "confidence": 0.9,
                "use_full_workflow": False,
                "reasoning": "Simple greeting detected",
                "suggested_response_strategy": "direct_response"
            }

        # Default to complex task (safe fallback)
        return {
            "type": QueryType.COMPLEX_TASK,
            "confidence": 0.6,
            "use_full_workflow": True,
            "reasoning": "Default to full workflow for safety",
            "suggested_response_strategy": "full_planning"
        }

    def _get_strategy(self, query_type: QueryType) -> str:
        """Get response strategy for query type."""
        strategy_map = {
            QueryType.GREETING: "direct_response",
            QueryType.SIMPLE_QUESTION: "quick_answer",
            QueryType.COMPLEX_TASK: "full_planning",
            QueryType.CLARIFICATION: "context_aware"
        }
        return strategy_map.get(query_type, "full_planning")

    def get_quick_response(self, query: str, classification: Dict[str, Any]) -> str:
        """
        Generate a quick response for simple queries without full workflow.

        Args:
            query: The user's query
            classification: Classification results

        Returns:
            Quick response string
        """
        if classification["type"] == QueryType.GREETING:
            return self._get_greeting_response(query)
        else:
            return None  # Needs LLM for other types

    def _get_greeting_response(self, query: str) -> str:
        """Generate greeting response."""
        query_lower = query.lower()

        # Check language and respond appropriately
        if any(ch in query for ch in ['你好', '您好', '嗨']):
            return """你好！我是一个智能 AI Agent，可以帮助您处理各种任务。

我的能力包括：
• 💡 规划和执行复杂任务
• 📝 编写和分析代码
• 🔍 研究和收集信息
• 🤔 问题解决和决策

有什么我可以帮助您的吗？"""
        else:
            return """Hello! I'm an intelligent AI Agent that can help you with various tasks.

My capabilities include:
• 💡 Planning and executing complex tasks
• 📝 Writing and analyzing code
• 🔍 Researching and gathering information
• 🤔 Problem-solving and decision making

What can I help you with today?"""


# Convenience function
def classify_query(query: str, llm_client=None) -> Dict[str, Any]:
    """
    Classify a user query.

    Args:
        query: User's query string
        llm_client: Optional LLM client

    Returns:
        Classification results dict
    """
    classifier = QueryClassifier(llm_client)
    return classifier.classify(query)
