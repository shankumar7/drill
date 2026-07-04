import os
import re

directory = r"C:\Users\Administrator\Desktop\military drill project\drill\backend\evaluation\rules"

for filename in os.listdir(directory):
    if filename.endswith(".py"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Matches: status = "pass" if score >= 80 else "fail"
        # and replaces the number with 90.
        new_content = re.sub(
            r'status\s*=\s*"pass"\s*if\s+([a-zA-Z0-9_]+)\s*>=\s*[0-9]+', 
            r'status = "pass" if \1 >= 90', 
            content
        )
        
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Updated {filename}")
