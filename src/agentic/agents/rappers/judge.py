"""Rap battle judge agent for evaluating rap battles"""

import json
from typing import Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass

from langchain_core.messages import HumanMessage

from agentic.llm import create_model_instance

if TYPE_CHECKING:
    from agentic.tui.rich_ui import DebateUI


@dataclass
class RapBattleScore:
    """Individual scoring for a rap battle round"""
    round_number: int
    rapper: str
    
    # Rap battle specific criteria (0-10 scale)
    flow_delivery: float
    lyrical_complexity: float
    wordplay_creativity: float
    punchlines_impact: float
    crowd_appeal: float
    battle_tactics: float
    
    # Technical aspects
    rhyme_scheme: float
    originality: float
    
    # Overall round score (calculated)
    total_score: float
    
    # Detailed feedback
    best_bars: List[str]
    weaknesses: List[str]
    judge_comments: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'round_number': self.round_number,
            'rapper': self.rapper,
            'flow_delivery': self.flow_delivery,
            'lyrical_complexity': self.lyrical_complexity,
            'wordplay_creativity': self.wordplay_creativity,
            'punchlines_impact': self.punchlines_impact,
            'crowd_appeal': self.crowd_appeal,
            'battle_tactics': self.battle_tactics,
            'rhyme_scheme': self.rhyme_scheme,
            'originality': self.originality,
            'total_score': self.total_score,
            'best_bars': self.best_bars,
            'weaknesses': self.weaknesses,
            'judge_comments': self.judge_comments
        }


@dataclass
class RapBattleJudgment:
    """Final rap battle judgment and winner"""
    rapper1_total: float
    rapper2_total: float
    winner: str
    margin: float
    
    # Category winners
    best_flow: str
    best_wordplay: str
    best_punchlines: str
    best_crowd_appeal: str
    
    # Overall assessment
    battle_quality: str  # "legendary", "fire", "solid", "weak"
    key_moments: List[str]
    judge_summary: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'rapper1_total': self.rapper1_total,
            'rapper2_total': self.rapper2_total,
            'winner': self.winner,
            'margin': self.margin,
            'best_flow': self.best_flow,
            'best_wordplay': self.best_wordplay,
            'best_punchlines': self.best_punchlines,
            'best_crowd_appeal': self.best_crowd_appeal,
            'battle_quality': self.battle_quality,
            'key_moments': self.key_moments,
            'judge_summary': self.judge_summary
        }


