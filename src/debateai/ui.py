import sys
from .graph import run_streaming_debate, run_custom_streaming_debate
from .rich_ui import DebateUI
from .markdown_formatter import MarkdownFormatter


def run_terminal_ui():
    """Run the Rich-enhanced terminal UI for political debates"""
    ui = DebateUI()
    
    try:
        while True:
            ui.clear_screen()
            ui.show_api_key_warnings()
            
            # Get debate type
            debate_type_num = ui.get_debate_type()
            
            if debate_type_num == 4:  # Exit
                ui.console.print("\n[bold green]👋 Thanks for using Political Debate AI![/bold green]")
                break
            
            debate_types = {
                1: "Political Debate",
                2: "Political Discussion", 
                3: "Policy Analysis"
            }
            debate_type_str = debate_types[debate_type_num]
            
            # Get debate configuration
            topic = ui.get_debate_topic()
            left_model = ui.get_model_choice("left")
            right_model = ui.get_model_choice("right")
            max_turns = ui.get_max_turns()
            tools_enabled = ui.get_tools_preference()
            judge_enabled = ui.get_judge_preference()
            judge_model = ui.get_judge_model_choice() if judge_enabled else None
            left_persona, right_persona = ui.get_custom_personas()
            
            # Confirm setup
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
                
                # Offer markdown view and export options
                if final_state and final_state.get("messages"):
                    # Ask if user wants to view in markdown format
                    if ui.ask_view_markdown():
                        formatter = MarkdownFormatter()
                        markdown_content = formatter.format_debate(
                            topic, left_model, right_model, final_state, debate_type, tools_enabled, left_persona, right_persona, judge_enabled
                        )
                        ui.display_markdown_view(markdown_content)
                    
                    # Ask if user wants to export to file
                    if ui.ask_markdown_export():
                        formatter = MarkdownFormatter()
                        filepath = formatter.save_debate_markdown(
                            topic, left_model, right_model, final_state, debate_type, tools_enabled, left_persona, right_persona, judge_enabled=judge_enabled
                        )
                        ui.show_export_success(filepath)
                
            except KeyboardInterrupt:
                ui.console.print("\n\n[yellow]⏹️  Debate interrupted by user.[/yellow]")
            except Exception as e:
                ui.console.print(f"\n[red]❌ Error during debate: {str(e)}[/red]")
            
            # Ask if user wants another debate
            if not ui.ask_continue():
                ui.console.print("\n[bold green]👋 Thanks for using Political Debate AI![/bold green]")
                break
    
    except KeyboardInterrupt:
        ui.console.print("\n\n[bold green]👋 Goodbye![/bold green]")
    except Exception as e:
        ui.console.print(f"\n[red]❌ Unexpected error: {str(e)}[/red]")
        sys.exit(1)
