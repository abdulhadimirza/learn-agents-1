from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, router, start
from crewai import Agent, Crew, Task, LLM
from dotenv import load_dotenv

# 1. Define the shared state for the flow
class ReviewState(BaseModel):
    topic: str = ""
    draft: str = ""
    feedback: str = ""
    score: int = 0
    iteration: int = 0

# 2. Define the Flow class
class ContentReviewFlow(Flow[ReviewState]):

    @start()
    def generate_draft(self):
        """
        Step 1: The Writer Agent generates a draft based on the topic and any feedback.
        """
        print(f"\n--- Generating Draft (Iteration {self.state.iteration + 1}) ---")
        print(f"Topic: {self.state.topic}")
        if self.state.feedback:
            print(f"Feedback to incorporate: {self.state.feedback}")
        
        # Define your Gemini LLM using LiteLLM syntax
        gemini_llm = LLM(model="gemini/gemini-flash-lite-latest")
        
        # Define the Writer Agent
        writer = Agent(
            role="Expert Content Writer",
            goal="Write a compelling, engaging, and well-structured draft about the given topic.",
            backstory="You are a renowned content creator known for producing high-quality articles.",
            llm=gemini_llm,
            verbose=True
        )
        
        # Define the Drafting Task
        draft_description = f"Write a comprehensive draft about: '{self.state.topic}'."
        if self.state.feedback:
            draft_description += f"\nCRITICAL INSTRUCTION: You must incorporate this feedback into your revision: '{self.state.feedback}'"
            
        drafting_task = Task(
            description=draft_description,
            expected_output="A full, well-written draft formatted in Markdown.",
            agent=writer
        )
        
        # Create a Crew, kickoff(), and save the result to self.state.draft
        crew = Crew(
            agents=[writer],
            tasks=[drafting_task],
            verbose=True
        )
        
        result = crew.kickoff()
        self.state.draft = result.raw
        self.state.iteration += 1
        
        return self.state.draft

    @listen(generate_draft)
    def review_draft(self):
        """
        Step 2: The Reviewer Agent reads the draft and provides a score (1-10) and feedback.
        """
        print("\n--- Reviewing Draft ---")
        print(f"Draft to review: {self.state.draft}")
        
        # TODO: Define your Reviewer Agent here
        # TODO: Define your Reviewing Task here (pass self.state.draft in the prompt)
        # Tip: You can enforce structured output using Pydantic models in the Task!

        # === Placeholder Simulation (Replace with actual CrewAI code) ===
        self.state.score = 7  # Change to >=8 to see it pass
        self.state.feedback = "The grammar is good, but needs more detail on the topic."
        
        return self.state.score

    @router(review_draft)
    def route_based_on_score(self):
        """
        Step 3: Route the flow based on the Reviewer's score.
        If the score is >= 8 or we've reached max iterations, we approve.
        Otherwise, we route back to needs_improvement.
        """
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
        """
        Step 4: The draft is approved! Finalize and save.
        """
        print("\n--- Finalizing ---")
        print(f"Final Approved Draft: {self.state.draft}")
        
        # TODO: Add any final steps, like saving the draft to a Markdown file.
        return self.state.draft

    @listen("needs_improvement")
    def loop_back(self):
        """
        Step 5: Trigger the generation step again with the feedback.
        """
        print("\n--- Looping Back ---")
        self.generate_draft()


if __name__ == "__main__":
    load_dotenv()
    
    # Initialize the flow
    flow = ContentReviewFlow()
    
    # Set the initial state
    flow.state.topic = "The future of AI agents in 2026"
    
    # Run the flow
    final_output = flow.kickoff()
    
    print("\n=== FLOW COMPLETED ===")
