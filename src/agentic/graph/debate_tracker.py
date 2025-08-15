from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

from agentic.state import ChatState


@dataclass
class DebateSession:
    """Tracks a single debate session"""
    topic: str
    left_model: str
    right_model: str
    debate_type: str
    tools_enabled: bool
    max_turns: int
    left_persona: Optional[str] = None
    right_persona: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    final_state: Optional[ChatState] = None
    markdown_file: Optional[str] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Get debate duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def is_completed(self) -> bool:
        """Check if debate reached max turns"""
        if self.final_state:
            return self.final_state["conversation_count"] >= self.final_state["max_turns"]
        return False
    
    @property
    def turn_count(self) -> int:
        """Get number of completed turns"""
        if self.final_state:
            return self.final_state["conversation_count"]
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "topic": self.topic,
            "left_model": self.left_model,
            "right_model": self.right_model,
            "debate_type": self.debate_type,
            "tools_enabled": self.tools_enabled,
            "max_turns": self.max_turns,
            "left_persona": self.left_persona,
            "right_persona": self.right_persona,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "is_completed": self.is_completed,
            "turn_count": self.turn_count,
            "markdown_file": self.markdown_file
        }


class DebateTracker:
    """Manages multiple debate sessions"""
    
    def __init__(self):
        self.sessions: List[DebateSession] = []
        self.current_session: Optional[DebateSession] = None
    
    def start_debate(
        self,
        topic: str,
        left_model: str,
        right_model: str,
        debate_type: str,
        tools_enabled: bool,
        max_turns: int,
        left_persona: Optional[str] = None,
        right_persona: Optional[str] = None
    ) -> DebateSession:
        """Start tracking a new debate"""
        session = DebateSession(
            topic=topic,
            left_model=left_model,
            right_model=right_model,
            debate_type=debate_type,
            tools_enabled=tools_enabled,
            max_turns=max_turns,
            left_persona=left_persona,
            right_persona=right_persona
        )
        
        self.current_session = session
        self.sessions.append(session)
        return session
    
    def end_debate(self, final_state: ChatState, markdown_file: Optional[str] = None):
        """Mark current debate as ended"""
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.final_state = final_state
            self.current_session.markdown_file = markdown_file
            self.current_session = None
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of all sessions"""
        total_sessions = len(self.sessions)
        completed_sessions = sum(1 for s in self.sessions if s.is_completed)
        total_turns = sum(s.turn_count for s in self.sessions)
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0,
            "total_turns": total_turns,
            "average_turns": total_turns / total_sessions if total_sessions > 0 else 0,
            "sessions": [s.to_dict() for s in self.sessions]
        }
    
    def export_session_summary(self, output_file: str = "debate_session_summary.md") -> str:
        """Export session summary as markdown"""
        from ..tui.markdown import create_debate_summary_markdown
        
        debates_data = []
        for session in self.sessions:
            debates_data.append({
                "topic": session.topic,
                "type": session.debate_type,
                "left_model": session.left_model,
                "right_model": session.right_model,
                "tools_enabled": session.tools_enabled,
                "turns_completed": session.turn_count,
                "max_turns": session.max_turns,
                "completed": session.is_completed,
                "file_path": session.markdown_file
            })
        
        return create_debate_summary_markdown(debates_data, output_file)


# Global tracker instance
debate_tracker = DebateTracker()