import re
import os
import sys

def refactor_host_agent_docstrings(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    in_function = False
    in_docstring = False
    docstring_buffer = []
    function_indent = ""
    
    # Regex to find function definitions
    function_pattern = re.compile(r"^\s*(async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*")

    # First pass: Fix the instruction string in create_agent
    # This was a specific issue with extra triple quotes
    instruction_fixed = False
    temp_lines = list(lines) # Create a mutable copy for the first pass
    
    i = 0
    while i < len(temp_lines):
        line = temp_lines[i]
        if not instruction_fixed and "instruction = f\"\"\"" in line:
            # Find the end of the instruction string
            j = i + 1
            while j < len(temp_lines):
                if temp_lines[j].strip() == '"""':
                    # Check if there's another """ immediately after
                    if j + 1 < len(temp_lines) and temp_lines[j+1].strip() == '"""':
                        # This is the extra """
                        temp_lines.pop(j+1) # Remove the extra line
                        instruction_fixed = True
                        break
                j += 1
        if instruction_fixed:
            break # Only fix once
        i += 1
    lines = temp_lines # Update lines with the fixed instruction

    # Second pass: Process docstrings
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()

        match = function_pattern.match(line)
        if match:
            in_function = True
            function_indent = line[:line.find(stripped_line)]
            new_lines.append(line)
            i += 1
            continue

        if in_function:
            # Detect docstring start
            if '"""' in stripped_line and not in_docstring:
                in_docstring = True
                docstring_buffer = [line] # Start collecting docstring lines
                
                # Check if it's a single-line docstring
                if stripped_line.count('"""') == 2:
                    in_docstring = False
                    new_lines.append(line)
                    docstring_buffer = []
                    in_function = False # Assume function body starts after single-line docstring
                i += 1
                continue

            # Inside docstring
            if in_docstring:
                docstring_buffer.append(line)
                if stripped_line.endswith('"""'):
                    in_docstring = False
                    
                    # Process multi-line docstring
                    docstring_content = "".join(docstring_buffer)
                    
                    # Extract content between triple quotes
                    start_quote_index = docstring_content.find('"""')
                    end_quote_index = docstring_content.rfind('"""')
                    
                    actual_docstring_text = ""
                    if start_quote_index != -1 and end_quote_index != -1 and start_quote_index != end_quote_index:
                        actual_docstring_text = docstring_content[start_quote_index + 3:end_quote_index].strip()
                    else:
                        actual_docstring_text = docstring_content.strip('"""').strip()

                    reconstructed_docstring_lines = [f'{function_indent}        """{actual_docstring_text}'']
                    
                    # Check for Args/Returns that might have been outside
                    j = i
                    while j < len(lines):
                        next_line_stripped = lines[j].strip()
                        if next_line_stripped.startswith("Args:") or next_line_stripped.startswith("Returns:"):
                            reconstructed_docstring_lines.append(lines[j].rstrip() + '\n') # Keep original indentation
                            j += 1
                        elif next_line_stripped == '"""': # This is the closing triple quote that was misplaced
                            j += 1 # Skip this line
                        else:
                            break
                    
                    reconstructed_docstring_lines.append(f'{function_indent}        """\n')
                    new_lines.extend(reconstructed_docstring_lines)
                    docstring_buffer = []
                    i = j # Adjust i to skip lines that were moved into the docstring
                    in_function = False # Assume function body starts after docstring
                else:
                    i += 1
                continue
            
            # After docstring, but still in function (looking for actual code)
            if not in_docstring and in_function:
                # Check for misplaced Args/Returns that were not caught by the docstring reconstruction
                if stripped_line.startswith("Args:") or stripped_line.startswith("Returns:"):
                    i += 1 # Skip these lines
                    continue
                else:
                    new_lines.append(line)
                    in_function = False # Assume function body starts
                    i += 1
                    continue
        else:
            new_lines.append(line)
            i += 1
            
    # Write the modified content back to the file
    with open(file_path, 'w') as f:
        f.writelines(new_lines)

    print(f"Refactoring complete for {file_path}. Please review the changes.")

# Main execution block
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python refactor_script.py <path_to_host_agent.py>")
        sys.exit(1)
    
    target_file_path = sys.argv[1]
    refactor_host_agent_docstrings(target_file_path)
