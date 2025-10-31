#!/usr/bin/env python3
"""Quick start script for the General Purpose Agent."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check credentials
required_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_DEPLOYMENT_NAME"
]

missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    print("❌ Missing required environment variables:")
    for var in missing:
        print(f"   - {var}")
    print("\n📝 Please:")
    print("   1. Copy .env.example to .env")
    print("   2. Add your Azure OpenAI credentials")
    print("   3. Run this script again")
    sys.exit(1)

print("✅ Environment variables loaded\n")

# Import agent
from src.agent import GeneralPurposeAgent

print("="*70)
print("  GENERAL PURPOSE AGENT - QUICK START")
print("="*70)

# Create agent
print("\n🤖 Initializing agent...")
agent = GeneralPurposeAgent(verbose=True)

print("\n✅ Agent initialized successfully!")
print("\n" + "="*70)

# Example task
goal = """Create a simple Python script called 'demo.py' that prints 'Hello from Agent!'"""

print(f"\n🎯 GOAL: {goal}")
print("\n" + "="*70)

try:
    evaluation = agent.run(goal)

    print("\n" + "="*70)
    print("  FINAL RESULTS")
    print("="*70)
    print(f"\n✅ Overall Success: {evaluation.overall_success}")
    print(f"📊 Overall Score: {evaluation.overall_score:.2f}")
    print(f"\n📝 Summary: {evaluation.summary}")

    if evaluation.strengths:
        print(f"\n💪 Strengths:")
        for strength in evaluation.strengths:
            print(f"   • {strength}")

    if evaluation.weaknesses:
        print(f"\n⚠️  Weaknesses:")
        for weakness in evaluation.weaknesses:
            print(f"   • {weakness}")

    if evaluation.lessons_learned:
        print(f"\n🎓 Lessons Learned:")
        for lesson in evaluation.lessons_learned:
            print(f"   • {lesson}")

    print("\n" + "="*70)
    print("\n🎉 Quick start completed!")
    print("\n💡 Next steps:")
    print("   1. Check out examples/example_usage.py for more examples")
    print("   2. Read docs/GETTING_STARTED.md for setup guide")
    print("   3. Explore docs/USAGE_GUIDE.md for patterns")
    print("   4. Try creating your own custom tools")
    print("\n" + "="*70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Verify your Azure OpenAI credentials in .env")
    print("   2. Check your API deployment name")
    print("   3. Ensure your API has function calling enabled")
    sys.exit(1)
