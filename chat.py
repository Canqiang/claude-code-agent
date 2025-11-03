#!/usr/bin/env python3
"""
Chat CLI - Interactive chat interface for the Agent system.
Similar to Claude Code's conversational interface.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from src.agent import GeneralPurposeAgent
from src.streaming import StreamHandler, StreamEvent, StreamEventType

# Load environment variables
load_dotenv()


class ChatSession:
    """Manage a chat session with the agent."""

    def __init__(self):
        self.agent = None
        self.stream_handler = StreamHandler()
        self.conversation_history: List[Dict[str, str]] = []
        self.is_configured = self.check_configuration()

    def check_configuration(self) -> bool:
        """Check if Azure OpenAI is configured."""
        has_api_key = bool(os.getenv('AZURE_OPENAI_API_KEY'))
        has_endpoint = bool(os.getenv('AZURE_OPENAI_ENDPOINT'))
        has_deployment = bool(os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'))
        return has_api_key and has_endpoint and has_deployment

    def print_header(self):
        """Print chat header."""
        print("\n" + "=" * 70)
        print("🤖 Agent Chat - Interactive AI Assistant")
        print("=" * 70)

        if self.is_configured:
            print("✅ Azure OpenAI configured - Full functionality enabled")
        else:
            print("⚠️  Demo Mode - Configure .env file for full functionality")

        print("\nCommands:")
        print("  /help     - Show this help message")
        print("  /clear    - Clear conversation history")
        print("  /history  - Show conversation history")
        print("  /exit     - Exit the chat")
        print("  /quit     - Exit the chat")
        print("\nType your message and press Enter. Use Ctrl+C to exit anytime.")
        print("=" * 70 + "\n")

    def print_message(self, role: str, content: str, timestamp: str = None):
        """Print a formatted message."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")

        if role == "user":
            print(f"\n💬 You [{timestamp}]")
            print(f"   {content}")
        elif role == "assistant":
            print(f"\n🤖 Assistant [{timestamp}]")
            print(f"   {content}")
        elif role == "system":
            print(f"\n📌 System [{timestamp}]")
            print(f"   {content}")
        elif role == "error":
            print(f"\n❌ Error [{timestamp}]")
            print(f"   {content}")

    def print_streaming_event(self, event: StreamEvent):
        """Print a streaming event."""
        event_symbols = {
            StreamEventType.START: "🚀",
            StreamEventType.PLANNING: "🎯",
            StreamEventType.THINKING: "🤔",
            StreamEventType.EXECUTION: "⚙️",
            StreamEventType.TOOL_CALL: "🔧",
            StreamEventType.EVALUATION: "📊",
            StreamEventType.COMPLETE: "✅",
            StreamEventType.ERROR: "❌",
            StreamEventType.PROGRESS: "📈"
        }

        symbol = event_symbols.get(event.type, "•")

        if event.type == StreamEventType.PROGRESS:
            percentage = event.data.get('percentage', 0)
            message = event.data.get('message', '')
            print(f"   {symbol} {message} ({percentage}%)")
        elif event.type == StreamEventType.COMPLETE:
            print(f"\n   {symbol} Task completed!")
        else:
            # For other events, print the data
            if isinstance(event.data, str):
                print(f"   {symbol} {event.data}")
            elif isinstance(event.data, dict):
                message = event.data.get('message', '')
                if message:
                    print(f"   {symbol} {message}")

    def handle_command(self, command: str) -> bool:
        """Handle special commands. Returns True if should continue, False if should exit."""
        command = command.strip().lower()

        if command in ['/exit', '/quit']:
            print("\n👋 Goodbye! Thanks for chatting.")
            return False

        elif command == '/help':
            self.print_header()

        elif command == '/clear':
            self.conversation_history = []
            print("\n🗑️  Conversation history cleared.")

        elif command == '/history':
            if not self.conversation_history:
                print("\n📭 No conversation history yet.")
            else:
                print("\n📜 Conversation History:")
                print("-" * 70)
                for i, msg in enumerate(self.conversation_history, 1):
                    role_display = "You" if msg['role'] == 'user' else "Assistant"
                    timestamp = msg.get('timestamp', 'N/A')
                    print(f"{i}. [{timestamp}] {role_display}:")
                    print(f"   {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
                print("-" * 70)

        else:
            print(f"\n❓ Unknown command: {command}")
            print("   Type /help to see available commands.")

        return True

    def process_user_message(self, user_input: str):
        """Process user message and get agent response."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Add to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': timestamp
        })

        # Print user message
        self.print_message("user", user_input, timestamp)

        try:
            # Classify query to determine response strategy using LLM
            from src.utils.query_classifier import QueryClassifier
            from src.utils.llm_client import AzureOpenAIClient

            llm_client = None
            if self.is_configured:
                try:
                    llm_client = AzureOpenAIClient()
                except Exception as e:
                    print(f"Failed to initialize LLM client for classification: {e}")

            classifier = QueryClassifier(llm_client=llm_client)
            classification = classifier.classify(user_input)

            # Handle simple queries with quick responses
            if not classification["use_full_workflow"]:
                quick_response = classifier.get_quick_response(user_input, classification)

                if quick_response:
                    response = quick_response
                elif not self.is_configured:
                    response = self.get_demo_response(user_input)
                else:
                    response = self.get_agent_response(user_input)
            elif not self.is_configured:
                # Demo mode response for complex tasks
                response = self.get_demo_response(user_input)
            else:
                # Real agent response for complex tasks
                response = self.get_agent_response(user_input)

            # Add response to history
            response_timestamp = datetime.now().strftime("%H:%M:%S")
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': response_timestamp
            })

            # Print assistant response
            self.print_message("assistant", response, response_timestamp)

        except KeyboardInterrupt:
            print("\n\n⚠️  Task interrupted by user.")
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.print_message("error", error_msg)

    def get_demo_response(self, user_input: str) -> str:
        """Get a demo response (when not configured)."""
        import time

        print("\n🤖 Assistant [Processing...]")

        # Simulate streaming
        events = [
            ("🎯", "Planning task...", 0.3),
            ("🤔", "Analyzing request...", 0.3),
            ("⚙️", "Generating response...", 0.3),
            ("✅", "Complete!", 0.2)
        ]

        for symbol, message, delay in events:
            print(f"   {symbol} {message}")
            time.sleep(delay)

        # Generate demo response
        response = f"""I understand you want to: "{user_input}"

⚠️  Demo Mode Active: I'm currently running in demo mode because Azure OpenAI credentials are not configured.

To enable full functionality:
1. Copy .env.example to .env
2. Add your Azure OpenAI credentials
3. Restart this chat session

In real mode, I would:
- Analyze your request thoroughly
- Break it down into actionable steps
- Execute tasks using available tools
- Provide detailed results and evaluation

Would you like me to explain more about what I can do once configured?"""

        return response

    def get_agent_response(self, user_input: str) -> str:
        """Get response from the real agent."""
        print("\n🤖 Assistant [Processing...]")

        # Subscribe to streaming events
        def on_event(event: StreamEvent):
            self.print_streaming_event(event)

        self.stream_handler.subscribe(on_event)

        # Create agent if not exists
        if self.agent is None:
            self.agent = GeneralPurposeAgent(verbose=False)

        # Build context from conversation history
        context = self.build_context()

        # Run agent with streaming simulation
        self.stream_handler.emit_start(user_input)
        self.stream_handler.emit_planning("Analyzing your request...")
        self.stream_handler.emit_thinking("Planning approach...")

        # Execute task
        evaluation = self.agent.run(user_input, context=context)

        self.stream_handler.emit_progress("Task completed", 100)

        # Build response
        response = f"{evaluation.summary}"

        if evaluation.overall_success:
            response += f"\n\n✅ Success (Score: {evaluation.overall_score:.2f})"
        else:
            response += f"\n\n⚠️  Completed with issues (Score: {evaluation.overall_score:.2f})"

        if evaluation.strengths:
            response += "\n\n💪 Strengths:"
            for strength in evaluation.strengths:
                response += f"\n  • {strength}"

        if evaluation.weaknesses:
            response += "\n\n⚠️  Areas for improvement:"
            for weakness in evaluation.weaknesses:
                response += f"\n  • {weakness}"

        return response

    def build_context(self) -> str:
        """Build context from conversation history."""
        if not self.conversation_history:
            return ""

        context = "Previous conversation:\n"
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = "User" if msg['role'] == 'user' else "Assistant"
            context += f"{role}: {msg['content']}\n"

        return context

    def run(self):
        """Run the chat loop."""
        self.print_header()

        while True:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()

                # Skip empty input
                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    should_continue = self.handle_command(user_input)
                    if not should_continue:
                        break
                    continue

                # Process normal message
                self.process_user_message(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for chatting.")
                break
            except EOFError:
                print("\n\n👋 Goodbye! Thanks for chatting.")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("   Type /exit to quit or continue chatting.")


def main():
    """Main entry point."""
    try:
        session = ChatSession()
        session.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
