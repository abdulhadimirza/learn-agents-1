#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, router, start
from crewai import CrewOutput
from dotenv import load_dotenv

from content_review_flow.crews.writer_crew.writer_crew import WriterCrew
from content_review_flow.crews.reviewer_crew.reviewer_crew import ReviewerCrew, ReviewResult

class ReviewState(BaseModel):
    topic: str = ""
    draft: str = ""
    feedback: str = ""
    score: int = 0
    iteration: int = 0

class ContentReviewFlow(Flow[ReviewState]):

    @start()
    def generate_draft(self):
        print(f"\n--- Generating Draft (Iteration {self.state.iteration + 1}) ---")
        print(f"Topic: {self.state.topic}")
        if self.state.feedback:
            print(f"Feedback to incorporate: {self.state.feedback}")
        
        result = WriterCrew().crew().kickoff(inputs={
            "topic": self.state.topic,
            "feedback": self.state.feedback
        })
        
        if isinstance(result, CrewOutput):
            self.state.draft = result.raw
        else:
            self.state.draft = str(result)
        self.state.iteration += 1
        
        return self.state.draft

    @listen(generate_draft)
    def review_draft(self):
        print("\n--- Reviewing Draft ---")
        print(f"Draft to review: {self.state.draft}")
        
        result = ReviewerCrew().crew().kickoff(inputs={
            "draft": self.state.draft
        })
        
        if isinstance(result, CrewOutput) and result.pydantic:
            review_result = result.pydantic
            if isinstance(review_result, ReviewResult):
                self.state.score = review_result.score
                self.state.feedback = review_result.feedback
        else:
            # Fallback if parsing fails
            self.state.score = 5
            self.state.feedback = "Grammar review completed, but structured feedback parsing failed."
        
        return self.state.score

    @router(review_draft)
    def route_based_on_score(self):
        print(f"\n--- Routing (Score: {self.state.score}) ---")
        
        if self.state.score >= 8:
            return "approved"
        elif self.state.iteration >= 3:
            print("Max iterations reached. Approving current draft to prevent infinite loop.")
            return "approved"
        else:
            print("Draft needs improvement. Routing back to writer...")
            return "needs_improvement"

    @listen("approved")
    def finalize(self):
        print("\n--- Finalizing ---")
        print(f"Final Approved Draft: {self.state.draft}")
        
        with open("draft.md", "w", encoding="utf-8") as f:
            f.write(self.state.draft)
        print("Draft saved to draft.md")
        return self.state.draft

    @listen("needs_improvement")
    def loop_back(self):
        print("\n--- Looping Back ---")
        self.generate_draft()


def kickoff():
    load_dotenv()
    flow = ContentReviewFlow(name="ContentReviewFlow")
    flow.state.topic = "The future of AI agents in 2026"
    final_output = flow.kickoff()
    print("\n=== FLOW COMPLETED ===")

def plot():
    flow = ContentReviewFlow(name="ContentReviewFlow")
    flow.plot()

if __name__ == "__main__":
    kickoff()
