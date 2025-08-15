"""Rapper agents for rap battles"""

from .eminem import EminemAgent
from .kendrick import KendrickAgent
from .jay_z import JayZAgent
from .nas import NasAgent
from .drake import DrakeAgent
from .tupac import TupacAgent
from .biggie import BiggieAgent
from .base_rapper import BaseRapperAgent

__all__ = [
    'BaseRapperAgent',
    'EminemAgent', 
    'KendrickAgent',
    'JayZAgent',
    'NasAgent',
    'DrakeAgent',
    'TupacAgent',
    'BiggieAgent'
]

# Rapper registry for easy access
AVAILABLE_RAPPERS = {
    'eminem': {
        'name': 'Eminem',
        'class': EminemAgent,
        'icon': '🔥',
        'description': 'The Rap God - Technical mastery and controversial lyrics'
    },
    'kendrick': {
        'name': 'Kendrick Lamar',
        'class': KendrickAgent,
        'icon': '👑',
        'description': 'King Kendrick - Conscious rap and lyrical complexity'
    },
    'jay-z': {
        'name': 'Jay-Z',
        'class': JayZAgent,
        'icon': '💎',
        'description': 'HOV - Business mogul with smooth flow'
    },
    'nas': {
        'name': 'Nas',
        'class': NasAgent,
        'icon': '📜',
        'description': 'Nasty Nas - Storytelling and street poetry'
    },
    'drake': {
        'name': 'Drake',
        'class': DrakeAgent,
        'icon': '🎵',
        'description': 'Champagne Papi - Melodic rap and emotional depth'
    },
    'tupac': {
        'name': '2Pac',
        'class': TupacAgent,
        'icon': '✊',
        'description': 'Legendary revolutionary rapper'
    },
    'biggie': {
        'name': 'The Notorious B.I.G.',
        'class': BiggieAgent,
        'icon': '🏆',
        'description': 'Ready to Die - East Coast legend'
    }
}

def get_rapper_agent(rapper_id: str, model_name: str):
    """Get a rapper agent instance"""
    if rapper_id not in AVAILABLE_RAPPERS:
        raise ValueError(f"Unknown rapper: {rapper_id}")
    
    rapper_class = AVAILABLE_RAPPERS[rapper_id]['class']
    return rapper_class(model_name)

def get_available_rappers():
    """Get list of available rappers"""
    return AVAILABLE_RAPPERS
