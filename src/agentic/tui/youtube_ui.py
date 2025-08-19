"""Rich TUI components for YouTube automation interface"""

from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.columns import Columns

from ..llm.models import get_available_models, LLMModel


class YouTubeUI:
    """Rich-based UI for YouTube automation workflow"""
    
    def __init__(self):
        self.console = Console()
    
    def display_welcome(self):
        """Display welcome message for YouTube automation"""
        welcome_text = """
# 🎬 YouTube Content Automation AI

Welcome to your AI-powered YouTube content creation assistant! This system will help you:

- 🔍 **Research** trending topics and competitor analysis
- 📝 **Create** engaging video scripts and content ideas  
- 🎨 **Design** compelling thumbnail concepts
- 📊 **Optimize** for SEO and YouTube algorithm
- 📅 **Plan** content calendar and posting schedule

Let's get started by configuring your automation workflow!
        """
        
        self.console.print(Panel(
            Markdown(welcome_text.strip()),
            title="YouTube Content Automation",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def get_workflow_config(self) -> Dict[str, any]:
        """Get workflow configuration from user"""
        self.console.print("\n[bold blue]📋 Workflow Configuration[/bold blue]\n")
        
        # Get channel URL
        channel_url = Prompt.ask(
            "[yellow]📺 Enter your YouTube channel URL[/yellow]",
            default="https://youtube.com/@example"
        )
        
        # Get niche/topic
        niche = Prompt.ask(
            "[yellow]🎯 What's your content niche/topic?[/yellow]",
            default="tech reviews"
        )
        
        # Get target audience
        target_audience = Prompt.ask(
            "[yellow]👥 Describe your target audience[/yellow]",
            default="tech enthusiasts aged 18-35"
        )
        
        # Get content goals
        goals_options = [
            "Increase subscribers",
            "Improve video views", 
            "Create viral content",
            "Better SEO optimization",
            "Consistent content schedule",
            "Higher engagement rate"
        ]
        
        # Use Rich for multiple selection
        self.console.print("\n[bold yellow]🎯 Select your main content goals (enter numbers separated by commas):[/bold yellow]")
        
        for i, goal in enumerate(goals_options, 1):
            self.console.print(f"  {i}. {goal}")
        
        selected_goals = []
        while not selected_goals:
            choices_input = Prompt.ask("\nEnter your choices (e.g., 1,3,5)", default="1,2")
            try:
                choice_indices = [int(x.strip()) for x in choices_input.split(',')]
                selected_goals = [goals_options[i-1] for i in choice_indices if 1 <= i <= len(goals_options)]
                if not selected_goals:
                    self.console.print("[red]Please select at least one valid goal.[/red]")
            except (ValueError, IndexError):
                self.console.print("[red]Please enter valid numbers separated by commas.[/red]")
        
        # Get tools preference
        tools_enabled = Confirm.ask("🛠️  Enable web search tools for real-time research?", default=True)
        
        # Get competitor URLs (optional)
        competitor_urls = []
        if Confirm.ask("🎯 Do you want to provide specific competitor YouTube channel URLs for analysis?", default=False):
            self.console.print("\n[bold yellow]Enter competitor YouTube channel URLs (press Enter with empty input to finish):[/bold yellow]")
            
            while len(competitor_urls) < 5:  # Limit to 5 competitors
                url = Prompt.ask(f"Competitor {len(competitor_urls) + 1} URL (or press Enter to finish)", default="")
                if not url.strip():
                    break
                if 'youtube.com' in url.lower():
                    competitor_urls.append(url.strip())
                    self.console.print(f"[green]✅ Added: {url.strip()}[/green]")
                else:
                    self.console.print("[red]⚠️  Please enter a valid YouTube channel URL[/red]")
            
            if competitor_urls:
                self.console.print(f"\n[green]✅ Added {len(competitor_urls)} competitor(s) for analysis[/green]")
        
        return {
            "channel_url": channel_url,
            "niche": niche,
            "target_audience": target_audience,
            "content_goals": selected_goals,
            "tools_enabled": tools_enabled,
            "competitor_urls": competitor_urls
        }
    
    def select_agents_and_models(self) -> Tuple[Dict[str, bool], Dict[str, str]]:
        """Let user select which agents to use and their models"""
        self.console.print("\n[bold blue]🤖 Agent & Model Selection[/bold blue]\n")
        
        available_models = get_available_models()
        if not available_models:
            self.console.print("[red]❌ No AI models available. Please configure API keys.[/red]")
            return {}, {}
        
        model_choices = [(f"{model.display_name} ({model.provider.value})", model.model_name) 
                        for model in available_models]
        
        agents = {
            "competitor_analyst": "🎯 Competitor Analyst (analyzes competitor strategies) [NEW]",
            "researcher": "🔍 Content Researcher (finds trends and opportunities)",
            "writer": "📝 Script Writer (creates video scripts)", 
            "designer": "🎨 Thumbnail Creator (designs thumbnail concepts)",
            "analyst": "📊 Analytics Processor (optimization and planning)"
        }
        
        # First, let user select which agents to use
        self.console.print("[bold yellow]Select which agents you want to include in your workflow:[/bold yellow]\n")
        
        for i, (agent_key, agent_desc) in enumerate(agents.items(), 1):
            self.console.print(f"  {i}. {agent_desc}")
        
        selected_agents = {}
        while not selected_agents:
            choices_input = Prompt.ask(
                "\nEnter agent numbers you want to use (e.g., 1,2,3)", 
                default="1,2,3,4,5"
            )
            try:
                choice_indices = [int(x.strip()) for x in choices_input.split(',')]
                agent_keys = list(agents.keys())
                selected_agents = {
                    agent_keys[i-1]: True 
                    for i in choice_indices 
                    if 1 <= i <= len(agents)
                }
                if not selected_agents:
                    self.console.print("[red]Please select at least one valid agent.[/red]")
            except (ValueError, IndexError):
                self.console.print("[red]Please enter valid numbers separated by commas.[/red]")
        
        # Then select models for selected agents
        self.console.print("\n[bold blue]Now select AI models for your chosen agents:[/bold blue]\n")
        
        selected_models = {}
        for agent_key in selected_agents.keys():
            agent_desc = agents[agent_key]
            self.console.print(f"\n[bold cyan]Select model for {agent_desc}:[/bold cyan]")
            
            for i, (display_name, model_name) in enumerate(model_choices, 1):
                self.console.print(f"  {i}. {display_name}")
            
            while True:
                try:
                    choice_num = int(Prompt.ask("Enter your choice", default="1"))
                    if 1 <= choice_num <= len(model_choices):
                        selected_models[agent_key] = model_choices[choice_num - 1][1]
                        break
                    else:
                        self.console.print("[red]Please enter a valid choice number.[/red]")
                except ValueError:
                    self.console.print("[red]Please enter a valid number.[/red]")
        
        return selected_agents, selected_models
    
    def display_workflow_summary(self, config: Dict[str, any], selected_agents: Dict[str, bool], models: Dict[str, str]):
        """Display workflow configuration summary"""
        # Create model summary
        model_info = []
        agent_names = {
            "competitor_analyst": "Competitor Analyst",
            "researcher": "Content Researcher", 
            "writer": "Script Writer",
            "designer": "Thumbnail Creator",
            "analyst": "Analytics Processor"
        }
        
        for agent, model in models.items():
            available_models = get_available_models()
            model_obj = next((m for m in available_models if m.model_name == model), None)
            display_name = model_obj.display_name if model_obj else model
            agent_display = agent_names.get(agent, agent.title())
            model_info.append(f"**{agent_display}**: {display_name}")
        
        active_agents = [agent_names.get(k, k.title()) for k, v in selected_agents.items() if v]
        
        # Competitor URLs section
        competitor_section = ""
        if config.get('competitor_urls'):
            competitor_list = '\n'.join([f"- {url}" for url in config['competitor_urls']])
            competitor_section = f"""
## 🎯 Competitor Analysis

**Provided Competitors**: {len(config['competitor_urls'])} channels
{competitor_list}
"""

        summary_text = f"""
## 🎬 Workflow Configuration

**📺 Channel**: {config['channel_url']}
**🎯 Niche**: {config['niche']}
**👥 Audience**: {config['target_audience']}
**🎯 Goals**: {', '.join(config['content_goals'])}
**🛠️ Tools**: {'Enabled' if config['tools_enabled'] else 'Disabled'}
{competitor_section}
## 🤖 Active Agents

{', '.join(active_agents)}

## 🤖 AI Models

{chr(10).join(model_info)}

The workflow will run through multiple phases using your selected agents to create a comprehensive YouTube content strategy.
        """
        
        self.console.print(Panel(
            Markdown(summary_text.strip()),
            title="Configuration Summary",
            border_style="green",
            padding=(1, 2)
        ))
        
        return Confirm.ask("🚀 Ready to start the automation workflow?", default=True)
    
    def display_workflow_progress(self, step: int, total_steps: int, current_agent: str, phase_name: str):
        """Display current workflow progress"""
        progress_text = f"Step {step}/{total_steps}: {phase_name}"
        agent_icons = {
            "researcher": "🔍",
            "writer": "📝", 
            "designer": "🎨",
            "analyst": "📊"
        }
        
        icon = agent_icons.get(current_agent, "🤖")
        
        self.console.print(f"\n{icon} [bold blue]{progress_text}[/bold blue]")
        self.console.print("─" * 60)
    
    def display_results_summary(self, final_state: Dict[str, any]):
        """Display final results summary"""
        content_ideas_count = len(final_state.get('content_ideas', []))
        scripts_count = len(final_state.get('video_scripts', []))
        thumbnails_count = len(final_state.get('thumbnail_concepts', []))
        
        summary_text = f"""
# 🎉 YouTube Automation Complete!

## 📊 Generated Content

- **📝 Content Ideas**: {content_ideas_count} unique video concepts
- **🎬 Video Scripts**: {scripts_count} complete scripts with hooks and CTAs
- **🎨 Thumbnail Concepts**: {thumbnails_count} design concepts ready for creation
- **📅 Content Calendar**: Strategic posting schedule included
- **📈 SEO Recommendations**: Optimization strategies provided

## ✨ What You Received

✅ **Market Research**: Competitor analysis and trend insights
✅ **Content Strategy**: Data-driven video ideas and topics  
✅ **Production Ready**: Complete scripts with timing and structure
✅ **Visual Concepts**: Professional thumbnail design descriptions
✅ **Growth Plan**: SEO, scheduling, and optimization strategies
✅ **Action Items**: Clear next steps and implementation timeline

Your YouTube content automation is ready to implement!
        """
        
        self.console.print(Panel(
            Markdown(summary_text.strip()),
            title="Results Summary",
            border_style="green",
            padding=(1, 2)
        ))
    
    def offer_export_options(self) -> str:
        """Offer export options for the results"""
        export_choices = [
            ("📊 View comprehensive report", "report"),
            ("📄 View detailed results in terminal", "view"),
            ("💾 Export to markdown file", "export"),
            ("📋 Copy to clipboard (summary)", "clipboard"),
            ("❌ No export needed", "none")
        ]
        
        self.console.print("\n[bold cyan]What would you like to do with your results?[/bold cyan]")
        
        for i, (label, value) in enumerate(export_choices, 1):
            self.console.print(f"  {i}. {label}")
        
        while True:
            try:
                choice_num = int(Prompt.ask("Enter your choice", default="1"))
                if 1 <= choice_num <= len(export_choices):
                    choice = export_choices[choice_num - 1][1]
                    break
                else:
                    self.console.print("[red]Please enter a valid choice number.[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")
        
        return choice
    
    def display_detailed_results(self, messages: List[any]):
        """Display detailed results from all agents"""
        self.console.print("\n[bold blue]📊 Detailed Results[/bold blue]\n")
        
        for i, message in enumerate(messages):
            if hasattr(message, 'content') and message.content:
                # Try to identify the agent based on content
                content = message.content
                
                if "Research" in content or "Competitor" in content:
                    title = "🔍 Content Research Results"
                    style = "blue"
                elif "Script" in content or "Hook" in content:
                    title = "📝 Script Writing Results"
                    style = "yellow"
                elif "Thumbnail" in content or "Design" in content:
                    title = "🎨 Thumbnail Design Results"
                    style = "magenta"
                elif "Analytics" in content or "SEO" in content:
                    title = "📊 Analytics & Optimization Results"
                    style = "green"
                else:
                    title = f"📋 Agent Response {i+1}"
                    style = "white"
                
                self.console.print(Panel(
                    content,
                    title=title,
                    border_style=style,
                    padding=(1, 2)
                ))
                self.console.print()
    
    def export_to_markdown(self, messages: List[any], config: Dict[str, any]) -> str:
        """Export results to markdown format"""
        from datetime import datetime
        
        markdown_content = f"""# YouTube Content Automation Results

**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Channel**: {config.get('channel_url', 'Unknown')}
**Niche**: {config.get('niche', 'Unknown')}
**Target Audience**: {config.get('target_audience', 'Unknown')}
**Goals**: {', '.join(config.get('content_goals', []))}

---

"""
        
        section_titles = [
            "## 🔍 Content Research & Analysis",
            "## 📊 Market Analysis & Opportunities", 
            "## 📝 Content Ideas & Video Scripts",
            "## 🎨 Thumbnail Design Concepts",
            "## 📈 SEO & Optimization Strategies",
            "## 📅 Content Calendar & Schedule",
            "## 💡 Final Recommendations"
        ]
        
        for i, message in enumerate(messages):
            if hasattr(message, 'content') and message.content:
                if i < len(section_titles):
                    markdown_content += f"\n{section_titles[i]}\n\n"
                
                markdown_content += message.content + "\n\n---\n\n"
        
        return markdown_content
    
    def save_markdown_file(self, content: str, filename: str = None) -> str:
        """Save markdown content to file"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"youtube_automation_results_{timestamp}.md"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.console.print(f"[green]✅ Results exported to: {filename}[/green]")
            return filename
            
        except Exception as e:
            self.console.print(f"[red]❌ Error saving file: {str(e)}[/red]")
            return ""
    
    def display_error(self, error_msg: str):
        """Display error message"""
        self.console.print(Panel(
            f"[red]❌ {error_msg}[/red]",
            title="Error",
            border_style="red"
        ))
    
    def ask_continue_after_error(self) -> bool:
        """Ask user if they want to continue after an error"""
        return Confirm.ask(
            "An error occurred. Would you like to try again with different settings?",
            default=False
        )