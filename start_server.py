#!/usr/bin/env python3
"""
Start the Agent Web Server

This script starts the web server with both chat and dashboard interfaces.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def check_environment():
    """Check if environment variables are set."""
    required_vars = [
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    print("\n" + "=" * 70)
    print("🚀 Agent Web Server")
    print("=" * 70)

    if missing_vars:
        print("\n⚠️  Warning: Running in DEMO MODE")
        print("   Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n   💡 To enable full functionality:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Azure OpenAI credentials")
        print("   3. Restart this server")
    else:
        print("\n✅ Azure OpenAI configured - Full functionality enabled")

    print("\n📍 Server URLs:")
    print("   • Chat Interface:      http://localhost:8000")
    print("   • Dashboard Interface: http://localhost:8000/dashboard")
    print("   • Health Check:        http://localhost:8000/health")
    print("\n⌨️  Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")


def main():
    """Main entry point."""
    try:
        from dotenv import load_dotenv
        load_dotenv()

        check_environment()

        import uvicorn
        from src.web_ui.app import app

        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )

    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
