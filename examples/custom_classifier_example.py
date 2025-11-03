#!/usr/bin/env python3
"""
Custom Query Classifier Example

This example demonstrates how to customize the QueryClassifier
for specialized agents. The framework is flexible - you can:
1. Extend QueryType with custom types
2. Provide custom classification prompts
3. Create domain-specific agents

Examples:
- Code review agent
- Data analysis agent
- Customer support agent
- DevOps agent
"""

from dotenv import load_dotenv
from src.utils.query_classifier import QueryClassifier, QueryType
from src.utils.llm_client import AzureOpenAIClient
from enum import Enum

load_dotenv()


# Example 1: Custom Query Types for Code Review Agent
class CodeReviewQueryType(Enum):
    """Custom query types for code review agent."""
    CODE_REVIEW_REQUEST = "code_review_request"
    SECURITY_CHECK = "security_check"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    BEST_PRACTICES = "best_practices"
    SIMPLE_QUESTION = "simple_question"


# Example 2: Custom Classification Prompt for Code Review Agent
CODE_REVIEW_CLASSIFICATION_PROMPT = """You are a query classifier for a specialized CODE REVIEW agent.
Analyze the user's query and classify it:

1. CODE_REVIEW_REQUEST - User wants code to be reviewed
   Example: "Review this Python function", "Check my code"
   → Strategy: Full code analysis workflow

2. SECURITY_CHECK - Specifically asking about security
   Example: "Are there any security vulnerabilities?", "Is this code safe?"
   → Strategy: Security-focused analysis

3. PERFORMANCE_ANALYSIS - Performance-related queries
   Example: "How can I optimize this?", "Is this efficient?"
   → Strategy: Performance profiling

4. BEST_PRACTICES - Questions about coding standards
   Example: "Is this following best practices?", "How should I structure this?"
   → Strategy: Standards checking

5. SIMPLE_QUESTION - General programming questions
   Example: "What does this function do?", "How does Python work?"
   → Strategy: Quick answer

User Query: "{query}"

Respond ONLY with JSON:
{{
    "type": "CODE_REVIEW_REQUEST|SECURITY_CHECK|PERFORMANCE_ANALYSIS|BEST_PRACTICES|SIMPLE_QUESTION",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "use_full_workflow": true|false
}}"""


# Example 3: Custom Classification Prompt for Data Analysis Agent
DATA_ANALYSIS_CLASSIFICATION_PROMPT = """You are a query classifier for a DATA ANALYSIS agent.
Classify the user's query:

1. DATA_EXPLORATION - Exploratory data analysis requests
   Example: "Show me the data distribution", "What's in this dataset?"
   → Strategy: Quick visualization and summary

2. STATISTICAL_ANALYSIS - Statistical testing and analysis
   Example: "Run correlation analysis", "Test for significance"
   → Strategy: Full statistical workflow

3. ML_MODELING - Machine learning tasks
   Example: "Build a prediction model", "Train a classifier"
   → Strategy: ML pipeline with evaluation

4. DATA_CLEANING - Data preprocessing requests
   Example: "Clean the missing values", "Remove duplicates"
   → Strategy: Data quality workflow

5. SIMPLE_QUESTION - General data questions
   Example: "What is standard deviation?", "How does this work?"
   → Strategy: Quick explanation

User Query: "{query}"

Respond ONLY with JSON:
{{
    "type": "DATA_EXPLORATION|STATISTICAL_ANALYSIS|ML_MODELING|DATA_CLEANING|SIMPLE_QUESTION",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "use_full_workflow": true|false
}}"""


def example_1_default_classifier():
    """Example 1: Using default classifier."""
    print("=" * 70)
    print("Example 1: Default General-Purpose Classifier")
    print("=" * 70)

    llm_client = AzureOpenAIClient()
    classifier = QueryClassifier(llm_client=llm_client)

    test_queries = [
        "Hello, how are you?",
        "What is Python?",
        "Create a web application with user authentication and database"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        classification = classifier.classify(query)
        print(f"Type: {classification['type'].value}")
        print(f"Confidence: {classification['confidence']:.2f}")
        print(f"Use Full Workflow: {classification['use_full_workflow']}")
        print(f"Reasoning: {classification.get('reasoning', 'N/A')}")


def example_2_code_review_agent():
    """Example 2: Custom classifier for code review agent."""
    print("\n" + "=" * 70)
    print("Example 2: Custom Code Review Agent Classifier")
    print("=" * 70)

    llm_client = AzureOpenAIClient()
    classifier = QueryClassifier(
        llm_client=llm_client,
        custom_prompt=CODE_REVIEW_CLASSIFICATION_PROMPT
    )

    test_queries = [
        "Review this Python function for best practices",
        "Are there any security vulnerabilities in this code?",
        "How can I optimize this loop for better performance?",
        "What does the enumerate function do?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        classification = classifier.classify(query)
        print(f"Classification: {classification}")


def example_3_data_analysis_agent():
    """Example 3: Custom classifier for data analysis agent."""
    print("\n" + "=" * 70)
    print("Example 3: Custom Data Analysis Agent Classifier")
    print("=" * 70)

    llm_client = AzureOpenAIClient()
    classifier = QueryClassifier(
        llm_client=llm_client,
        custom_prompt=DATA_ANALYSIS_CLASSIFICATION_PROMPT
    )

    test_queries = [
        "Show me the distribution of ages in the dataset",
        "Build a random forest model to predict customer churn",
        "Clean the missing values and remove outliers",
        "What is the difference between mean and median?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        classification = classifier.classify(query)
        print(f"Classification: {classification}")


def example_4_fallback_without_llm():
    """Example 4: Fallback behavior when LLM is not available."""
    print("\n" + "=" * 70)
    print("Example 4: Fallback Classification (No LLM)")
    print("=" * 70)

    classifier = QueryClassifier(llm_client=None)

    test_queries = [
        "Hello!",
        "Create a complex web application"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        classification = classifier.classify(query)
        print(f"Type: {classification['type'].value}")
        print(f"Use Full Workflow: {classification['use_full_workflow']}")
        print(f"Reasoning: {classification['reasoning']}")


def example_5_multilingual():
    """Example 5: Multilingual classification."""
    print("\n" + "=" * 70)
    print("Example 5: Multilingual Classification")
    print("=" * 70)

    llm_client = AzureOpenAIClient()
    classifier = QueryClassifier(llm_client=llm_client)

    test_queries = [
        "你好！",  # Chinese: Hello
        "创建一个机器学习模型来预测房价",  # Chinese: Create ML model
        "¿Qué es Python?",  # Spanish: What is Python
        "Construye una aplicación web completa"  # Spanish: Build a web app
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        classification = classifier.classify(query)
        print(f"Type: {classification['type'].value}")
        print(f"Confidence: {classification['confidence']:.2f}")
        print(f"Use Full Workflow: {classification['use_full_workflow']}")


if __name__ == "__main__":
    try:
        # Run examples
        example_1_default_classifier()
        example_2_code_review_agent()
        example_3_data_analysis_agent()
        example_4_fallback_without_llm()
        example_5_multilingual()

        print("\n" + "=" * 70)
        print("✅ All examples completed!")
        print("=" * 70)

        print("\n💡 Key Takeaways:")
        print("1. Use default classifier for general-purpose agents")
        print("2. Customize prompts for domain-specific agents")
        print("3. LLM classification works across languages")
        print("4. Fallback ensures robustness when LLM unavailable")
        print("5. Framework is flexible for any agent type!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Azure OpenAI credentials are configured in .env")
        print("2. All dependencies are installed")
