from tools.aberowl import object_properties_tool, subclasses_tool
from browser_agent import browse_tool

from models import deepseek_model, gemini_model
from camel.agents import ChatAgent
import json

def definition(ontology, text):
    """Get class description in ManchesterOWL syntax from definition in natural language.
    Args:
        ontology (str): The ontology to use (e.g., "HP" for the Human Phenotype Ontology).
        text (str): The natural language definition of the class.
    Returns:
        str: The class description in ManchesterOWL syntax.
    """
    
    system_message = """You are an ontology expert.
 Your task is to build the class description in ManchesterOWL syntax from the following natural language definition.
 First, find the classes in the definition using browse tool.
 Second, find the object properties in the definition using object_properties tool.
 Finally, provide a class label or build the class description in ManchesterOWL syntax using the classes and object properties found.
 Here are examples:
 - Any process that increases the rate of the directed movement of calcium ions into the cytosol of a cell. The cytosol is that part of the cytoplasm that does not contain membranous or particulate subcellular components. => 'biological regulation' and ('positively regulates' some 'calcium ion transport into cytosol')
 - The increase in size or mass of an entire organism, a part of an organism or a cell, where the increase in size or mass has the specific outcome of the progression of the organism over time from one condition to another. => 	growth and ('part of' some 'developmental process')
"""
    def_agent = ChatAgent(
        model=gemini_model,
        tools=[browse_tool, object_properties_tool],
        system_message=system_message,)
    prompt = f"""I have the following class description in natural language:
    {text}.
    Your tasks are:
    1. Identify concepts and object properties in the description.
    2. Find relevant concepts in AberOWL using the browse tool.
    3. Find relevant object properties in AberOWL using the object_properties tool.
    4. Describe the class description using the concepts and object properties found using ManchesterOWL syntax.
    Output only the class description in ManchesterOWL syntax."""
    response = def_agent.step(prompt).msgs[0].content

    critic_system_message = """You are a critic agent. You evaluate the output of another agent.
    Your task is to check if the natural language definition and class description in ManchesterOWL syntax are correct.
    If it is not correct, explain what is wrong and suggest steps to fix it.
    If it is correct, just say "OK"."""
    critic_agent = ChatAgent(
        model=gemini_model,
        tools=[],
        system_message=critic_system_message)
    iteration = 0
    while True:
        critic_prompt = f"""Here is the natural language definition:
        {text}.
        Here is the class description:
        {response}"""
        critic_response = critic_agent.step(critic_prompt).msgs[0].content
        print(f"Critic response: {critic_response}")
        if critic_response.strip().lower() == "ok":
            break
        elif iteration > 2:
            print("Too many iterations, stopping.")
            break
        else:
            iteration += 1          
            prompt = f"""The class description {response} is not correct.
            {critic_response}
            Please find more relevant classes in AberOWL, fix the class description
            and output only the class description in ManchesterOWL syntax."""
            response = def_agent.step(prompt).msgs[0].content
    print(f"Agent response: {response}")
    return response


if __name__ == "__main__":
    definition("GO", "procces that regulates cell death")