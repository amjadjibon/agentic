import sys
from datetime import datetime

from agentic.graph.graph import run_streaming_debate, run_custom_streaming_debate
from agentic.graph.rap_battle_graph import run_rap_battle
from agentic.tui.rich_ui import DebateUI
from agentic.tui.markdown_formatter import MarkdownFormatter
from agentic.agents.rappers import get_available_rappers


def run_terminal_ui():
    """Run the Rich-enhanced terminal UI for political debates"""
    ui = DebateUI()
    
    try:
        while True:
            ui.clear_screen()
            ui.show_api_key_warnings()
            
            # Get debate type
            debate_type_num = ui.get_debate_type()
            
            if debate_type_num == 5:  # Exit
                ui.console.print("\n[bold green]👋 Thanks for using Agentic AI![/bold green]")
                break
            
            debate_types = {    
                1: "Debate",
                2: "Discussion", 
                3: "Analysis",
                4: "Rap Battle"
            }
            debate_type_str = debate_types[debate_type_num]
            
            # Handle rap battle vs regular debate
            if debate_type_num == 4:  # Rap Battle
                # Rap battle configuration
                topic = ui.get_battle_topic()
                rapper1_id = ui.get_rapper_choice("first")
                rapper2_id = ui.get_rapper_choice("second")
                model1 = ui.get_model_choice("rapper 1")
                model2 = ui.get_model_choice("rapper 2")
                max_rounds = ui.get_battle_rounds()
                tools_enabled = ui.get_tools_preference()
                judge_enabled = ui.get_judge_preference()
                judge_model = ui.get_judge_model_choice() if judge_enabled else None
                
                # Get rapper info for confirmation
                rappers = get_available_rappers()
                rapper1_info = rappers[rapper1_id]
                rapper2_info = rappers[rapper2_id]
                
                # Confirm rap battle setup
                if not ui.confirm_battle_setup(topic, rapper1_id, rapper2_id, model1, model2, max_rounds, tools_enabled, judge_enabled, judge_model):
                    ui.console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
                    continue
                
                # Start rap battle
                ui.clear_screen()
                ui.console.print("[bold magenta]🎤 STARTING RAP BATTLE...[/bold magenta]\n")
                ui.show_battle_header(topic, rapper1_info, rapper2_info, tools_enabled)
                
                try:
                    final_state = run_rap_battle(
                        topic, rapper1_id, rapper2_id, model1, model2, 
                        max_rounds, tools_enabled, ui, judge_enabled, 
                        judge_model or "openai-gpt4o-mini"
                    )
                    
                    # Battle completion message
                    ui.console.print("\n🏆 [bold green]RAP BATTLE COMPLETED![/bold green] 🏆")
                    
                except Exception as e:
                    ui.console.print(f"\n[red]❌ Error during rap battle: {str(e)}[/red]")
                    final_state = None
                
            else:
                # Regular debate configuration
                topic = ui.get_debate_topic()
                left_model = ui.get_model_choice("left")
                right_model = ui.get_model_choice("right")
                max_turns = ui.get_max_turns()
                tools_enabled = ui.get_tools_preference()
                judge_enabled = ui.get_judge_preference()
                judge_model = ui.get_judge_model_choice() if judge_enabled else None
                left_persona, right_persona = ui.get_custom_personas()
            
                # Confirm setup for regular debates
                if not ui.confirm_setup(topic, left_model, right_model, max_turns, debate_type_str, tools_enabled, left_persona, right_persona, judge_enabled, judge_model):
                    ui.console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
                    continue
                
                # Start debate
                ui.clear_screen()
                ui.console.print("[bold green]🚀 Starting debate...[/bold green]\n")
                
                try:
                    # Map debate type to internal string
                    debate_type_map = {
                        1: "debate",
                        2: "discussion", 
                        3: "policy"
                    }
                    debate_type = debate_type_map[debate_type_num]
                    
                    # Show debate header
                    ui.show_debate_header(topic, left_model, right_model, tools_enabled, debate_type)
                    
                    # Run appropriate debate type
                    if left_persona and right_persona:
                        final_state = run_custom_streaming_debate(topic, left_model, right_model, left_persona, right_persona, max_turns, tools_enabled, ui, judge_enabled, judge_model or "openai-gpt4o-mini")
                    else:
                        final_state = run_streaming_debate(topic, left_model, right_model, max_turns, tools_enabled, debate_type, ui, judge_enabled, judge_model or "openai-gpt4o-mini")
                    
                    # Show completion message
                    ui.show_completion_message(debate_type)
                
                except KeyboardInterrupt:
                    ui.console.print("\n\n[yellow]⏹️  Debate interrupted by user.[/yellow]")
                    final_state = None
                except Exception as e:
                    ui.console.print(f"\n[red]❌ Error during debate: {str(e)}[/red]")
                    final_state = None
            
            # Handle markdown export for both rap battles and debates
            if final_state and final_state.get("messages"):
                # Ask if user wants to view in markdown format
                if ui.ask_view_markdown():
                    formatter = MarkdownFormatter()
                    if debate_type_num == 4:  # Rap Battle
                        # For rap battles, we'll need a custom formatter (for now use debate format)
                        markdown_content = f"# Rap Battle: {topic}\n\n**Type:** Rap Battle\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## Battle Results\n\nRap battle content formatting coming soon..."
                    else:
                        markdown_content = formatter.format_debate(
                            topic, left_model, right_model, final_state, debate_type, tools_enabled, left_persona, right_persona, judge_enabled
                        )
                    ui.display_markdown_view(markdown_content)
                
                # Ask if user wants to export to file
                if ui.ask_markdown_export():
                    formatter = MarkdownFormatter()
                    if debate_type_num == 4:  # Rap Battle
                        # Simple export for rap battles (can be enhanced later)
                        ui.console.print("[yellow]🎤 Rap battle export format coming soon! Using basic format for now.[/yellow]")
                        filepath = f"rap_battle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                        with open(filepath, 'w') as f:
                            f.write(f"# Rap Battle: {topic}\n\nBattle completed successfully!")
                    else:
                        filepath = formatter.save_debate_markdown(
                            topic, left_model, right_model, final_state, debate_type, tools_enabled, left_persona, right_persona, judge_enabled=judge_enabled
                        )
                    ui.show_export_success(filepath)
            
            # Ask if user wants another debate
            if not ui.ask_continue():
                ui.console.print("\n[bold green]👋 Thanks for using Agentic AI![/bold green]")
                break
    
    except KeyboardInterrupt:
        ui.console.print("\n\n[bold green]👋 Goodbye![/bold green]")
    except Exception as e:
        ui.console.print(f"\n[red]❌ Unexpected error: {str(e)}[/red]")
        sys.exit(1)
