import re

evaluator_path = "backend/evaluation/evaluator.py"
with open(evaluator_path, "r") as f:
    content = f.read()

# Add imports
imports = """
from backend.evaluation.rules.savdhan_shared import SavdhanBackPostureRule, SavdhanBodyPostureRule, SavdhanShoulderLevelRule, SavdhanHeadAlignmentRule
from backend.evaluation.rules.vishram_shared import VishramBackPostureRule, VishramBodyPostureRule, VishramShoulderLevelRule, VishramHeadAlignmentRule
from backend.evaluation.rules.generic_shared import GenericBackPostureRule, GenericBodyPostureRule, GenericShoulderLevelRule, GenericHeadAlignmentRule
"""

content = content.replace("from backend.evaluation.rules.head_alignment import HeadAlignmentRule\n", "")
content = content.replace("from backend.evaluation.rules.posture import BackPostureRule, BodyPostureRule\n", "")
content = content.replace("from backend.evaluation.rules.shoulder_level import ShoulderLevelRule\n", "")
content = imports + content

# Remove the shared list definition
content = re.sub(r'\s*shared\s*=\s*\[.*?\]\n', '\n', content, flags=re.MULTILINE | re.DOTALL)

# Replace HeadAlignmentRule() in SAVDHAN (first instance usually)
content = re.sub(r'HeadAlignmentRule\(\)', 'SavdhanHeadAlignmentRule()', content, count=1)

# Replace *shared in SAVDHAN (first instance)
content = re.sub(r'\*shared', 'SavdhanBackPostureRule(160, 210),\n                SavdhanBodyPostureRule(160, 200),\n                SavdhanShoulderLevelRule()', content, count=1)

# Replace HeadAlignmentRule() in VISHRAM (second instance)
content = re.sub(r'HeadAlignmentRule\(\)', 'VishramHeadAlignmentRule()', content, count=1)

# Replace *shared in VISHRAM (second instance)
content = re.sub(r'\*shared', 'VishramBackPostureRule(160, 210),\n                VishramBodyPostureRule(160, 200),\n                VishramShoulderLevelRule()', content, count=1)

# Replace remaining *shared
content = re.sub(r'\*shared', 'GenericBackPostureRule(160, 210),\n                GenericBodyPostureRule(160, 200),\n                GenericShoulderLevelRule()', content)

with open(evaluator_path, "w") as f:
    f.write(content)
print("Updated evaluator.py")
