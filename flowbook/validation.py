import json
from jsonschema import validate, ValidationError

def validate_flowbook(data, schema_path="schema/flowbook.schema.json"):
    with open(schema_path, "r") as f:
        schema = json.load(f)
    try:
        validate(instance=data, schema=schema)
        print("✅ Flowbook file is valid.")
        return True
    except ValidationError as e:
        print(f"❌ Invalid Flowbook file: {e.message}")
        return False
