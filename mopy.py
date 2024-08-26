#!/usr/bin/env python2
import re

def open_modelica(file_path, model_path):
    """Opens a Modelica file and retrieves the content of the specified model from nested packages."""
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Split the model path into parts (packages and final model)
    path_parts = model_path.split('.')
    
    # Initialize the current scope of content to search within
    current_content = content
    
    # Process each part in the model path
    for i, part in enumerate(path_parts):
        if i < len(path_parts) - 1:  # This part is a package
            # Regex to extract the content within this package
            pattern_text = r'\bpackage\s+' + re.escape(part) + r'\s*(.*?)\s*end ' + re.escape(part) + ';'
        else:  # The last part is the model
            # Regex to extract the content within this model
            pattern_text = r'\bmodel\s+' + re.escape(part) + r'(.*?)end ' + re.escape(part) + ';'
        
        pattern = re.compile(pattern_text, re.DOTALL)
        
        # Print the current regex pattern
        print("Current regex pattern: {}".format(pattern_text))
        
        # Search for the current part within the current scope of content
        match = pattern.search(current_content)
        if not match:
            raise ValueError("Segment '{}' not found in the provided scope.".format(part))
        
        # Narrow down the content scope to the matched content for the next iteration
        current_content = match.group(1) if i < len(path_parts) - 1 else match.group(0)
    
    # Return the final matched content
    return current_content, content

def add_component(model_content, com_type, com_name, com_para=None):
    """ Adds a new component within the model. """
    insertion_point = model_content.rfind('equation')
    component_string = '  {} {}'.format(com_type, com_name)
    if com_para:
        component_string += '({})'.format(com_para)
    component_string += ';\n    '
    
    new_model_content = model_content[:insertion_point] + component_string + model_content[insertion_point:]
    return new_model_content

def add_parameter(model_content, param_type, param_name, param_value, annotation=None):
    """Adds a new parameter within the model."""
    insertion_point = model_content.rfind('equation')
    parameter_string = '  parameter {} {} = {}'.format(param_type, param_name, param_value)
    if annotation:
        parameter_string += ' "{}"'.format(annotation)
    parameter_string += ';'
    
    new_model_content = model_content[:insertion_point] + parameter_string + '\n    ' + model_content[insertion_point:]
    return new_model_content

def edit_parameter(model_content, para_name, para_value):
    """ Edits a specified parameter within the model. Handles various parameter types. """
    # Regex pattern modified to match any parameter type and retain the entire declaration
    parameter_pattern = re.compile(r'(parameter .*? {} = )(.*?);'.format(re.escape(para_name)))

    # Function to replace the matched parameter with the new value
    def replacement(match):
        return '{}{};'.format(match.group(1), para_value)
    
    # Replace the found pattern with the new parameter value, using the replacement function
    new_model_content = parameter_pattern.sub(replacement, model_content)
    return new_model_content

def edit_connection(model_content, a_old, b_old, a_new, b_new):
    """ Edits existing connections within the model. """
    # Adjust the pattern to match Modelica's connect function
    connection_pattern = re.compile(r'connect\(' + re.escape(a_old) + r'\s*,\s*' + re.escape(b_old) + r'\)')
    # Replace the old connection with the new one
    new_model_content = connection_pattern.sub(r'connect(' + a_new + ',' + b_new + ')', model_content)
    return new_model_content

def add_connection(model_content, a_new, b_new):
    """ Adds a new connection within the model, right after the 'equation' keyword, with one more level of indentation. """
    # Find the 'equation' keyword and capture its indentation
    match = re.search(r'(\s*)equation\b', model_content)
    if not match:
        raise ValueError("No 'equation' keyword found in the model content.")
    
    # Determine the existing indentation level
    existing_indent = match.group(1)
    # Create a new indentation level by adding more spaces (assuming space-based indentation)
    # You can adjust the number of spaces added based on your style guide (e.g., 4 spaces, 2 spaces, etc.)
    new_indent = existing_indent + '\t'  # Adds four more spaces for the new indent level
    
    # Prepare the connection string to be inserted, using the new indentation level
    connection_string = '{}connect({}, {});'.format(new_indent, a_new, b_new)
    
    # Find the insertion point right after the 'equation' keyword
    insertion_point = match.end()
    
    # Insert the new connection string at the correct position
    new_model_content = model_content[:insertion_point] + connection_string + model_content[insertion_point:]
    return new_model_content

def generate_new_model(full_content, model_content, new_model_name):
    old_model_name_match = re.search(r'\bmodel\s+(\w+)', model_content)
    if not old_model_name_match:
        raise ValueError("Could not find the model name in the model content.")
    old_model_name = old_model_name_match.group(1)

    # Change the model name and the end name
    new_model_content = re.sub(r'\bmodel\s+\w+', 'model ' + new_model_name, model_content, 1)
    new_model_content = re.sub(r'\bend\s+\w+;', 'end ' + new_model_name + ';', new_model_content, 1)
    
    # Find the end of the target old model
    model_end_match = re.search(r'(end\s+' + re.escape(old_model_name) + r';)', full_content)
    if not model_end_match:
        raise ValueError("Could not find the end of the target model.")
    insertion_point = model_end_match.end()
    
    # Insert the new model content immediately after the end of the target old model
    new_full_content = full_content[:insertion_point] + '\n\n' + new_model_content + '\n' + full_content[insertion_point:]
    
    return new_full_content

def extend_old_model(new_model_content, old_model_name, new_model_name):
    """Extends the old model in the new model by adding 'extends old_model;' keyword after the 'model new_model' keyword."""
    # Get the indentation of the new model
    new_model_indent_match = re.search(r'(^\s*)model\s+' + re.escape(new_model_name), new_model_content, re.MULTILINE)
    new_model_indent = new_model_indent_match.group(1) if new_model_indent_match else ''

    # Add the 'extends old_model;' keyword
    extend_statement = new_model_indent + '  ' + 'extends ' + old_model_name + ';'

    # Insert the extend statement after the 'model new_model' keyword
    new_model_content_lines = new_model_content.split('\n')
    for i, line in enumerate(new_model_content_lines):
        if re.match(r'^\s*model\s+' + re.escape(new_model_name), line):
            new_model_content_lines.insert(i + 1, extend_statement)
            break

    # Join the lines back into a single string
    new_model_content = '\n'.join(new_model_content_lines)
    return new_model_content

def save_changes(new_file_path, full_content):
    """ Saves the changes to a new Modelica file. """
    with open(new_file_path, 'w') as file:
        file.write(full_content)

