"""Parser de Postman Collection v2.1 JSON."""


def parse_collection(input_file):
    """Parseia o arquivo JSON da collection Postman."""
    with open(input_file, "r") as f:
        import json
        return json.load(f)
