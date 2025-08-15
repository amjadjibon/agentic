import os
import sys
from typing import Literal
from .conversations import run_political_debate_with_models, run_political_discussion_with_models, run_policy_analysis_with_models


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the debate AI header"""
    print("=" * 70)
    print("🗳️  POLITICAL DEBATE AI  🗳️")
    print("=" * 70)
    print("Engage in structured political debates between progressive and conservative perspectives")
    print("=" * 70)


def print_model_options():
    """Print available model options"""
    print("\nAvailable Models:")
    print("1. OpenAI GPT-4o")
    print("2. Google Gemini 1.5 Pro")


def get_model_choice(side: str) -> Literal["openai", "gemini"]:
    """Get model choice for a specific side"""
    while True:
        print(f"\nChoose model for {side.upper()} side:")
        print_model_options()
        choice = input(f"Enter choice for {side} (1 for OpenAI, 2 for Gemini): ").strip()
        
        if choice == "1":
            return "openai"
        elif choice == "2":
            return "gemini"
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")


def get_debate_topic() -> str:
    """Get debate topic from user"""
    while True:
        topic = input("\n📝 Enter debate topic: ").strip()
        if topic:
            return topic
        print("❌ Please enter a valid topic.")


def get_max_turns() -> int:
    """Get maximum number of turns from user"""
    while True:
        try:
            turns = input("\n🔄 Enter maximum number of turns (default: 8): ").strip()
            if not turns:
                return 8
            turns_int = int(turns)
            if turns_int > 0:
                return turns_int
            else:
                print("❌ Please enter a positive number.")
        except ValueError:
            print("❌ Please enter a valid number.")


def get_debate_type() -> int:
    """Get type of debate from user"""
    while True:
        print("\n🎯 Choose debate type:")
        print("1. 🗳️  Political Debate (Structured argument format)")
        print("2. 💬 Political Discussion (General discussion)")
        print("3. 📋 Policy Analysis (Deep policy analysis)")
        print("4. 🚪 Exit")
        
        try:
            choice = int(input("Enter your choice (1-4): ").strip())
            if 1 <= choice <= 4:
                return choice
            else:
                print("❌ Please enter a number between 1-4.")
        except ValueError:
            print("❌ Please enter a valid number.")


def confirm_setup(topic: str, left_model: str, right_model: str, max_turns: int, debate_type: str) -> bool:
    """Confirm debate setup with user"""
    print("\n" + "=" * 50)
    print("📋 DEBATE SETUP CONFIRMATION")
    print("=" * 50)
    print(f"🎯 Topic: {topic}")
    print(f"🔴 Left (Progressive): {left_model.upper()}")
    print(f"🔵 Right (Conservative): {right_model.upper()}")
    print(f"🔄 Max Turns: {max_turns}")
    print(f"📝 Type: {debate_type}")
    print("=" * 50)
    
    while True:
        confirm = input("Start debate? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            return True
        elif confirm in ['n', 'no']:
            return False
        else:
            print("❌ Please enter 'y' or 'n'.")


def show_progress(current_turn: int, max_turns: int):
    """Show debate progress"""
    progress = "█" * current_turn + "░" * (max_turns - current_turn)
    print(f"\n📊 Progress: [{progress}] {current_turn}/{max_turns}")


def run_terminal_ui():
    """Run the terminal UI for political debates"""
    try:
        while True:
            clear_screen()
            print_header()
            
            # Check for API keys
            if not os.getenv("OPENAI_API_KEY"):
                print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
            if not os.getenv("GOOGLE_API_KEY"):
                print("⚠️  Warning: GOOGLE_API_KEY not found in environment variables")
            
            # Get debate type
            debate_type_num = get_debate_type()
            
            if debate_type_num == 4:  # Exit
                print("\n👋 Thanks for using Political Debate AI!")
                break
            
            debate_types = {
                1: "Political Debate",
                2: "Political Discussion", 
                3: "Policy Analysis"
            }
            debate_type = debate_types[debate_type_num]
            
            # Get debate configuration
            topic = get_debate_topic()
            left_model = get_model_choice("left")
            right_model = get_model_choice("right")
            max_turns = get_max_turns()
            
            # Confirm setup
            if not confirm_setup(topic, left_model, right_model, max_turns, debate_type):
                input("\nPress Enter to continue...")
                continue
            
            # Start debate
            clear_screen()
            print("🚀 Starting debate...")
            print(f"🎯 Topic: {topic}")
            print(f"🔴 Left: {left_model.upper()} | 🔵 Right: {right_model.upper()}")
            print("=" * 70)
            
            try:
                # Run appropriate debate type
                if debate_type_num == 1:
                    run_political_debate_with_models(topic, left_model, right_model, max_turns)
                elif debate_type_num == 2:
                    run_political_discussion_with_models(topic, left_model, right_model, max_turns)
                elif debate_type_num == 3:
                    run_policy_analysis_with_models(topic, left_model, right_model, max_turns)
                
                print("\n" + "=" * 70)
                print("🏁 Debate completed!")
                print("=" * 70)
                
            except KeyboardInterrupt:
                print("\n\n⏹️  Debate interrupted by user.")
            except Exception as e:
                print(f"\n❌ Error during debate: {str(e)}")
            
            # Ask if user wants another debate
            while True:
                another = input("\nStart another debate? (y/n): ").strip().lower()
                if another in ['y', 'yes']:
                    break
                elif another in ['n', 'no']:
                    print("\n👋 Thanks for using Political Debate AI!")
                    return
                else:
                    print("❌ Please enter 'y' or 'n'.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
