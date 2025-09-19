import json
from camel.toolkits import FunctionTool
import requests
import re
CLEANR = re.compile('<.*?>') 
from urllib.parse import quote

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

def subclasses(ontology: str, owl_class_iri: str = None) -> str:
    """Retrieve subclasses of a given OWL class from AberOWL.
    Args:
        ontology (str): The ontology to use (e.g., "HP" for the Human Phenotype Ontology).
        owl_class_iri (str): The OWL class (e.g., "<http://purl.obolibrary.org/obo/HP_0000001>"). If None, retrieves subclasses of owl:Thing.
    Returns:
        list: list of subclasses of the OWL class.
    """
    if owl_class_iri.startswith("http"):
        owl_class_iri = f"<{owl_class_iri}>"
    print(f"Retrieving subclasses of {owl_class_iri if owl_class_iri else 'owl:Thing'} from {ontology} ontology...")
    if owl_class_iri is None or owl_class_iri.lower() == "owl:thing":
        response = requests.get(f"http://localhost:8001/api/api/runQuery.groovy?direct=true&axioms=true&query=%3Chttp%3A%2F%2Fwww.w3.org/2002/07/owl%23Thing%3E&type=subclass")
    else:
        response = requests.get(f"http://localhost:8001/api/api/runQuery.groovy",
                            params=f"type=subclass&query={quote(owl_class_iri)}&ontology={ontology}")
    response.raise_for_status()
    data = response.json()
    result = []
    if len(data['result']) > 0:
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
    response = requests.get(f"http://localhost:8001/api/class/_startwith",
                            params=f"query={quote(search_term)}&ontology={ontology}")
    response.raise_for_status()
    data = response.json()
    result = []
    if 'status' in data and data['status'] == 'ok' and len(data['result']) > 0:
        for item in data['result']:
            item = f"""iri: {item['class']}\nLabel: {item['label']}"""
            result.append(item)
    return "\n\n".join(result)

def object_properties(ontology: str) -> str:
    """Retrieve object properties of a given property from AberOWL.
    Args:
        ontology (str): The ontology to use (e.g., "HP" for the Human Phenotype Ontology).
    Returns:
        list: list of object properties of the given property.
    """
    print(f"Retrieving object properties of {ontology} ontology...")
    def get_object_properties(prop: str) -> dict:
        response = requests.get(f"http://localhost:8001/api/api/getObjectProperties.groovy",
                                params=f"ontology={ontology}&property={quote(prop)}")
        response.raise_for_status()
        result = response.json()['result']
        for item in result:
            item['subproperties'] = get_object_properties(item['class'])
        return result
    response = requests.get(f"http://localhost:8001/api/api/getObjectProperties.groovy",
                            params=f"ontology={ontology}")
    response.raise_for_status()
    result = response.json()['result']
    for item in result:
        item['subproperties'] = get_object_properties(item['class'])
    return json.dumps(result)

subclasses_tool = FunctionTool(subclasses)
search_tool = FunctionTool(search)
object_properties_tool = FunctionTool(object_properties)

if __name__ == "__main__":
    print(subclasses("GO"))