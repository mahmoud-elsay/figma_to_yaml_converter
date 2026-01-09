#!/usr/bin/env python3
"""
Quick test of the updated converter
"""

import json
from pathlib import Path

# Import the converter classes
import sys

sys.path.insert(0, str(Path(__file__).parent))

from convert_to_yaml_v2 import FigmaNormalizer, SemanticMapper, YAMLConverter

# Load the test JSON
json_file = "ucrbA01Va5RCZ2x6HgTjvB.json"

with open(json_file, "r", encoding="utf-8") as f:
    figma_data = json.load(f)

# Normalize
normalizer = FigmaNormalizer()
normalized_nodes = normalizer.normalize(figma_data)

print(f"✅ Normalized {len(normalized_nodes)} nodes\n")

# Check for icons/images in normalized data
icon_count = sum(1 for n in normalized_nodes if n.get("type") == "ICON")
image_count = sum(1 for n in normalized_nodes if n.get("type") == "IMAGE")

print(f"📊 Found:")
print(f"   - {icon_count} ICON nodes")
print(f"   - {image_count} IMAGE nodes")
print()

# Map to screens
mapper = SemanticMapper()
screens = mapper.map_to_screens(normalized_nodes)

print(f"✅ Created {len(screens)} screens\n")


# Check for icons/images in screen output
def count_assets(element):
    icons = 0
    images = 0

    if isinstance(element, dict):
        if element.get("type") == "icon":
            icons += 1
        if element.get("type") == "image":
            images += 1

        for child in element.get("children", []):
            i, img = count_assets(child)
            icons += i
            images += img

    return icons, images


total_icons = 0
total_images = 0

for screen in screens:
    for child in screen.get("children", []):
        i, img = count_assets(child)
        total_icons += i
        total_images += img

print(f"📊 In screens:")
print(f"   - {total_icons} icon elements")
print(f"   - {total_images} image elements")
print()

# Show sample screen structure
if screens:
    print(f"📋 Sample screen: {screens[0]['name']}")
    import yaml

    print(
        yaml.dump({"screen": screens[0]}, default_flow_style=False, sort_keys=False)[
            :500
        ]
    )
