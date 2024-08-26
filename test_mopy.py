#!/usr/bin/env python2
from mopy import open_modelica
from mopy import add_connection
from mopy import save_changes
from mopy import generate_new_model
from mopy import extend_old_model
from mopy import add_component, add_parameter

# Example usage:
original_file_path = '../../Model/Example.mo'
new_file_path = '../../Model/Example1.mo'
model_path = 'Example.G.R4C3'
new_model_name = 'R4C3_New'

# Load the model
try:
    original_model_content, full_content = open_modelica(original_file_path, model_path)
    print("Model found and loaded successfully.")
except ValueError as e:
    print(str(e))

# Generate a new model with a different name
full_content_with_new_model = generate_new_model(full_content, original_model_content, new_model_name)

# Extend the old model in the new model
full_content_with_new_model = extend_old_model(full_content_with_new_model, 'R4C3', new_model_name)

# Make modifications
new_model_content = full_content_with_new_model  # Start with the original content
#new_model_content = add_component(new_model_content, 'Modelica.Blocks.Interfaces.RealInput', 'kkk')
#new_model_content = add_parameter(new_model_content, 'Modelica.SIunits.Area', 'A_w', '336/2', 'Area of external wall')
#new_model_content = edit_parameter(new_model_content, 'A_z', '100')
#new_model_content = edit_connection(new_model_content, 'HeaCap.u', 'conHea_zone', 'HeaCap.u', 'u_rad1')
#new_model_content = add_connection(new_model_content, 'A_new', 'B_new')

# Save the changes to a new file
save_changes(new_file_path, new_model_content)