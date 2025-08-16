# Agentic AI

A powerful Python-based agentic AI system that creates real-time interactive conversations between AI agents with different personas and perspectives. Features both political debates and epic rap battles with streaming responses and comprehensive model support.

## Features

### Multiple AI Agents
- **Political Debates**: Progressive vs Conservative perspectives
- **Rap Battles**: Legendary rappers (Tupac, Biggie, Eminem, Jay-Z, Nas, Drake, Kendrick)
- **Real-time Streaming**: Live responses with beautiful terminal UI
- **Judge System**: AI judges evaluate performances with detailed scoring

### Debate Types
1. **Political Debate** - Structured arguments with opposing viewpoints
2. **Political Discussion** - General exchange of ideas  
3. **Policy Analysis** - Deep analysis of policy implications
4. **Rap Battle** - Epic battles between legendary artists

### Comprehensive Model Support
- **OpenAI**: GPT-5, GPT-4o, GPT-4.5, o3, GPT-4o-Mini
- **Anthropic**: Claude Sonnet 4, Claude Opus 4.1, Claude Haiku 3.5
- **Google**: Gemini 2.5 Flash, Gemini 2.5 Pro
- **DeepSeek**: DeepSeek R1, DeepSeek V3
- **Meta**: Llama 4 Scout, Llama 4 Maverick
- **Groq**: High-speed inference
- **Ollama**: Local models (Qwen 3, Gemma 3, Mistral Small)
- **OpenRouter**: GLM-4.5, Qwen 3 Thinking
- **GigaChat**: Russian language models

### Advanced Features
- **Web Search Tools**: DuckDuckGo integration for factual information
- **Rich Terminal UI**: Beautiful panels, tables, progress bars
- **Markdown Export**: Professional documentation with judge scores
- **Session Tracking**: Multiple debates with summary export
- **Custom Personas**: User-defined perspectives and viewpoints
- **Real-time Scoring**: 8-criteria judge evaluation system

## Quick Start

### Prerequisites
- Python 3.13+
- UV package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/amjadjibon/agentic.git
   cd agentic
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up API keys** (add to `.env` file)
   ```bash
   export OPENAI_API_KEY=your_openai_key
   export GOOGLE_API_KEY=your_google_key
   export export ANTHROPIC_API_KEY=your_anthropic_key
   export DEEPSEEK_API_KEY=your_deepseek_key
   export GROQ_API_KEY=your_groq_key
   export OPENROUTER_API_KEY=your_openrouter_key
   ```

4. **Run the application**
   ```bash
   uv run python src/main.py
   ```

## Usage

### Political Debate Example
```bash
# Start the interactive terminal
uv run python src/main.py

# Select debate type (1-4)
# Choose models for each side
# Enter your debate topic
# Watch the real-time streaming debate!
```

### Rap Battle Example  
```bash
# Select "Rap Battle" option
# Choose legendary rappers (Tupac vs Biggie)
# Pick models and battle rounds
# Enjoy the epic lyrical showdown!
```

## Development

### Commands
```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check

# Format code  
uv run ruff format
```

### Adding New Models
1. Add model configuration to `src/agentic/llm/models.py`
2. Implement provider support in `get_model()` function
3. Update model availability checking

### Creating Custom Agents
1. Inherit from `BaseStreamingAgent` or `BaseRapperAgent`
2. Implement required methods (`stream_response`, etc.)
3. Add to agent registry

## Judge Evaluation System

The AI judge evaluates performances using 8 criteria (0-10 scale):

1. **Logic & Reasoning** - Argument coherence and logical flow
2. **Evidence & Sources** - Use of facts, statistics, examples
3. **Source Quality** - Credibility and relevance of sources
4. **Argument Structure** - Organization and presentation
5. **Rebuttals** - Addressing opponent's points effectively
6. **Clarity & Communication** - Clear, engaging delivery
7. **Accuracy** - Factual correctness
8. **Originality** - Creative and novel perspectives


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **LangChain** for the excellent LLM framework
- **LangGraph** for ai agents orchestrations
- **Rich** for the beautiful terminal UI
- **UV** for fast Python package management
- All the amazing AI model providers
