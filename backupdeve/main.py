#!/usr/bin/env python3
"""
Norskord - Norwegian Language Learning Game
Main entry point - modular version of ma.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point"""
    print("🇳🇴 Starting Norskord - Norwegian Language Learning Game")
    
    try:
        from game_engine import DuolingoStyleDictationGame
        
        # Initialize and run the game
        game = DuolingoStyleDictationGame()
        game.run()
        
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())