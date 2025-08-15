# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based political debate AI system that uses streaming agents to create real-time debates between AI with different political personas. The system supports multiple LLM providers with a configurable model selection system and includes optional web search tools. All interactions are streaming-only for better user experience.

## Key Commands

### Development Commands
- `uv run python src/main.py` - Run the Rich-enhanced debate AI terminal interface
- `uv run pytest` - Run all tests
- `uv run pytest tests/` - Run tests in the tests directory
- `uv run pytest -m unit` - Run only unit tests
- `uv run pytest -m integration` - Run only integration tests
- `uv run pytest -m "not slow"` - Skip slow tests
- `uv run ruff check` - Run linting
- `uv run ruff format` - Format code

### Environment Setup
Set these environment variables for full functionality:
- `OPENAI_API_KEY` - Required for OpenAI GPT-4o model
- `GOOGLE_API_KEY` - Required for Google Gemini model

## Architecture Overview

### Core Components

**Model Configuration (`src/debateai/config.py`)**
- `ModelConfig`: Centralized model configuration with provider info, API keys, and capabilities
- `AVAILABLE_MODELS`: Dictionary of all supported models (OpenAI GPT-4o, GPT-4o Mini, Gemini Pro, Gemini Flash)
- Model availability validation and UI formatting functions

**State Management (`src/debateai/state.py`)**
- `ChatState`: TypedDict defining the conversation state with messages, current speaker, turn count, and max turns

**Streaming Orchestration (`src/debateai/graph.py`)**
- `run_streaming_debate()`: Main streaming debate function supporting all debate types
- `run_custom_streaming_debate()`: Custom persona debates with user-defined perspectives
- Real-time streaming with progress tracking and error handling

**Agent System (`src/debateai/agents/`)**
- `base_agent.py`: `BaseStreamingAgent` abstract class with common streaming functionality
- `left_agent.py`: `LeftAgent` and `CustomLeftAgent` for progressive perspectives
- `right_agent.py`: `RightAgent` and `CustomRightAgent` for conservative perspectives
- All agents inherit streaming capabilities with tool integration support

**LLM Integration (`src/debateai/models.py`)**
- `create_model_instance()`: Factory function to create models from configuration
- Supports OpenAI and Gemini providers with automatic API key validation
- `initialize_models()`: Legacy compatibility function

**Tools Integration (`src/debateai/tools/`)**
- `search.py`: DuckDuckGo web search tool for factual information
- `tools_registry.py`: Manages available tools for agents
- Tools can be enabled/disabled per debate session
- Robust tool call handling with argument filtering for model compatibility

**Rich-Enhanced User Interface**
- `rich_ui.py`: Rich-based UI components with panels, tables, and progress displays
- `ui.py`: Main terminal interface using Rich for beautiful, interactive experience
- Features: Dynamic model selection tables, styled panels, progress tracking, colored output
- Real-time model availability checking with visual status indicators

### Data Flow

1. User configures debate through terminal UI (topic, models, tools, max turns, optional custom personas)
2. Model availability is validated based on API keys
3. Appropriate streaming agents are created with selected models
4. Initial state is set with debate-type-specific prompts
5. Agents alternate streaming responses with real-time output
6. Each agent response updates the state and switches to the next speaker
7. Progress tracking and tool usage is displayed during streaming
8. Debate continues until max turns reached or manually stopped

### Testing Structure

Tests are organized in `tests/debateai/` matching the source structure:
- Unit tests for individual components
- Integration tests for end-to-end workflows
- Tool-specific tests in `tests/debateai/tools/`
- Uses pytest with custom markers for test categorization

## Development Notes

- Uses UV for dependency management instead of pip
- Python 3.13+ required
- **Rich library integration** for beautiful terminal UI with colors, panels, tables, and progress bars
- All agents use streaming-only architecture for real-time experience
- Configurable model system allows easy addition of new LLM providers
- Object-oriented agent design with inheritance and factory patterns
- Comprehensive error handling with API key validation and graceful degradation
- Modular design supports custom personas and debate types
- Rich UI components provide professional-looking terminal interface