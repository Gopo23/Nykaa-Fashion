import os
import re

base_dir = r"c:\Users\Gourav\Desktop\Nykaa Fashion"
command_center_dir = os.path.join(base_dir, "stitch_nykaa_conversion_command_center")
views_dir = os.path.join(base_dir, "frontend", "src", "views")
os.makedirs(views_dir, exist_ok=True)

mappings = {
    "command_center_overview/code.html": "overview.html",
    "priority_action_queue/code.html": "action-queue.html",
    "impact_simulator/code.html": "impact-simulator.html",
    "category_brand_matrix/code.html": "category-deep-dive.html"
}

for src, dest in mappings.items():
    src_path = os.path.join(command_center_dir, src)
    dest_path = os.path.join(views_dir, dest)
    
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract everything inside <main ...> ... </main>
    # Using regex to find the content
    match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)
    if match:
        inner_html = match.group(1)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(inner_html)
        print(f"Extracted to {dest}")
    else:
        print(f"Could not find <main> in {src}")
