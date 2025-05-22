import textwrap

def two_columns(text, column_width=40, spacing=4):
    wrapper = textwrap.TextWrapper(width=column_width)
    paragraphs = text.split('\n\n')  # Split by paragraphs
    
    # Distribute paragraphs alternately between columns
    left = []
    right = []
    for i, para in enumerate(paragraphs):
        if i % 2 == 0:
            left.extend(wrapper.wrap(para))
        else:
            right.extend(wrapper.wrap(para))
    
    # Format into columns
    max_lines = max(len(left), len(right))
    result = []
    for i in range(max_lines):
        l = left[i] if i < len(left) else ""
        r = right[i] if i < len(right) else ""
        result.append(f"{l.ljust(column_width)}{r}")
    
    return '\n'.join(result)

# Example usage
text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl.
\n\n
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
\n\n
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore.
\n\n
Eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident."""

print(two_columns(text))