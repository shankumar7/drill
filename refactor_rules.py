import os
import re

rules_dir = "backend/evaluation/rules"
files_to_read = ["posture.py", "shoulder_level.py", "head_alignment.py"]

combined_content = ""
for f in files_to_read:
    with open(os.path.join(rules_dir, f), "r") as file:
        content = file.read()
        # Remove imports from combined content to add them later
        content = re.sub(r'from backend.*?import.*?\n', '', content)
        content = re.sub(r'import math\n', '', content)
        combined_content += content + "\n\n"

header = """import math
from backend.core.types import PoseDetection, RuleResult
from backend.evaluation.rules.base import EvaluationRule
from backend.evaluation.geometry import calculate_angle, segment_length

"""

def create_specific_file(prefix, file_name):
    specific_content = header + combined_content
    # Rename classes
    specific_content = re.sub(r'class BackPostureRule', f'class {prefix}BackPostureRule', specific_content)
    specific_content = re.sub(r'class BodyPostureRule', f'class {prefix}BodyPostureRule', specific_content)
    specific_content = re.sub(r'class ShoulderLevelRule', f'class {prefix}ShoulderLevelRule', specific_content)
    specific_content = re.sub(r'class HeadAlignmentRule', f'class {prefix}HeadAlignmentRule', specific_content)
    
    with open(os.path.join(rules_dir, file_name), "w") as file:
        file.write(specific_content)

create_specific_file("Savdhan", "savdhan_shared.py")
create_specific_file("Vishram", "vishram_shared.py")
create_specific_file("Generic", "generic_shared.py")
print("Created shared files")
