"""YouTube Automation Main Interface"""

import sys
from typing import Dict, Any
from langchain_core.messages import BaseMessage

from .tui.youtube_ui import YouTubeUI
from .graph.youtube_graph import run_youtube_automation
from .states.youtube_state import YouTubeAutomationState


class YouTubeAutomationInterface:
    """Main interface for YouTube content automation"""
    
    def __init__(self):
        self.ui = YouTubeUI()
    
    def run(self):
        """Run the YouTube automation interface"""
        try:
            # Display welcome
            self.ui.display_welcome()
            
            # Get workflow configuration
            config = self.ui.get_workflow_config()
            if not config:
                self.ui.console.print("[yellow]👋 Automation cancelled.[/yellow]")
                return
            
            # Select models
            models = self.ui.select_models()
            if not models:
                self.ui.display_error("No AI models selected. Please configure API keys and try again.")
                return
            
            # Display summary and confirm
            if not self.ui.display_workflow_summary(config, models):
                self.ui.console.print("[yellow]👋 Automation cancelled.[/yellow]")
                return
            
            # Run the workflow
            self.run_workflow(config, models)
            
        except KeyboardInterrupt:
            self.ui.console.print("\n[yellow]👋 Automation interrupted by user.[/yellow]")
        except Exception as e:
            self.ui.display_error(f"Unexpected error: {str(e)}")
            if self.ui.ask_continue_after_error():
                self.run()
    
    def run_workflow(self, config: Dict[str, Any], models: Dict[str, str]):
        """Execute the YouTube automation workflow"""
        try:
            # Prepare workflow parameters
            workflow_params = {
                "channel_url": config["channel_url"],
                "niche": config["niche"], 
                "target_audience": config["target_audience"],
                "content_goals": config["content_goals"],
                "models": models,
                "tools_enabled": config["tools_enabled"],
                "max_steps": 8,
                "ui": self.ui
            }
            
            # Track workflow state
            final_state = None
            step_count = 0
            
            # Phase names for progress display
            phase_names = [
                "Content Research & Competitor Analysis",
                "Market Analysis & Trend Identification", 
                "Content Ideation & Script Creation",
                "Thumbnail Design & Visual Concepts",
                "SEO & Optimization Strategies",
                "Content Calendar & Scheduling",
                "Final Recommendations & Action Plan"
            ]
            
            # Run the workflow with streaming updates
            for state_update in run_youtube_automation(**workflow_params):
                final_state = state_update
                
                # Update progress if step changed
                if state_update.get("step_count", 0) > step_count:
                    step_count = state_update["step_count"]
                    current_agent = state_update.get("current_agent", "system")
                    
                    # Display progress for new steps
                    if step_count <= len(phase_names):
                        phase_name = phase_names[step_count - 1]
                        self.ui.display_workflow_progress(
                            step_count, 
                            len(phase_names), 
                            current_agent,
                            phase_name
                        )
            
            # Handle workflow completion
            if final_state:
                if final_state.get("workflow_status") == "completed":
                    self.handle_successful_completion(final_state, config)
                elif final_state.get("workflow_status") == "error":
                    error_messages = final_state.get("error_messages", ["Unknown error"])
                    self.ui.display_error(f"Workflow failed: {'; '.join(error_messages)}")
                    if self.ui.ask_continue_after_error():
                        self.run()
                else:
                    self.ui.display_error("Workflow completed with unknown status")
            else:
                self.ui.display_error("Workflow did not complete properly")
                
        except Exception as e:
            self.ui.display_error(f"Workflow execution error: {str(e)}")
            if self.ui.ask_continue_after_error():
                self.run()
    
    def handle_successful_completion(self, final_state: YouTubeAutomationState, config: Dict[str, Any]):
        """Handle successful workflow completion"""
        # Display results summary
        self.ui.display_results_summary(final_state)
        
        # Offer export options
        export_choice = self.ui.offer_export_options()
        
        if export_choice == "view":
            self.ui.display_detailed_results(final_state.get("messages", []))
            
        elif export_choice == "export":
            markdown_content = self.ui.export_to_markdown(
                final_state.get("messages", []), 
                config
            )
            self.ui.save_markdown_file(markdown_content)
            
        elif export_choice == "clipboard":
            self.copy_summary_to_clipboard(final_state, config)
            
        # Ask if user wants to run another automation
        if self.ui.console.input("\n[blue]Press Enter to exit or 'r' to run another automation: [/blue]").lower() == 'r':
            self.ui.console.print("\n" + "="*60 + "\n")
            self.run()
    
    def copy_summary_to_clipboard(self, final_state: YouTubeAutomationState, config: Dict[str, Any]):
        """Copy a summary to clipboard"""
        try:
            import pyperclip
            
            summary = f"""YouTube Automation Results Summary:

Channel: {config.get('channel_url', 'Unknown')}
Niche: {config.get('niche', 'Unknown')}
Goals: {', '.join(config.get('content_goals', []))}

Results:
- Content Ideas: {len(final_state.get('content_ideas', []))}
- Video Scripts: {len(final_state.get('video_scripts', []))}
- Thumbnail Concepts: {len(final_state.get('thumbnail_concepts', []))}
- SEO Recommendations: Included
- Content Calendar: Included

Complete detailed results available in the full export."""
            
            pyperclip.copy(summary)
            self.ui.console.print("[green]✅ Summary copied to clipboard![/green]")
            
        except ImportError:
            self.ui.console.print("[yellow]⚠️  pyperclip not available. Install with: pip install pyperclip[/yellow]")
        except Exception as e:
            self.ui.display_error(f"Failed to copy to clipboard: {str(e)}")


def main():
    """Main entry point for YouTube automation"""
    try:
        automation = YouTubeAutomationInterface()
        automation.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()