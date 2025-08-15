import json
from typing import Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass

from langchain_core.messages import HumanMessage

from agentic.llm import create_model_instance

if TYPE_CHECKING:
    from agentic.tui.rich_ui import DebateUI


@dataclass
class DebateScore:
    """Individual scoring for a debate turn"""
    turn_number: int
    speaker: str  # "progressive" or "conservative"
    
    # Scoring criteria (0-10 scale)
    logic_reasoning: float
    evidence_quality: float
    source_credibility: float
    argument_structure: float
    rebuttal_effectiveness: float
    clarity_communication: float
    
    # Additional factors
    factual_accuracy: float
    originality: float
    
    # Overall turn score (calculated)
    total_score: float
    
    # Detailed feedback
    strengths: List[str]
    weaknesses: List[str]
    specific_feedback: str
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DebateScore':
        """Create DebateScore from dictionary"""
        return cls(**data)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'turn_number': self.turn_number,
            'speaker': self.speaker,
            'logic_reasoning': self.logic_reasoning,
            'evidence_quality': self.evidence_quality,
            'source_credibility': self.source_credibility,
            'argument_structure': self.argument_structure,
            'rebuttal_effectiveness': self.rebuttal_effectiveness,
            'clarity_communication': self.clarity_communication,
            'factual_accuracy': self.factual_accuracy,
            'originality': self.originality,
            'total_score': self.total_score,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'specific_feedback': self.specific_feedback
        }


@dataclass
class FinalJudgment:
    """Final debate judgment and overall winner"""
    progressive_total: float
    conservative_total: float
    winner: str  # "progressive", "conservative", or "tie"
    margin: float
    
    # Category winners
    best_logic: str
    best_evidence: str
    best_communication: str
    best_rebuttals: str
    
    # Overall assessment
    debate_quality: str  # "excellent", "good", "fair", "poor"
    key_insights: List[str]
    judge_summary: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'progressive_total': self.progressive_total,
            'conservative_total': self.conservative_total,
            'winner': self.winner,
            'margin': self.margin,
            'best_logic': self.best_logic,
            'best_evidence': self.best_evidence,
            'best_communication': self.best_communication,
            'best_rebuttals': self.best_rebuttals,
            'debate_quality': self.debate_quality,
            'key_insights': self.key_insights,
            'judge_summary': self.judge_summary
        }


