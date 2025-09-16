import sys
import json

def parse_obo(obo_path):
    classes = {}
    properties = {}
    current_id = None
    current_name = None
    current_type = None
    with open(obo_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '[Term]':
                current_type = 'class'
                current_id = None
                current_name = None
            elif line == '[Typedef]':
                current_type = 'property'
                current_id = None
                current_name = None
            elif line.startswith('id:'):
                current_id = line[3:].strip()
            elif line.startswith('name:'):
                current_name = line[5:].strip()
            elif line == '' and current_id and current_name and current_type:
                if current_type == 'class':
                    classes[current_id] = current_name
                elif current_type == 'property':
                    properties[current_id] = current_name
                current_id = None
                current_name = None
                current_type = None
        # Handle last entry
        if current_id and current_name and current_type:
            if current_type == 'class':
                classes[current_id] = current_name
            elif current_type == 'property':
                properties[current_id] = current_name
    return classes, properties

def generate_examples(classes, properties):
    class_items = list(classes.items())
    prop_items = list(properties.items())
    examples = []
    # Example 1: class with property some (class or class)
    if len(class_items) >= 3 and prop_items:
        c1_id, c1_name = class_items[0]
        c2_id, c2_name = class_items[1]
        c3_id, c3_name = class_items[2]
        p_id, p_name = prop_items[0]
        nl = f"{c1_name.lower()}s with {p_name.lower()} some ({c2_name.lower()} or {c3_name.lower()})"
        entities = {
            "classes": {
                c1_id: {"label": c1_name},
                c2_id: {"label": c2_name},
                c3_id: {"label": c3_name}
            },
            "properties": {
                p_id: {"label": p_name}
            }
        }
        manchester = f"{c1_name} and ({p_name} some ({c2_name} or {c3_name}))"
        examples.append((nl, entities, manchester))
    # Example 2: class with property exactly n other class
    if len(class_items) >= 2 and prop_items:
        c1_id, c1_name = class_items[0]
        c2_id, c2_name = class_items[1]
        p_id, p_name = prop_items[0]
        nl = f"{c1_name.lower()}s with exactly 2 {c2_name.lower()}s"
        entities = {
            "classes": {
                c1_id: {"label": c1_name},
                c2_id: {"label": c2_name}
            },
            "properties": {
                p_id: {"label": p_name}
            }
        }
        manchester = f"{c1_name} and ({p_name} exactly 2 {c2_name})"
        examples.append((nl, entities, manchester))
    # Example 3: class or class
    if len(class_items) >= 2:
        c1_id, c1_name = class_items[0]
        c2_id, c2_name = class_items[1]
        nl = f"{c1_name.lower()} or {c2_name.lower()}s"
        entities = {
            "classes": {
                c1_id: {"label": c1_name},
                c2_id: {"label": c2_name}
            },
            "properties": {}
        }
        manchester = f"{c1_name} or {c2_name}"
        examples.append((nl, entities, manchester))
    # Example 4: class that property only other class
    if len(class_items) >= 2 and prop_items:
        c1_id, c1_name = class_items[0]
        c2_id, c2_name = class_items[1]
        p_id, p_name = prop_items[0]
        nl = f"{c1_name.lower()}s that {p_name.lower()} only {c2_name.lower()}s"
        entities = {
            "classes": {
                c1_id: {"label": c1_name},
                c2_id: {"label": c2_name}
            },
            "properties": {
                p_id: {"label": p_name}
            }
        }
        manchester = f"{c1_name} and ({p_name} only {c2_name})"
        examples.append((nl, entities, manchester))
    return examples

def format_example(nl, entities, manchester, idx):
    return f"## EXAMPLE {idx}:\nNatural Language Query: \"{nl}\"\n\nValidated Entities:\n``\n{json.dumps(entities, indent=2)}\n``\nResulting Manchester Expression:\n\n{manchester}\n"

def main():
    if len(sys.argv) < 2:
        print("Usage: python exgen.py <ontology.obo> [output.md]")
        sys.exit(1)
    obo_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "examples_output.md"
    classes, properties = parse_obo(obo_path)
    examples = generate_examples(classes, properties)
    with open(output_path, 'w') as out:
        for i, (nl, entities, manchester) in enumerate(examples, 1):
            formatted = format_example(nl, entities, manchester, i)
            print(formatted)
            out.write(formatted + "\n")
    print(f"\nExamples written to {output_path}")

if __name__ == "__main__":
    main()