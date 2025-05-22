def format_two_columns(left_text, right_text, width=40, spacing=4):
    left_lines = left_text.split('\n')
    right_lines = right_text.split('\n')
    
    max_lines = max(len(left_lines), len(right_lines))
    formatted = []
    
    for i in range(max_lines):
        left = left_lines[i] if i < len(left_lines) else ""
        right = right_lines[i] if i < len(right_lines) else ""
        
        # Format with spacing between columns
        line = f"{left.ljust(width)}{right}"
        formatted.append(line)
    
    return '\n'.join(formatted)

# Example usage
left_col = """This is some text
for the left column.
It has multiple lines."""

right_col = """Right column text
also with multiple lines.
And more text here."""

print(format_two_columns(left_col, right_col))