class JudgeAgent:
    """Professional debate judge agent"""
    
    def __init__(self, model_name: str = "openai-gpt4o"):
        self.model_name = model_name
        self.scores: List[DebateScore] = []
        self.final_judgment: Optional[FinalJudgment] = None
        
        self.judge_persona = """You are an expert debate judge with extensive experience in competitive debating, rhetoric, and political analysis. Your role is to fairly and objectively evaluate political debates based on established criteria.

JUDGING EXPERTISE:
- Former competitive debater and debate coach
- PhD in Political Science with expertise in argumentation theory
- 15+ years experience judging academic and professional debates
- Published researcher on debate methodology and evaluation
- Committed to impartial, criteria-based assessment

SCORING CRITERIA (0-10 scale for each):
1. LOGIC & REASONING: Soundness of arguments, logical consistency, absence of fallacies
2. EVIDENCE QUALITY: Relevance, reliability, and strength of supporting evidence
3. SOURCE CREDIBILITY: Quality and trustworthiness of cited sources and data
4. ARGUMENT STRUCTURE: Organization, flow, and coherent presentation
5. REBUTTAL EFFECTIVENESS: Direct engagement with opponent's points, counter-arguments
6. CLARITY & COMMUNICATION: Clear expression, accessibility, persuasive delivery
7. FACTUAL ACCURACY: Correctness of claims and proper interpretation of data
8. ORIGINALITY: Novel insights, creative approaches, fresh perspectives

JUDGING PRINCIPLES:
- Maintain strict neutrality regardless of personal political views
- Focus on argumentation quality, not political agreement
- Provide specific, actionable feedback
- Recognize both strengths and areas for improvement
- Be encouraging while maintaining high standards
- Give detailed explanations for all scoring decisions

You must provide fair, detailed evaluations that help debaters improve while maintaining the highest standards of competitive debate judging."""
    
    def evaluate_turn(
        self, 
        turn_content: str, 
        turn_number: int, 
        speaker: str, 
        conversation_context: List[str],
        tools_used: Optional[List[Dict]] = None,
        ui: Optional['DebateUI'] = None
    ) -> DebateScore:
        """Evaluate a single debate turn"""
        
        try:
            model = create_model_instance(self.model_name, with_tools=False)
        except ValueError as e:
            # Fallback scoring if model fails
            return self._create_fallback_score(turn_number, speaker, turn_content)
        
        # Prepare evaluation prompt
        evaluation_prompt = f"""
DEBATE TURN EVALUATION

Turn Number: {turn_number}
Speaker: {speaker.title()}
Context: This is turn {turn_number} in a political debate.

Previous Context:
{chr(10).join(conversation_context[-3:]) if conversation_context else "This is the opening statement."}

Current Statement to Evaluate:
{turn_content}

Tools/Research Used:
{json.dumps(tools_used, indent=2) if tools_used else "No external research tools were used."}

EVALUATION TASK:
Please evaluate this debate turn using the 8 criteria listed in your persona (0-10 scale each). 

You MUST respond with a valid JSON object containing:
{{
    "logic_reasoning": <score 0-10>,
    "evidence_quality": <score 0-10>,
    "source_credibility": <score 0-10>,
    "argument_structure": <score 0-10>,
    "rebuttal_effectiveness": <score 0-10>,
    "clarity_communication": <score 0-10>,
    "factual_accuracy": <score 0-10>,
    "originality": <score 0-10>,
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "specific_feedback": "Detailed paragraph explaining the scoring and providing constructive feedback"
}}

Focus on objective criteria. Be fair but maintain high standards.
        """
        
        messages = [
            HumanMessage(content=self.judge_persona),
            HumanMessage(content=evaluation_prompt)
        ]
        
        if ui:
            ui.console.print(f"\n⚖️ [bold]Judge evaluating {speaker} turn {turn_number}...[/bold]", style="yellow")
        else:
            print(f"\n⚖️ Judge evaluating {speaker} turn {turn_number}...")
        
        try:
            response = model.invoke(messages)
            if ui:
                ui.console.print(f"[dim]🤖 Judge response length: {len(response.content)} chars[/dim]")
            evaluation_data = self._parse_evaluation_response(response.content)
            
            # Calculate total score
            total_score = (
                evaluation_data["logic_reasoning"] +
                evaluation_data["evidence_quality"] +
                evaluation_data["source_credibility"] +
                evaluation_data["argument_structure"] +
                evaluation_data["rebuttal_effectiveness"] +
                evaluation_data["clarity_communication"] +
                evaluation_data["factual_accuracy"] +
                evaluation_data["originality"]
            )
            
            score = DebateScore(
                turn_number=turn_number,
                speaker=speaker,
                logic_reasoning=evaluation_data["logic_reasoning"],
                evidence_quality=evaluation_data["evidence_quality"],
                source_credibility=evaluation_data["source_credibility"],
                argument_structure=evaluation_data["argument_structure"],
                rebuttal_effectiveness=evaluation_data["rebuttal_effectiveness"],
                clarity_communication=evaluation_data["clarity_communication"],
                factual_accuracy=evaluation_data["factual_accuracy"],
                originality=evaluation_data["originality"],
                total_score=total_score,
                strengths=evaluation_data["strengths"],
                weaknesses=evaluation_data["weaknesses"],
                specific_feedback=evaluation_data["specific_feedback"]
            )
            
            self.scores.append(score)
            
            if ui:
                self._display_turn_score(score, ui)
            
            return score
            
        except Exception as e:
            if ui:
                ui.console.print(f"[red]⚠️ Judge evaluation error: {str(e)}[/red]")
            return self._create_fallback_score(turn_number, speaker, turn_content)
    
    def _parse_evaluation_response(self, response_content: str) -> Dict:
        """Parse the judge's JSON response"""
        try:
            # Try to extract JSON from the response
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_content[start_idx:end_idx]
                parsed_data = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['logic_reasoning', 'evidence_quality', 'source_credibility', 
                                 'argument_structure', 'rebuttal_effectiveness', 'clarity_communication',
                                 'factual_accuracy', 'originality', 'strengths', 'weaknesses', 'specific_feedback']
                
                for field in required_fields:
                    if field not in parsed_data:
                        print(f"⚠️ Missing field in judge response: {field}")
                        return self._create_fallback_evaluation()
                
                return parsed_data
            else:
                print(f"⚠️ No JSON found in judge response (length: {len(response_content)})")
                print(f"Response preview: {response_content[:200]}...")
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ Judge JSON parsing error: {str(e)}")
            print(f"Response content: {response_content[:500]}...")
            # Fallback parsing if JSON is malformed
            return self._create_fallback_evaluation()
    
    def _create_fallback_evaluation(self) -> Dict:
        """Create fallback evaluation if parsing fails"""
        return {
            "logic_reasoning": 6.0,
            "evidence_quality": 6.0,
            "source_credibility": 6.0,
            "argument_structure": 6.0,
            "rebuttal_effectiveness": 6.0,
            "clarity_communication": 6.0,
            "factual_accuracy": 6.0,
            "originality": 6.0,
            "strengths": ["Argument presented", "Position articulated"],
            "weaknesses": ["Could be more detailed", "Needs stronger evidence"],
            "specific_feedback": "Evaluation system encountered an error. Default scoring applied."
        }
    
    def _create_fallback_score(self, turn_number: int, speaker: str, content: str) -> DebateScore:
        """Create fallback score if evaluation fails"""
        return DebateScore(
            turn_number=turn_number,
            speaker=speaker,
            logic_reasoning=6.0,
            evidence_quality=6.0,
            source_credibility=6.0,
            argument_structure=6.0,
            rebuttal_effectiveness=6.0,
            clarity_communication=6.0,
            factual_accuracy=6.0,
            originality=6.0,
            total_score=48.0,
            strengths=["Participated in debate", "Presented viewpoint"],
            weaknesses=["Evaluation system error"],
            specific_feedback="Judge evaluation system encountered an error. Default scoring applied."
        )
    
    def finalize_judgment(self, ui: Optional['DebateUI'] = None) -> FinalJudgment:
        """Create final judgment after all turns"""
        if not self.scores:
            if ui:
                ui.console.print("[yellow]⚠️ No scores available for final judgment[/yellow]")
            else:
                print("⚠️ No scores available for final judgment")
            return self._create_default_judgment()
        
        if ui:
            ui.console.print(f"\n⚖️ [bold]Judge creating final decision from {len(self.scores)} turn evaluations...[/bold]", style="yellow")
        else:
            print(f"\n⚖️ Judge creating final decision from {len(self.scores)} turn evaluations...")
        
        # Calculate totals
        progressive_scores = [s for s in self.scores if s.speaker == "progressive"]
        conservative_scores = [s for s in self.scores if s.speaker == "conservative"]
        
        progressive_total = sum(s.total_score for s in progressive_scores)
        conservative_total = sum(s.total_score for s in conservative_scores)
        
        # Determine winner
        if abs(progressive_total - conservative_total) < 5.0:
            winner = "tie"
            margin = abs(progressive_total - conservative_total)
        elif progressive_total > conservative_total:
            winner = "progressive"
            margin = progressive_total - conservative_total
        else:
            winner = "conservative"
            margin = conservative_total - progressive_total
        
        # Category analysis
        best_logic = self._find_category_winner("logic_reasoning")
        best_evidence = self._find_category_winner("evidence_quality")
        best_communication = self._find_category_winner("clarity_communication")
        best_rebuttals = self._find_category_winner("rebuttal_effectiveness")
        
        # Debate quality assessment
        avg_total = (progressive_total + conservative_total) / len(self.scores) if self.scores else 0
        if avg_total >= 65:
            quality = "excellent"
        elif avg_total >= 55:
            quality = "good"
        elif avg_total >= 45:
            quality = "fair"
        else:
            quality = "poor"
        
        # Generate key insights
        insights = self._generate_key_insights()
        
        # Create judge summary
        judge_summary = self._generate_judge_summary(winner, margin, quality)
        
        self.final_judgment = FinalJudgment(
            progressive_total=progressive_total,
            conservative_total=conservative_total,
            winner=winner,
            margin=margin,
            best_logic=best_logic,
            best_evidence=best_evidence,
            best_communication=best_communication,
            best_rebuttals=best_rebuttals,
            debate_quality=quality,
            key_insights=insights,
            judge_summary=judge_summary
        )
        
        if ui:
            self._display_final_judgment(ui)
        
        return self.final_judgment
    
    def _find_category_winner(self, category: str) -> str:
        """Find which side performed better in a specific category"""
        progressive_avg = sum(getattr(s, category) for s in self.scores if s.speaker == "progressive")
        conservative_avg = sum(getattr(s, category) for s in self.scores if s.speaker == "conservative")
        
        prog_count = len([s for s in self.scores if s.speaker == "progressive"])
        cons_count = len([s for s in self.scores if s.speaker == "conservative"])
        
        if prog_count > 0:
            progressive_avg /= prog_count
        if cons_count > 0:
            conservative_avg /= cons_count
        
        if abs(progressive_avg - conservative_avg) < 0.5:
            return "tie"
        return "progressive" if progressive_avg > conservative_avg else "conservative"
    
    def _generate_key_insights(self) -> List[str]:
        """Generate key insights about the debate"""
        insights = []
        
        if self.scores:
            # Find strongest areas
            avg_scores = {}
            categories = ["logic_reasoning", "evidence_quality", "source_credibility", 
                         "argument_structure", "rebuttal_effectiveness", "clarity_communication",
                         "factual_accuracy", "originality"]
            
            for category in categories:
                avg_scores[category] = sum(getattr(s, category) for s in self.scores) / len(self.scores)
            
            # Best performing category
            best_category = max(avg_scores.keys(), key=lambda k: avg_scores[k])
            insights.append(f"Strongest debate aspect: {best_category.replace('_', ' ').title()}")
            
            # Improvement area
            worst_category = min(avg_scores.keys(), key=lambda k: avg_scores[k])
            insights.append(f"Area for improvement: {worst_category.replace('_', ' ').title()}")
            
            # Quality assessment
            overall_avg = sum(avg_scores.values()) / len(avg_scores)
            if overall_avg >= 7.5:
                insights.append("High-quality debate with strong arguments from both sides")
            elif overall_avg >= 6.0:
                insights.append("Solid debate performance with room for enhancement")
            else:
                insights.append("Debate would benefit from stronger evidence and clearer reasoning")
        
        return insights
    
    def _generate_judge_summary(self, winner: str, margin: float, quality: str) -> str:
        """Generate comprehensive judge summary"""
        if winner == "tie":
            result_text = f"This debate ended in a tie, with both sides performing comparably (margin: {margin:.1f} points)."
        else:
            result_text = f"The {winner} side won this debate by {margin:.1f} points."
        
        quality_text = f"Overall debate quality was {quality}."
        
        return f"{result_text} {quality_text} Both participants demonstrated engagement with the topic and made efforts to support their positions."
    
    def _create_default_judgment(self) -> FinalJudgment:
        """Create default judgment if no scores available"""
        return FinalJudgment(
            progressive_total=0.0,
            conservative_total=0.0,
            winner="tie",
            margin=0.0,
            best_logic="tie",
            best_evidence="tie", 
            best_communication="tie",
            best_rebuttals="tie",
            debate_quality="fair",
            key_insights=["Debate evaluation incomplete"],
            judge_summary="Unable to complete full evaluation due to technical issues."
        )
    
    def _display_turn_score(self, score: DebateScore, ui: 'DebateUI'):
        """Display turn score using Rich UI"""
        from ..tui.rich_ui import DebateUIComponents
        
        # Create score panel
        score_text = f"""
**{score.speaker.title()} - Turn {score.turn_number} Score: {score.total_score:.1f}/80**

**Category Scores:**
• Logic & Reasoning: {score.logic_reasoning:.1f}/10
• Evidence Quality: {score.evidence_quality:.1f}/10  
• Source Credibility: {score.source_credibility:.1f}/10
• Argument Structure: {score.argument_structure:.1f}/10
• Rebuttal Effectiveness: {score.rebuttal_effectiveness:.1f}/10
• Clarity & Communication: {score.clarity_communication:.1f}/10
• Factual Accuracy: {score.factual_accuracy:.1f}/10
• Originality: {score.originality:.1f}/10

**Strengths:** {', '.join(score.strengths)}
**Areas for Improvement:** {', '.join(score.weaknesses)}

**Judge Feedback:** {score.specific_feedback}
        """
        
        score_panel = DebateUIComponents.create_speaker_panel(
            "Judge Evaluation", "⚖️", score_text.strip()
        )
        ui.console.print(score_panel)
    
    def _display_final_judgment(self, ui: 'DebateUI'):
        """Display final judgment using Rich UI"""
        from ..tui.rich_ui import DebateUIComponents
        
        judgment = self.final_judgment
        
        winner_text = "🏆 DEBATE WINNER 🏆"
        if judgment.winner == "tie":
            result = f"**TIE DEBATE** (Margin: {judgment.margin:.1f} points)"
        else:
            result = f"**{judgment.winner.upper()} WINS** by {judgment.margin:.1f} points"
        
        final_text = f"""
{result}

**Final Scores:**
🔴 Progressive Total: {judgment.progressive_total:.1f}
🔵 Conservative Total: {judgment.conservative_total:.1f}

**Category Winners:**
• Best Logic: {judgment.best_logic.title()}
• Best Evidence: {judgment.best_evidence.title()}
• Best Communication: {judgment.best_communication.title()}
• Best Rebuttals: {judgment.best_rebuttals.title()}

**Debate Quality:** {judgment.debate_quality.title()}

**Key Insights:**
{chr(10).join(f"• {insight}" for insight in judgment.key_insights)}

**Judge's Summary:**
{judgment.judge_summary}
        """
        
        judgment_panel = DebateUIComponents.create_speaker_panel(
            winner_text, "⚖️", final_text.strip()
        )
        ui.console.print(judgment_panel)
    
    def get_scoreboard(self) -> Dict:
        """Get complete scoreboard data"""
        return {
            "individual_scores": [score.to_dict() for score in self.scores],
            "final_judgment": self.final_judgment.to_dict() if self.final_judgment else None
        }


def create_judge_agent(model_name: str = "openai-gpt4o") -> JudgeAgent:
    """Factory function to create judge agent"""
    return JudgeAgent(model_name)