class RapBattleJudge:
    """Professional rap battle judge agent"""
    
    def __init__(self, model_name: str = "openai-gpt4o"):
        self.model_name = model_name
        self.scores: List[RapBattleScore] = []
        self.final_judgment: Optional[RapBattleJudgment] = None
        
        self.judge_persona = """You are a legendary rap battle judge with decades of experience in underground battle scenes, professional rap competitions, and hip-hop culture. Your expertise includes judging battles at venues like URL (Ultimate Rap League), King of the Dot, and classic NYC cipher battles.

JUDGING EXPERTISE:
- 20+ years in hip-hop culture and battle rap scene
- Former battle rapper turned respected judge
- Expert in rap history, flows, and lyrical techniques
- Judge for major battle leagues and competitions
- Deep understanding of crowd psychology and battle dynamics
- Respected for fair, knowledgeable, and entertaining judgments

RAP BATTLE SCORING CRITERIA (0-10 scale for each):
1. FLOW & DELIVERY: Rhythm, cadence, breath control, voice modulation, timing
2. LYRICAL COMPLEXITY: Vocabulary, sentence structure, internal rhymes, complexity
3. WORDPLAY & CREATIVITY: Puns, double entendres, metaphors, creative language use
4. PUNCHLINES & IMPACT: Hard-hitting bars, memorable moments, crowd reaction worthy lines
5. CROWD APPEAL: Entertainment value, charisma, stage presence, audience connection
6. BATTLE TACTICS: Rebuttals, personals, how well they address opponent, battle IQ
7. RHYME SCHEME: Rhyme patterns, multi-syllabic rhymes, internal rhyme structure
8. ORIGINALITY: Fresh angles, unique style, avoiding cliché bars and common setups

JUDGING PRINCIPLES:
- Respect all styles (lyrical, punch-heavy, flow-focused, etc.)
- Consider crowd reaction and battle atmosphere
- Look for quotable moments and replay value
- Judge what's said, not reputation or previous battles
- Appreciate technical skill while valuing entertainment
- Give detailed feedback that helps battlers improve
- Maintain the energy and culture of battle rap

BATTLE CULTURE KNOWLEDGE:
- Understand battle rap slang, references, and culture
- Recognize different regional styles and preferences
- Appreciate both old school and new school approaches
- Value authenticity and realness in content
- Respect the competitive nature while maintaining fairness

You must provide exciting, detailed evaluations that capture the energy of battle rap while maintaining professional standards."""

    def evaluate_round(
        self, 
        verse_content: str, 
        round_number: int, 
        rapper_name: str, 
        battle_context: List[str],
        ui: Optional['DebateUI'] = None
    ) -> RapBattleScore:
        """Evaluate a single rap battle round"""
        
        try:
            model = create_model_instance(self.model_name, with_tools=False)
        except ValueError as e:
            # Fallback scoring if model fails
            return self._create_fallback_score(round_number, rapper_name, verse_content)
        
        # Prepare evaluation prompt
        evaluation_prompt = f"""
RAP BATTLE ROUND EVALUATION

Round Number: {round_number}
Rapper: {rapper_name}
Context: This is round {round_number} in an intense rap battle.

Previous Battle Context:
{chr(10).join(battle_context[-2:]) if battle_context else "This is the opening round."}

Verse to Evaluate:
{verse_content}

EVALUATION TASK:
Judge this rap battle round using the 8 criteria listed in your persona (0-10 scale each).

You MUST respond with a valid JSON object containing:
{{
    "flow_delivery": <score 0-10>,
    "lyrical_complexity": <score 0-10>,
    "wordplay_creativity": <score 0-10>,
    "punchlines_impact": <score 0-10>,
    "crowd_appeal": <score 0-10>,
    "battle_tactics": <score 0-10>,
    "rhyme_scheme": <score 0-10>,
    "originality": <score 0-10>,
    "best_bars": ["best bar 1", "best bar 2", "best bar 3"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "judge_comments": "Detailed paragraph explaining the performance with battle rap energy and terminology"
}}

Judge with the energy and knowledge of a seasoned battle rap veteran. Keep it real!
        """
        
        messages = [
            HumanMessage(content=self.judge_persona),
            HumanMessage(content=evaluation_prompt)
        ]
        
        if ui:
            ui.console.print(f"\n🎤 [bold]Judge scoring {rapper_name}'s round {round_number}...[/bold]", style="yellow")
        else:
            print(f"\n🎤 Judge scoring {rapper_name}'s round {round_number}...")
        
        try:
            response = model.invoke(messages)
            if ui:
                ui.console.print(f"[dim]🔥 Judge response length: {len(response.content)} chars[/dim]")
            evaluation_data = self._parse_evaluation_response(response.content)
            
            # Calculate total score
            total_score = (
                evaluation_data["flow_delivery"] +
                evaluation_data["lyrical_complexity"] +
                evaluation_data["wordplay_creativity"] +
                evaluation_data["punchlines_impact"] +
                evaluation_data["crowd_appeal"] +
                evaluation_data["battle_tactics"] +
                evaluation_data["rhyme_scheme"] +
                evaluation_data["originality"]
            )
            
            score = RapBattleScore(
                round_number=round_number,
                rapper=rapper_name,
                flow_delivery=evaluation_data["flow_delivery"],
                lyrical_complexity=evaluation_data["lyrical_complexity"],
                wordplay_creativity=evaluation_data["wordplay_creativity"],
                punchlines_impact=evaluation_data["punchlines_impact"],
                crowd_appeal=evaluation_data["crowd_appeal"],
                battle_tactics=evaluation_data["battle_tactics"],
                rhyme_scheme=evaluation_data["rhyme_scheme"],
                originality=evaluation_data["originality"],
                total_score=total_score,
                best_bars=evaluation_data["best_bars"],
                weaknesses=evaluation_data["weaknesses"],
                judge_comments=evaluation_data["judge_comments"]
            )
            
            self.scores.append(score)
            
            if ui:
                self._display_round_score(score, ui)
            
            return score
            
        except Exception as e:
            if ui:
                ui.console.print(f"[red]⚠️ Judge evaluation error: {str(e)}[/red]")
            else:
                print(f"⚠️ Judge evaluation error: {str(e)}")
            return self._create_fallback_score(round_number, rapper_name, verse_content)
    
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
                required_fields = ['flow_delivery', 'lyrical_complexity', 'wordplay_creativity', 
                                 'punchlines_impact', 'crowd_appeal', 'battle_tactics',
                                 'rhyme_scheme', 'originality', 'best_bars', 'weaknesses', 'judge_comments']
                
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
            "flow_delivery": 6.0,
            "lyrical_complexity": 6.0,
            "wordplay_creativity": 6.0,
            "punchlines_impact": 6.0,
            "crowd_appeal": 6.0,
            "battle_tactics": 6.0,
            "rhyme_scheme": 6.0,
            "originality": 6.0,
            "best_bars": ["Verse delivered", "Showed up to battle"],
            "weaknesses": ["Judge system error", "Could not evaluate properly"],
            "judge_comments": "Judge evaluation system encountered an error. Default scoring applied."
        }
    
    def _create_fallback_score(self, round_number: int, rapper: str, content: str) -> RapBattleScore:
        """Create fallback score if evaluation fails"""
        return RapBattleScore(
            round_number=round_number,
            rapper=rapper,
            flow_delivery=6.0,
            lyrical_complexity=6.0,
            wordplay_creativity=6.0,
            punchlines_impact=6.0,
            crowd_appeal=6.0,
            battle_tactics=6.0,
            rhyme_scheme=6.0,
            originality=6.0,
            total_score=48.0,
            best_bars=["Participated in battle", "Delivered verse"],
            weaknesses=["Judge system error"],
            judge_comments="Judge evaluation system encountered an error. Default scoring applied."
        )
    
    def finalize_judgment(self, rapper1_name: str, rapper2_name: str, ui: Optional['DebateUI'] = None) -> RapBattleJudgment:
        """Create final judgment after all rounds"""
        if not self.scores:
            if ui:
                ui.console.print("[yellow]⚠️ No scores available for final judgment[/yellow]")
            else:
                print("⚠️ No scores available for final judgment")
            return self._create_default_judgment(rapper1_name, rapper2_name)
        
        if ui:
            ui.console.print(f"\n🏆 [bold]Judge declaring the winner from {len(self.scores)} rounds...[/bold]", style="yellow")
        else:
            print(f"\n🏆 Judge declaring the winner from {len(self.scores)} rounds...")
        
        # Calculate totals
        rapper1_scores = [s for s in self.scores if s.rapper == rapper1_name]
        rapper2_scores = [s for s in self.scores if s.rapper == rapper2_name]
        
        rapper1_total = sum(s.total_score for s in rapper1_scores)
        rapper2_total = sum(s.total_score for s in rapper2_scores)
        
        # Determine winner
        if abs(rapper1_total - rapper2_total) < 3.0:
            winner = "tie"
            margin = abs(rapper1_total - rapper2_total)
        elif rapper1_total > rapper2_total:
            winner = rapper1_name
            margin = rapper1_total - rapper2_total
        else:
            winner = rapper2_name
            margin = rapper2_total - rapper1_total
        
        # Category analysis
        best_flow = self._find_category_winner("flow_delivery", rapper1_name, rapper2_name)
        best_wordplay = self._find_category_winner("wordplay_creativity", rapper1_name, rapper2_name)
        best_punchlines = self._find_category_winner("punchlines_impact", rapper1_name, rapper2_name)
        best_crowd_appeal = self._find_category_winner("crowd_appeal", rapper1_name, rapper2_name)
        
        # Battle quality assessment
        avg_total = (rapper1_total + rapper2_total) / len(self.scores) if self.scores else 0
        if avg_total >= 70:
            quality = "legendary"
        elif avg_total >= 60:
            quality = "fire"
        elif avg_total >= 50:
            quality = "solid"
        else:
            quality = "weak"
        
        # Generate key moments
        key_moments = self._generate_key_moments()
        
        # Create judge summary
        judge_summary = self._generate_judge_summary(winner, margin, quality, rapper1_name, rapper2_name)
        
        self.final_judgment = RapBattleJudgment(
            rapper1_total=rapper1_total,
            rapper2_total=rapper2_total,
            winner=winner,
            margin=margin,
            best_flow=best_flow,
            best_wordplay=best_wordplay,
            best_punchlines=best_punchlines,
            best_crowd_appeal=best_crowd_appeal,
            battle_quality=quality,
            key_moments=key_moments,
            judge_summary=judge_summary
        )
        
        if ui:
            self._display_final_judgment(ui, rapper1_name, rapper2_name)
        
        return self.final_judgment
    
    def _find_category_winner(self, category: str, rapper1_name: str, rapper2_name: str) -> str:
        """Find which rapper performed better in a specific category"""
        rapper1_avg = sum(getattr(s, category) for s in self.scores if s.rapper == rapper1_name)
        rapper2_avg = sum(getattr(s, category) for s in self.scores if s.rapper == rapper2_name)
        
        rapper1_count = len([s for s in self.scores if s.rapper == rapper1_name])
        rapper2_count = len([s for s in self.scores if s.rapper == rapper2_name])
        
        if rapper1_count > 0:
            rapper1_avg /= rapper1_count
        if rapper2_count > 0:
            rapper2_avg /= rapper2_count
        
        if abs(rapper1_avg - rapper2_avg) < 0.5:
            return "tie"
        return rapper1_name if rapper1_avg > rapper2_avg else rapper2_name
    
    def _generate_key_moments(self) -> List[str]:
        """Generate key moments from the battle"""
        moments = []
        
        if self.scores:
            # Find highest scoring round
            best_round = max(self.scores, key=lambda s: s.total_score)
            moments.append(f"Round {best_round.round_number}: {best_round.rapper}'s dominant performance ({best_round.total_score:.1f}/80)")
            
            # Find best bars mentioned
            for score in self.scores:
                if score.best_bars:
                    moments.append(f"{score.rapper}'s best bar: \"{score.best_bars[0]}\"")
                    break  # Just one example
        
        return moments[:3]  # Limit to top 3 moments
    
    def _generate_judge_summary(self, winner: str, margin: float, quality: str, rapper1_name: str, rapper2_name: str) -> str:
        """Generate comprehensive judge summary"""
        if winner == "tie":
            result_text = f"This battle was too close to call - both {rapper1_name} and {rapper2_name} brought their A-game (margin: {margin:.1f} points)."
        else:
            result_text = f"{winner} takes this battle with a {margin:.1f} point margin."
        
        quality_text = f"Overall battle quality was {quality}."
        
        return f"{result_text} {quality_text} Both rappers showed skills and brought entertainment value to the cypher."
    
    def _create_default_judgment(self, rapper1_name: str, rapper2_name: str) -> RapBattleJudgment:
        """Create default judgment if no scores available"""
        return RapBattleJudgment(
            rapper1_total=0.0,
            rapper2_total=0.0,
            winner="tie",
            margin=0.0,
            best_flow="tie",
            best_wordplay="tie",
            best_punchlines="tie",
            best_crowd_appeal="tie",
            battle_quality="incomplete",
            key_moments=["Battle evaluation incomplete"],
            judge_summary="Unable to complete full battle evaluation due to technical issues."
        )
    
    def _display_round_score(self, score: RapBattleScore, ui: 'DebateUI'):
        """Display round score using Rich UI"""
        from agentic.tui.rich_ui import DebateUIComponents
        
        # Create score panel
        score_text = f"""
**{score.rapper} - Round {score.round_number} Score: {score.total_score:.1f}/80**

**Category Scores:**
• Flow & Delivery: {score.flow_delivery:.1f}/10
• Lyrical Complexity: {score.lyrical_complexity:.1f}/10  
• Wordplay & Creativity: {score.wordplay_creativity:.1f}/10
• Punchlines & Impact: {score.punchlines_impact:.1f}/10
• Crowd Appeal: {score.crowd_appeal:.1f}/10
• Battle Tactics: {score.battle_tactics:.1f}/10
• Rhyme Scheme: {score.rhyme_scheme:.1f}/10
• Originality: {score.originality:.1f}/10

**Best Bars:** {', '.join(f'"{bar}"' for bar in score.best_bars)}
**Areas to Improve:** {', '.join(score.weaknesses)}

**Judge Comments:** {score.judge_comments}
        """
        
        score_panel = DebateUIComponents.create_speaker_panel(
            "Battle Judge Scorecard", "🎤", score_text.strip()
        )
        ui.console.print(score_panel)
    
    def _display_final_judgment(self, ui: 'DebateUI', rapper1_name: str, rapper2_name: str):
        """Display final judgment using Rich UI"""
        from agentic.tui.rich_ui import DebateUIComponents
        
        judgment = self.final_judgment
        
        winner_text = "🏆 RAP BATTLE WINNER 🏆"
        if judgment.winner == "tie":
            result = f"**BATTLE TIE** (Margin: {judgment.margin:.1f} points)"
        else:
            result = f"**{judgment.winner.upper()} WINS** by {judgment.margin:.1f} points"
        
        final_text = f"""
{result}

**Final Scores:**
🎤 {rapper1_name} Total: {judgment.rapper1_total:.1f}
🎤 {rapper2_name} Total: {judgment.rapper2_total:.1f}

**Category Winners:**
• Best Flow: {judgment.best_flow}
• Best Wordplay: {judgment.best_wordplay}
• Best Punchlines: {judgment.best_punchlines}
• Best Crowd Appeal: {judgment.best_crowd_appeal}

**Battle Quality:** {judgment.battle_quality.title()}

**Key Moments:**
{chr(10).join(f"• {moment}" for moment in judgment.key_moments)}

**Judge's Summary:**
{judgment.judge_summary}
        """
        
        judgment_panel = DebateUIComponents.create_speaker_panel(
            winner_text, "🎤", final_text.strip()
        )
        ui.console.print(judgment_panel)
    
    def get_scoreboard(self) -> Dict:
        """Get complete scoreboard data"""
        return {
            "individual_scores": [score.to_dict() for score in self.scores],
            "final_judgment": self.final_judgment.to_dict() if self.final_judgment else None
        }


def create_rap_battle_judge(model_name: str = "openai-gpt4o") -> RapBattleJudge:
    """Factory function to create rap battle judge"""
    return RapBattleJudge(model_name)