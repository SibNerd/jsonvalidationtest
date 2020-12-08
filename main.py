import json
import os
import re
import jsonschema
from jsonschema import validate



def getSchemas(files):
    """Gets dict of all schemas.

    Args:
        files (list): list of schema files.

    Returns:
        schemas: dictionary of schemas, where keys are names of schemas and values are names of files.
    """
    schemas = {}
    for file in files: 
        schema = re.split(r'\.', file)
        schemas[schema[0]] = file
    return schemas

def validateJSON(file, schemas):
    """Validation of JSON files using JSON Schemas

    Args:
        file (file): open JSON file
        schemas (dict): dict of schemas

    Returns:
        message (str): message with info about validation.
    """
    try:
        data = json.load(file)
        if not data:
            message = f"JSON file '{file.name}' is empty.\n\n"
            return message
        else:
            if data['event'] not in schemas:
                message = f"JSON file '{file.name}' doesn't match any JSON schemas and can't be validated.\
                    \nAdd new schema or check 'event' parameter of chosen JSON file.\n\n"
                return message
            else: 
                try:
                    chosen_schema = schemas[data['event']]
                    with open(('schema/'+chosen_schema), 'r') as schema_file:
                        schema = validateSchema(schema_file)
                        validate(data['data'], schema)
                        message = f"JSON file '{file.name}' is valid.\n\n"
                        return message
                except jsonschema.exceptions.ValidationError as err:
                    path_to_err = err.path
                    if not path_to_err:
                        path = 'Root'
                    else:
                        path = path_to_err[0]
                    error_property = re.search(r'required property', err.message)
                    error_type = re.search(r'is not of type', err.message)
                    if error_type:
                        hint = 'Types should match for JSON to be valid.'
                    elif error_property:
                        hint = 'All of the required properties must be present for JSON to be valid.'
                    else:
                        hint = ''
                    message = f"Error in file '{file.name}':\nMessage: '{err.message}'.\
                        \nOccured in '{err.validator}' validator on level: {path}.\
                        \n{hint}\n\n"
                    return message
    except ValueError as err:
        message = f"Couldn't open {file}, error message: {err}."
        return message

def validateSchema(file):
    """Validates given JSON schema.

    Args:
        file (file): JSON schema file

    Returns:
        data (dict) - if Schema is valid.
        message (str) - if Schema is invalid.
    """
    try:
        data = json.load(file)
        return data
    except jsonschema.exceptions.SchemaError as err:
        message = f'Could not validate JSON shema.\
            \n Error message: {err.message}.\n\n'
        return message



if __name__ == "__main__":
    # Create dict of given schemas
    schema_files = os.listdir('schema/')
    schemas = getSchemas(schema_files)

    # Validate JSON files
    json_files = os.listdir('event/')
    with open('readme.txt', 'w') as out:
        for file in json_files:
            with open(('event/'+file), 'r') as json_file:
                result = validateJSON(json_file, schemas)
                out.write(result)
