from camel.toolkits import FunctionTool
import requests
import re
CLEANR = re.compile('<.*?>') 
from urllib.parse import quote

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

def subclasses(ontology: str, owl_class_label: str = None) -> str:
    """Retrieve subclasses of a given OWL class from AberOWL.
    Args:
        ontology (str): The ontology to use (e.g., "HP" for the Human Phenotype Ontology).
        owl_class_label (str): The OWL class (e.g., "Phenotypic abnormality"). If None, retrieves subclasses of owl:Thing.
    Returns:
        list: list of subclasses of the OWL class.
    """
    print(f"Retrieving subclasses of {owl_class_label if owl_class_label else 'owl:Thing'} from {ontology} ontology...")
    if owl_class_label is None or owl_class_label.lower() == "owl:thing":
        response = requests.get(f"http://aber-owl.net/api/dlquery",
                                params=f"type=subclass&direct=true&query=<http://www.w3.org/2002/07/owl%23Thing>&ontology={ontology}")
    else:
        if owl_class_label.find(' ') != -1:
            owl_class_label = f'%27{quote(owl_class_label)}%27'
        response = requests.get(f"http://aber-owl.net/api/dlquery",
                            params=f"axioms=true&labels=true&type=subclass&query={owl_class_label}&ontology={ontology}")
    response.raise_for_status()
    data = response.json()
    result = []
    if 'status' in data and data['status'] == 'ok' and len(data['result']) > 0:
        for item in data['result']:
            if 'class' not in item:
                continue
            item = f"""iri: {item['class']}
Label: {item['label']}
Synonyms: {", ".join(item['synonyms']) if 'synonyms' in item else 'None'}
Definition: {item['definition'][0] if 'definition' in item else 'None'}"""
            result.append(item)
    return "\n\n".join(result)

def search(ontology: str, search_term: str) -> str:
    """Search for classes in a given ontology from AberOWL.
    Args:
        ontology (str): The ontology to use (e.g., "HP" for the Human Phenotype Ontology).
        search_term (str): The search term (e.g., "Phenotypic abnormality").
    Returns:
        list: list of classes matching the search term.
    """
    print(f"Searching for {search_term} in {ontology} ontology...")
    response = requests.get(f"http://aber-owl.net/api/class/_startwith",
                            params=f"query={quote(search_term)}&ontology={ontology}")
    response.raise_for_status()
    data = response.json()
    result = []
    if 'status' in data and data['status'] == 'ok' and len(data['result']) > 0:
        for item in data['result']:
            item = f"""iri: {item['class']}\nLabel: {item['label']}"""
            result.append(item)
    return "\n\n".join(result)

subclasses_tool = FunctionTool(subclasses)
search_tool = FunctionTool(search)

if __name__ == "__main__":
    print(subclasses("AGRO"))