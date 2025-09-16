from tools.aberowl import subclasses_tool
from models import deepseek_model, gemini_model
from camel.agents import ChatAgent
import json

def main():
    system_message = """You are an ontology expert.
 You can browse ontologies using the AberOWL subclasses tool.
"""
    agent = ChatAgent(
        model=gemini_model,
        tools=[subclasses_tool,],
        system_message=system_message,)
    current_class = "owl:Thing"
    search_class = "protein that trasport o2"
    ontology = "GO"
    while True:
        prompt = f"""I want to find the class for {search_class} and its definition in the
         {ontology} ontology. Always use subclasses tool and look for subclasses of {current_class}
         and tell me the most relevant one where I need to subclass next.
         If the class matches my search found=True.
         If you cannot find the class suggest another class restart from another subclass of owl:Thing.
         Output in clean JSON format with keys: iri, label, next_class, reason, definition, found."""
        response = agent.step(prompt).msgs[0].content
        print(f"Agent response: {response}")
        start = response.find("{")
        end = response.rfind("}") + 1
        response = response[start:end]
        res = json.loads(response)
        if res["found"]:
            print(f"Found class: {res['label']} ({res['iri']})")
            print(f"Definition: {res['definition']}")
            break
        else:
            print(f"Next class to search: {res['next_class']}")
            print(f"Reason: {res['reason']}")
            current_class = res["next_class"]
if __name__ == "__main__":
    main()