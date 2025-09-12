"""
Phoenix tracing configuration for YouTube automation system.

This module provides centralized tracing setup for monitoring LangChain
operations through Phoenix UI at localhost:6006.
"""

import os
from typing import Optional
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor


class PhoenixTracing:
    """Phoenix tracing configuration and management"""
    
    def __init__(self, phoenix_endpoint: str = "http://localhost:6006"):
        self.phoenix_endpoint = phoenix_endpoint
        self.is_initialized = False
        self.tracer_provider = None
    
    def initialize(self) -> bool:
        """
        Initialize Phoenix tracing for LangChain operations.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Set up Phoenix endpoint
            os.environ["PHOENIX_CLIENT_HEADERS"] = "api_key=your-api-key-here"
            os.environ["PHOENIX_PROJECT_NAME"] = "youtube-automation"
            
            # Register Phoenix tracer
            self.tracer_provider = register(
                project_name="youtube-automation",
                endpoint=self.phoenix_endpoint,
            )
            
            # Instrument LangChain
            LangChainInstrumentor().instrument(tracer_provider=self.tracer_provider)
            
            self.is_initialized = True
            print(f"✅ Phoenix tracing initialized at {self.phoenix_endpoint}")
            print("🔍 Traces will appear in Phoenix UI for YouTube automation workflows")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Phoenix tracing: {str(e)}")
            print("📝 YouTube automation will continue without tracing")
            return False
    
    def shutdown(self):
        """Shutdown tracing and cleanup resources"""
        try:
            if self.is_initialized:
                LangChainInstrumentor().uninstrument()
                self.is_initialized = False
                print("🔹 Phoenix tracing shutdown complete")
        except Exception as e:
            print(f"⚠️  Warning during Phoenix tracing shutdown: {str(e)}")


# Global tracing instance
phoenix_tracer: Optional[PhoenixTracing] = None


def setup_phoenix_tracing(phoenix_endpoint: str = "http://localhost:6006") -> bool:
    """
    Setup Phoenix tracing for the YouTube automation system.
    
    Args:
        phoenix_endpoint: Phoenix server endpoint (default: http://localhost:6006)
        
    Returns:
        bool: True if setup successful, False otherwise
    """
    global phoenix_tracer
    
    if phoenix_tracer is not None and phoenix_tracer.is_initialized:
        print("🔄 Phoenix tracing already initialized")
        return True
    
    phoenix_tracer = PhoenixTracing(phoenix_endpoint)
    return phoenix_tracer.initialize()


def shutdown_phoenix_tracing():
    """Shutdown Phoenix tracing"""
    global phoenix_tracer
    
    if phoenix_tracer is not None:
        phoenix_tracer.shutdown()
        phoenix_tracer = None


def is_tracing_enabled() -> bool:
    """Check if Phoenix tracing is currently enabled"""
    return phoenix_tracer is not None and phoenix_tracer.is_initialized


# Auto-initialize tracing if Phoenix endpoint is available
def auto_initialize_tracing():
    """Auto-initialize tracing if Phoenix is detected"""
    import requests
    
    try:
        # Check if Phoenix is running
        response = requests.get("http://localhost:6006/health", timeout=2)
        if response.status_code == 200:
            setup_phoenix_tracing()
        else:
            print("🔹 Phoenix not detected at localhost:6006, skipping tracing")
    except:
        # Phoenix not available, continue without tracing
        print("🔹 Phoenix not available, continuing without tracing")