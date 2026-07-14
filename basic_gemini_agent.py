import os
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

def run_agent():
    print("Welcome to the basic Gemini Agent!")
    prompt = input("Please enter your prompt: ")
    
    # Initialize the Gemini LLM
    gemini_llm = LLM(
        model="gemini/gemini-flash-lite-latest",
        # API key is automatically picked up from GEMINI_API_KEY or GOOGLE_API_KEY env var
    )

    # Create a basic agent
    basic_agent = Agent(
        role='Helpful Assistant',
        goal='Provide accurate and helpful responses to user prompts.',
        backstory='You are a helpful AI assistant powered by Google Gemini.',
        llm=gemini_llm,
        verbose=False
    )

    # Create a task based on the user prompt
    respond_task = Task(
        description=f'Respond to the following user prompt: "{prompt}"',
        expected_output='A clear, helpful, and concise response to the user prompt.',
        agent=basic_agent
    )

    # Create the crew and kickoff
    crew = Crew(
        agents=[basic_agent],
        tasks=[respond_task]
    )

    print("\nProcessing your request...\n")
    result = crew.kickoff()
    
    print("\n=== Agent Response ===")
    print(result)

if __name__ == "__main__":
    load_dotenv()
    
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment variables before running.")
        
    run_agent()
