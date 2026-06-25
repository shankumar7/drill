import re

file_path = '/Users/shankumar/drill/web-ui/src/app/page.tsx'
with open(file_path, 'r') as f:
    content = f.read()

# Container background
content = content.replace('bg-[#0B0F19]', 'bg-slate-50')
content = content.replace('text-slate-200', 'text-slate-800')

# Text colors
content = content.replace('text-slate-100', 'text-slate-800')
content = content.replace('text-slate-300', 'text-slate-700')
content = content.replace('text-slate-400', 'text-slate-500')
content = content.replace('text-white', 'text-slate-800')
# Note: we might want to keep some text white if they are on dark buttons.
# Let's be careful. The blue buttons should still have text-white. 
# Revert "text-white" on buttons specifically, or just don't global replace "text-white".

