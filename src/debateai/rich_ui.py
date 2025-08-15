"""Rich-enhanced UI components for the debate AI system"""

import sys
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align
from rich import box
from rich.markdown import Markdown

from debateai.config import (
    get_available_models_list,
    validate_model_availability
)
from debateai.rappers import get_available_rappers
from debateai.rap_battle_graph import get_rap_battle_topic_suggestions


console = Console()


class DebateUIComponents:
    """Rich UI components for debate interface"""
    
    @staticmethod
    def create_header() -> Panel:
        """Create the main header panel"""
        title_text = Text("🗳️ POLITICAL DEBATE AI 🗳️", style="bold magenta")
        subtitle_text = Text("Engage in real-time political debates with AI agents", style="dim")
        header_content = Align.center(Text.assemble(title_text, "\n", subtitle_text))
        
        return Panel(
            header_content,
            box=box.DOUBLE,
            style="bright_blue",
            padding=(1, 2)
        )
    
    @staticmethod
    def create_model_selection_table() -> Table:
        """Create a table showing available models"""
        models = get_available_models_list()
        
        table = Table(title="Available Models", box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Model", style="white")
        table.add_column("Provider", style="yellow")
        table.add_column("Status", style="green")
        
        for i, model in enumerate(models, 1):
            status_color = "green" if model['available'] else "red"
            status_icon = "✅" if model['available'] else "❌"
            
            table.add_row(
                str(i),
                model['display_name'],
                model['provider'].upper(),
                f"[{status_color}]{status_icon} {'Available' if model['available'] else 'API Key Missing'}[/{status_color}]"
            )
        
        return table
    
    @staticmethod
    def create_debate_types_table() -> Table:
        """Create a table showing debate types"""
        table = Table(title="Debate Types", box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Type", style="white")
        table.add_column("Description", style="dim")
        
        debate_types = [
            ("1", "🗳️ Political Debate", "Structured argument format with opposing viewpoints"),
            ("2", "💬 Political Discussion", "General discussion and exchange of ideas"),
            ("3", "📋 Policy Analysis", "Deep analysis of policy implications"),
            ("4", "🎤 Rap Battle", "Epic rap battles between legendary artists"),
            ("5", "🚪 Exit", "Exit the application")
        ]
        
        for type_id, type_name, description in debate_types:
            table.add_row(type_id, type_name, description)
        
        return table
    
    @staticmethod
    def create_rapper_selection_table() -> Table:
        """Create a table showing available rappers"""
        rappers = get_available_rappers()
        
        table = Table(title="Available Rappers", box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Icon", style="white", no_wrap=True)
        table.add_column("Rapper", style="white")
        table.add_column("Description", style="dim")
        
        for i, (rapper_id, rapper_info) in enumerate(rappers.items(), 1):
            table.add_row(
                str(i),
                rapper_info['icon'],
                rapper_info['name'],
                rapper_info['description']
            )
        
        return table
    
    @staticmethod
    def create_battle_topic_suggestions_table() -> Table:
        """Create a table showing rap battle topic suggestions"""
        suggestions = get_rap_battle_topic_suggestions()
        
        table = Table(title="Battle Topic Suggestions", box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Topic", style="white")
        
        for i, topic in enumerate(suggestions, 1):
            table.add_row(str(i), topic)
        
        return table
    
    @staticmethod
    def create_setup_confirmation_panel(
        topic: str, 
        left_model: str, 
        right_model: str, 
        max_turns: int, 
        debate_type: str, 
        tools_enabled: bool,
        left_persona: Optional[str] = None,
        right_persona: Optional[str] = None,
        judge_enabled: bool = False,
        judge_model: Optional[str] = None
    ) -> Panel:
        """Create setup confirmation panel"""
        models = get_available_models_list()
        left_display = next((m['display_name'] for m in models if m['name'] == left_model), left_model)
        right_display = next((m['display_name'] for m in models if m['name'] == right_model), right_model)
        
        setup_text = Text()
        setup_text.append("🎯 Topic: ", style="bold")
        setup_text.append(f"{topic}\n", style="white")
        
        setup_text.append("🔴 Left Side: ", style="bold red")
        setup_text.append(f"{left_display}\n", style="white")
        
        setup_text.append("🔵 Right Side: ", style="bold blue")
        setup_text.append(f"{right_display}\n", style="white")
        
        setup_text.append("🔄 Max Turns: ", style="bold")
        setup_text.append(f"{max_turns}\n", style="white")
        
        setup_text.append("📝 Type: ", style="bold")
        setup_text.append(f"{debate_type}\n", style="white")
        
        setup_text.append("🛠️ Tools: ", style="bold")
        setup_text.append(f"{'Enabled' if tools_enabled else 'Disabled'}\n", style="green" if tools_enabled else "red")
        
        setup_text.append("⚖️ Judge: ", style="bold")
        setup_text.append(f"{'Enabled' if judge_enabled else 'Disabled'}", style="green" if judge_enabled else "red")
        if judge_enabled and judge_model:
            judge_display = next((m['display_name'] for m in get_available_models_list() if m['name'] == judge_model), judge_model)
            setup_text.append(f" ({judge_display})", style="dim")
        setup_text.append("\n")
        
        if left_persona and right_persona:
            setup_text.append("🎭 Custom Personas: ", style="bold")
            setup_text.append("Enabled", style="green")
        
        return Panel(
            setup_text,
            title="📋 Debate Setup Confirmation",
            box=box.ROUNDED,
            style="bright_cyan"
        )
    
    @staticmethod
    def create_progress_display(current: int, total: int) -> Text:
        """Create a rich progress display"""
        filled = "█" * current
        empty = "░" * (total - current)
        progress_bar = f"[{filled}{empty}]"
        
        progress_text = Text()
        progress_text.append("📊 Progress: ", style="bold")
        progress_text.append(progress_bar, style="bright_blue")
        progress_text.append(f" {current}/{total}", style="white")
        
        return progress_text
    
    @staticmethod
    def create_speaker_panel(speaker_name: str, icon: str, content: str, is_streaming: bool = False) -> Panel:
        """Create a panel for speaker content"""
        title_text = Text()
        title_text.append(icon, style="bold")
        title_text.append(f" {speaker_name}", style="bold")
        
        if is_streaming:
            title_text.append(" ", style="white")
            title_text.append("●", style="red blink")
        
        # Color coding for different speakers
        if "Progressive" in speaker_name:
            border_style = "red"
        elif "Conservative" in speaker_name:
            border_style = "blue"
        else:
            border_style = "white"
        
        return Panel(
            content,
            title=title_text,
            box=box.ROUNDED,
            style=border_style,
            padding=(0, 1)
        )
    
    @staticmethod
    def create_tool_usage_panel(tool_name: str, query: str, result: str) -> Panel:
        """Create a panel showing tool usage"""
        tool_text = Text()
        tool_text.append("🔍 Tool: ", style="bold cyan")
        tool_text.append(f"{tool_name}\n", style="white")
        tool_text.append("📝 Query: ", style="bold yellow")
        tool_text.append(f"{query}\n", style="white")
        tool_text.append("📊 Result: ", style="bold green")
        tool_text.append(result[:200] + "..." if len(result) > 200 else result, style="dim")
        
        return Panel(
            tool_text,
            title="🛠️ Tool Usage",
            box=box.ROUNDED,
            style="cyan",
            padding=(0, 1)
        )


class DebateUI:
    """Main Rich-enhanced UI class"""
    
    def __init__(self):
        self.console = console
    
    def clear_screen(self):
        """Clear the screen and show header"""
        self.console.clear()
        self.console.print(DebateUIComponents.create_header())
        self.console.print()
    
    def show_api_key_warnings(self):
        """Show API key availability warnings"""
        availability = validate_model_availability()
        available_count = sum(availability.values())
        total_count = len(availability)
        
        if available_count == 0:
            error_panel = Panel(
                "[red]❌ No models available. Please check your API keys.\n\n"
                "[white]Required API keys:\n"
                "• OPENAI_API_KEY for OpenAI models\n"
                "• GOOGLE_API_KEY for Google Gemini models[/white]",
                title="❌ Configuration Error",
                style="red",
                box=box.ROUNDED
            )
            self.console.print(error_panel)
            sys.exit(1)
        elif available_count < total_count:
            warning_panel = Panel(
                f"[yellow]⚠️ {available_count}/{total_count} models available[/yellow]",
                style="yellow",
                box=box.ROUNDED
            )
            self.console.print(warning_panel)
    
    def get_model_choice(self, side: str) -> str:
        """Get model choice with Rich interface"""
        models = get_available_models_list()
        available_models = [m for m in models if m['available']]
        
        if not available_models:
            self.console.print("[red]❌ No models available. Please check your API keys.[/red]")
            sys.exit(1)
        
        while True:
            self.console.print(f"\n[bold]Choose model for {side.upper()} side:[/bold]")
            self.console.print(DebateUIComponents.create_model_selection_table())
            
            try:
                choice = Prompt.ask(f"Enter choice for {side}", choices=[str(i) for i in range(1, len(models) + 1)])
                choice_int = int(choice)
                selected_model = models[choice_int - 1]
                
                if selected_model['available']:
                    return selected_model['name']
                else:
                    self.console.print(f"[red]❌ Model {selected_model['display_name']} is not available. Missing API key.[/red]")
            except (ValueError, IndexError):
                self.console.print("[red]❌ Please enter a valid number.[/red]")
    
    def get_debate_type(self) -> int:
        """Get debate type with Rich interface"""
        self.console.print(DebateUIComponents.create_debate_types_table())
        
        while True:
            try:
                choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])
                return int(choice)
            except ValueError:
                self.console.print("[red]❌ Please enter a valid number.[/red]")
    
    def get_debate_topic(self) -> str:
        """Get debate topic with Rich interface"""
        return Prompt.ask("\n[bold cyan]📝 Enter debate topic[/bold cyan]")
    
    def get_max_turns(self) -> int:
        """Get maximum turns with Rich interface"""
        while True:
            try:
                turns_str = Prompt.ask("\n[bold]🔄 Enter maximum number of turns[/bold]", default="8")
                turns = int(turns_str)
                if turns > 0:
                    return turns
                else:
                    self.console.print("[red]❌ Please enter a positive number.[/red]")
            except ValueError:
                self.console.print("[red]❌ Please enter a valid number.[/red]")
    
    def get_tools_preference(self) -> bool:
        """Get tools preference with Rich interface"""
        tools_panel = Panel(
            "[cyan]🛠️ Enable tools (web search) for agents?\n\n"
            "[white]Tools allow agents to search for current facts and statistics[/white]",
            title="🛠️ Tool Configuration",
            style="cyan",
            box=box.ROUNDED
        )
        self.console.print(tools_panel)
        return Confirm.ask("Enable tools?", default=False)
    
    def get_judge_preference(self) -> bool:
        """Get judge preference with Rich interface"""
        judge_panel = Panel(
            "[yellow]⚖️ Enable AI judge for debate scoring?\n\n"
            "[white]The judge will evaluate each turn on logic, evidence, structure, and communication.\n"
            "Provides detailed scoring and declares a winner at the end.[/white]",
            title="⚖️ Judge Configuration",
            style="yellow",
            box=box.ROUNDED
        )
        self.console.print(judge_panel)
        return Confirm.ask("Enable judge?", default=True)
    
    def get_judge_model_choice(self) -> str:
        """Get model choice for judge with Rich interface"""
        models = get_available_models_list()
        available_models = [m for m in models if m['available']]
        
        if not available_models:
            self.console.print("[red]❌ No models available for judge. Using default.[/red]")
            return "openai-gpt4o-mini"
        
        self.console.print(f"\n[bold yellow]Choose model for JUDGE:[/bold yellow]")
        self.console.print(DebateUIComponents.create_model_selection_table())
        
        while True:
            try:
                choice = Prompt.ask(f"Enter choice for judge", choices=[str(i) for i in range(1, len(models) + 1)], default="1")
                choice_int = int(choice)
                selected_model = models[choice_int - 1]
                
                if selected_model['available']:
                    return selected_model['name']
                else:
                    self.console.print(f"[red]❌ Model {selected_model['display_name']} is not available. Missing API key.[/red]")
            except (ValueError, IndexError):
                self.console.print("[red]❌ Please enter a valid number.[/red]")
    
    def get_custom_personas(self) -> Tuple[Optional[str], Optional[str]]:
        """Get custom personas with Rich interface"""
        personas_panel = Panel(
            "[magenta]🎭 Enter custom personas (leave empty to use defaults)\n\n"
            "[white]This allows you to customize the political perspectives beyond the default progressive/conservative roles[/white]",
            title="🎭 Custom Personas",
            style="magenta",
            box=box.ROUNDED
        )
        self.console.print(personas_panel)
        
        left_persona = Prompt.ask("\n[red]🔴 Left side persona[/red]", default="")
        right_persona = Prompt.ask("[blue]🔵 Right side persona[/blue]", default="")
        
        if left_persona and right_persona:
            return left_persona, right_persona
        else:
            return None, None
    
    def confirm_setup(
        self, 
        topic: str, 
        left_model: str, 
        right_model: str, 
        max_turns: int, 
        debate_type: str, 
        tools_enabled: bool,
        left_persona: Optional[str] = None,
        right_persona: Optional[str] = None,
        judge_enabled: bool = False,
        judge_model: Optional[str] = None
    ) -> bool:
        """Confirm setup with Rich interface"""
        confirmation_panel = DebateUIComponents.create_setup_confirmation_panel(
            topic, left_model, right_model, max_turns, debate_type, 
            tools_enabled, left_persona, right_persona, judge_enabled, judge_model
        )
        self.console.print(confirmation_panel)
        
        return Confirm.ask("\n[bold green]Start debate?[/bold green]", default=True)
    
    def show_debate_header(self, topic: str, left_model: str, right_model: str, tools_enabled: bool, debate_type: str):
        """Show debate header with Rich formatting"""
        models = get_available_models_list()
        left_display = next((m['display_name'] for m in models if m['name'] == left_model), left_model)
        right_display = next((m['display_name'] for m in models if m['name'] == right_model), right_model)
        
        # Create debate type specific headers
        if debate_type == "debate":
            icon = "🗳️"
            title = "Political Debate"
        elif debate_type == "discussion":
            icon = "🏛️"
            title = "Political Discussion"
        else:
            icon = "📋"
            title = "Policy Analysis"
        
        header_text = Text()
        header_text.append(f"{icon} {title}: ", style="bold")
        header_text.append(topic, style="white")
        header_text.append("\n\n")
        header_text.append("🔴 Progressive: ", style="bold red")
        header_text.append(f"{left_display}", style="white")
        header_text.append(" vs ")
        header_text.append("🔵 Conservative: ", style="bold blue")
        header_text.append(f"{right_display}", style="white")
        
        if tools_enabled:
            header_text.append("\n🛠️ Tools: ", style="bold")
            header_text.append("Web search enabled", style="green")
        
        debate_panel = Panel(
            header_text,
            box=box.DOUBLE,
            style="bright_green",
            padding=(1, 2)
        )
        
        self.console.print(debate_panel)
    
    def show_progress(self, current: int, total: int):
        """Show progress with Rich formatting"""
        progress_text = DebateUIComponents.create_progress_display(current, total)
        self.console.print(progress_text)
    
    def show_completion_message(self, debate_type: str):
        """Show completion message with Rich formatting"""
        if debate_type == "debate":
            message = "🏁 Debate completed!"
        elif debate_type == "discussion":
            message = "🏁 Discussion completed!"
        else:
            message = "🏁 Policy analysis completed!"
        
        completion_panel = Panel(
            Text(message, style="bold green", justify="center"),
            box=box.DOUBLE,
            style="bright_green",
            padding=(1, 2)
        )
        
        self.console.print("\n")
        self.console.print(completion_panel)
    
    def ask_continue(self) -> bool:
        """Ask if user wants to continue with Rich interface"""
        return Confirm.ask("\n[bold]Start another debate?[/bold]", default=True)
    
    def display_markdown_view(self, markdown_content: str):
        """Display markdown content using Rich's markdown renderer"""
        self.console.print("\n[bold cyan]📄 Markdown View[/bold cyan]")
        self.console.print("=" * 50, style="cyan")
        
        # Create markdown object
        md = Markdown(markdown_content)
        
        # Display with pager for long content
        if len(markdown_content) > 2000:  # Use pager for long content
            with self.console.pager():
                self.console.print(md)
        else:
            self.console.print(md)
    
    def ask_markdown_export(self) -> bool:
        """Ask if user wants to export debate to markdown"""
        return Confirm.ask("\n[bold cyan]📄 Export debate to markdown file?[/bold cyan]", default=False)
    
    def ask_view_markdown(self) -> bool:
        """Ask if user wants to view markdown in terminal"""
        return Confirm.ask("\n[bold cyan]📄 View debate in markdown format?[/bold cyan]", default=False)
    
    def show_export_success(self, filepath: str):
        """Show successful export message"""
        success_panel = Panel(
            f"[green]✅ Debate exported successfully![/green]\n\n"
            f"[white]File saved to: [bold]{filepath}[/bold][/white]",
            title="📄 Export Complete",
            style="green",
            box=box.ROUNDED
        )
        self.console.print(success_panel)
    
    # Rap Battle specific UI methods
    def get_rapper_choice(self, position: str) -> str:
        """Get rapper choice with Rich interface"""
        rappers = get_available_rappers()
        rapper_list = list(rappers.items())
        
        while True:
            self.console.print(f"\n[bold]Choose rapper for {position.upper()} corner:[/bold]")
            self.console.print(DebateUIComponents.create_rapper_selection_table())
            
            try:
                choice = Prompt.ask(f"Enter choice for {position}", choices=[str(i) for i in range(1, len(rapper_list) + 1)])
                choice_int = int(choice)
                selected_rapper_id = rapper_list[choice_int - 1][0]
                return selected_rapper_id
            except (ValueError, IndexError):
                self.console.print("[red]❌ Please enter a valid number.[/red]")
    
    def get_battle_topic(self) -> str:
        """Get rap battle topic with suggestions"""
        battle_panel = Panel(
            "[yellow]🎤 Choose a battle topic or create your own!\n\n"
            "[white]You can select from suggestions below or enter a custom topic[/white]",
            title="🎤 Battle Topic Selection",
            style="yellow",
            box=box.ROUNDED
        )
        self.console.print(battle_panel)
        
        # Show suggestions
        self.console.print(DebateUIComponents.create_battle_topic_suggestions_table())
        
        choice = Prompt.ask("\n[bold]Enter suggestion number or type custom topic[/bold]")
        
        # Check if it's a number (suggestion choice)
        try:
            suggestion_num = int(choice)
            suggestions = get_rap_battle_topic_suggestions()
            if 1 <= suggestion_num <= len(suggestions):
                return suggestions[suggestion_num - 1]
        except ValueError:
            pass
        
        # If not a valid suggestion number, treat as custom topic
        return choice
    
    def get_battle_rounds(self) -> int:
        """Get number of battle rounds"""
        while True:
            try:
                rounds_str = Prompt.ask("\n[bold]🔄 Enter number of battle rounds[/bold]", default="3")
                rounds = int(rounds_str)
                if 1 <= rounds <= 5:
                    return rounds
                else:
                    self.console.print("[red]❌ Please enter between 1-5 rounds.[/red]")
            except ValueError:
                self.console.print("[red]❌ Please enter a valid number.[/red]")
    
    def confirm_battle_setup(
        self, 
        topic: str, 
        rapper1_id: str, 
        rapper2_id: str, 
        model1: str, 
        model2: str, 
        rounds: int, 
        tools_enabled: bool,
        judge_enabled: bool,
        judge_model: Optional[str] = None
    ) -> bool:
        """Confirm rap battle setup"""
        rappers = get_available_rappers()
        models = get_available_models_list()
        
        rapper1_info = rappers[rapper1_id]
        rapper2_info = rappers[rapper2_id]
        model1_display = next((m['display_name'] for m in models if m['name'] == model1), model1)
        model2_display = next((m['display_name'] for m in models if m['name'] == model2), model2)
        
        setup_text = Text()
        setup_text.append("🎤 Battle Topic: ", style="bold")
        setup_text.append(f"{topic}\n", style="white")
        
        setup_text.append(f"{rapper1_info['icon']} Rapper 1: ", style="bold red")
        setup_text.append(f"{rapper1_info['name']} ({model1_display})\n", style="white")
        
        setup_text.append(f"{rapper2_info['icon']} Rapper 2: ", style="bold blue")
        setup_text.append(f"{rapper2_info['name']} ({model2_display})\n", style="white")
        
        setup_text.append("🔄 Rounds: ", style="bold")
        setup_text.append(f"{rounds}\n", style="white")
        
        setup_text.append("🛠️ Tools: ", style="bold")
        setup_text.append(f"{'Enabled' if tools_enabled else 'Disabled'}\n", style="green" if tools_enabled else "red")
        
        setup_text.append("🏆 Judge: ", style="bold")
        setup_text.append(f"{'Enabled' if judge_enabled else 'Disabled'}", style="green" if judge_enabled else "red")
        if judge_enabled and judge_model:
            judge_display = next((m['display_name'] for m in get_available_models_list() if m['name'] == judge_model), judge_model)
            setup_text.append(f" ({judge_display})", style="dim")
        
        confirmation_panel = Panel(
            setup_text,
            title="🎤 Rap Battle Setup Confirmation",
            box=box.ROUNDED,
            style="bright_magenta"
        )
        self.console.print(confirmation_panel)
        
        return Confirm.ask("\n[bold magenta]🎤 START THE BATTLE?[/bold magenta]", default=True)
    
    def show_battle_header(self, topic: str, rapper1_info: dict, rapper2_info: dict, tools_enabled: bool):
        """Show rap battle header"""
        header_text = Text()
        header_text.append("🎤 RAP BATTLE: ", style="bold")
        header_text.append(topic, style="white")
        header_text.append("\n\n")
        header_text.append(f"{rapper1_info['icon']} {rapper1_info['name']}", style="bold red")
        header_text.append(" VS ", style="bold white")
        header_text.append(f"{rapper2_info['name']} {rapper2_info['icon']}", style="bold blue")
        
        if tools_enabled:
            header_text.append("\n🛠️ Research Tools: ", style="bold")
            header_text.append("Enabled", style="green")
        
        battle_panel = Panel(
            header_text,
            box=box.DOUBLE,
            style="bright_magenta",
            padding=(1, 2)
        )
        
        self.console.print(battle_panel)