from tools.aberowl import subclasses_tool
from models import deepseek_model, gemini_model
from camel.agents import ChatAgent
from camel.toolkits import FunctionTool
import json

def browse(ontology, search_class):
    """Browse classes in a given ontology from AberOWL.
    Args:
        ontology (str): The ontology to use (e.g., "HP" for the Human Phenotype Ontology).
        search_class (str): The search class (e.g., "Phenotypic abnormality").
    Returns:
        str: The class matching the search term.
    """
    
    system_message = """You are an ontology expert.
 You can browse ontologies using the AberOWL subclasses tool.
"""
    agent = ChatAgent(
        model=gemini_model,
        tools=[subclasses_tool,],
        system_message=system_message,)
    current_class = "owl:Thing"
    res = None
    iteration = 0
    while True:
        iteration += 1
        if iteration > 10:
            print("Too many iterations, stopping.")
            break
        prompt = f"""I want to find the class for {search_class} and its definition in the
         {ontology} ontology. Always use subclasses tool and look for subclasses of {current_class}
         and tell me the most relevant one where I need to subclass next.
         If the class matches my search found=True.
         If you cannot find the class suggest another class restart from another relevant subclass.
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
    if res:
        return f"Label: {res['label']}\nIRI: {res['iri']}\nDefinition: {res['definition']}"
    return "No matching class found."

browse_tool = FunctionTool(browse)

if __name__ == "__main__":
    browse("GO", "cell death")