#!/usr/bin/env python3
"""
Step 2: Convert Figma JSON to YAML
Converts downloaded Figma JSON file into clean YAML structure
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


def print_header():
    print("=" * 60)
    print("STEP 2: Convert Figma JSON to YAML")
    print("=" * 60)
    print()


class FigmaNormalizer:
    """Normalizes and filters Figma JSON to essential UI properties"""

    def __init__(self, figma_file_key: str = None):
        """Initialize with optional Figma file key for asset URLs"""
        self.figma_file_key = figma_file_key

    def normalize(self, figma_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize Figma data structure"""

        print("🔍 Analyzing JSON structure...")

        # Handle node-id specific requests
        if "nodes" in figma_data:
            print("   📌 Found specific node request")
            result = []
            for node_id, node_data in figma_data["nodes"].items():
                if "document" in node_data:
                    document = node_data["document"]
                    normalized = self._normalize_node(document)
                    if normalized:
                        result.append(normalized)
            return result

        # Handle full document requests
        if "document" in figma_data:
            print("   📄 Found full document")
            document = figma_data["document"]
            return self._normalize_children(document)

        print("   ⚠️  Unexpected JSON structure")
        return []

    def _normalize_children(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize all children of a node"""
        if "children" not in node:
            return []

        result = []
        for child in node["children"]:
            # Skip CANVAS nodes, but process their children
            if child.get("type") == "CANVAS":
                # Recursively get children from canvas
                canvas_children = self._normalize_children(child)
                result.extend(canvas_children)
            else:
                normalized = self._normalize_node(child)
                if normalized:
                    result.append(normalized)

        return result

    def _generate_asset_url(
        self, node_id: str, name: str, asset_type: str = "image"
    ) -> str:
        """
        Generate Flutter-friendly asset URL for icons and images.

        Args:
            node_id: Figma node ID
            name: Asset name
            asset_type: "image" or "icon"

        Returns:
            Asset URL path suitable for Flutter
        """
        # Sanitize name for URL
        safe_name = self._sanitize_name(name)

        # Some Figma default layer names are generic (e.g. "Vector", "Rectangle").
        # To avoid collisions when many layers share the same generic name,
        # append a sanitized node id suffix for uniqueness.
        generic_names = {
            "vector",
            "rectangle",
            "ellipse",
            "shape",
            "image",
            "unnamed",
            "layer",
        }
        if not safe_name or safe_name in generic_names:
            id_suffix = re.sub(r"[^0-9A-Za-z]+", "_", str(node_id))
            safe_name = f"{safe_name or 'asset'}_{id_suffix}"

        # Return Flutter asset path format
        if asset_type == "icon":
            return f"assets/icons/{safe_name}.svg"
        else:  # image
            return f"assets/images/{safe_name}.png"

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Sanitize asset name for file paths"""
        # Convert to lowercase, replace spaces and special chars with underscores
        name = name.lower()
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"[\s_]+", "_", name)
        name = name.strip("_")
        return name

    def _normalize_node(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize a single node"""
        node_type = node.get("type")
        node_id = node.get("id")
        name = node.get("name", "Unnamed")

        # Get bounding box
        bounds = node.get("absoluteBoundingBox", {})
        x = bounds.get("x")
        y = bounds.get("y")
        width = bounds.get("width")
        height = bounds.get("height")
        # Common visual properties
        opacity = node.get("opacity")
        strokes = node.get("strokes")
        stroke_weight = node.get("strokeWeight")
        effects = node.get("effects")
        visible = node.get("visible", True)

        # Detect icons and images by name patterns and visual characteristics
        name_lower = name.lower()
        is_icon = any(
            keyword in name_lower
            for keyword in [
                "icon",
                "logo",
                "arrow",
                "check",
                "close",
                "menu",
                "search",
                "heart",
                "star",
                "home",
                "profile",
                "settings",
                "notification",
                "back",
                "forward",
                "play",
                "pause",
                "stop",
                "edit",
                "delete",
                "add",
                "plus",
                "minus",
                "refresh",
                "share",
                "download",
                "upload",
                "li:",
                "ic_",
                "ico_",
                "btn_",
                "img_icon",
                "icon_",
            ]
        )

        is_image = any(
            keyword in name_lower
            for keyword in [
                "image",
                "photo",
                "picture",
                "img",
                "illustration",
                "graphic",
                "avatar",
                "thumbnail",
                "banner",
                "hero",
                "bg_",
                "background",
            ]
        )

        # Also detect icons/images by small size (likely icons) or by having image fills
        has_image_fill = False
        fills = node.get("fills", [])
        if fills and isinstance(fills, list):
            for fill in fills:
                if fill.get("type") == "IMAGE":
                    has_image_fill = True
                    break

        # Small elements are likely icons
        if not is_icon and width and height:
            if (
                width <= 64
                and height <= 64
                and (node_type in ["VECTOR", "ELLIPSE", "FRAME"])
            ):
                is_icon = True

        # Handle different node types
        if node_type in ["FRAME", "COMPONENT", "INSTANCE", "GROUP"]:
            # If it's an icon-like frame with no text children, mark as icon
            if (is_icon or has_image_fill) and not self._has_text_children(node):
                if has_image_fill:
                    return {
                        "id": node_id,
                        "name": name,
                        "type": "IMAGE",
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height,
                        "imageRef": name,
                        "imageId": node_id,
                        "url": self._generate_asset_url(node_id, name, "image"),
                        "children": [],
                    }
                else:
                    return {
                        "id": node_id,
                        "name": name,
                        "type": "ICON",
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height,
                        "iconName": name,
                        "iconId": node_id,
                        "url": self._generate_asset_url(node_id, name, "icon"),
                        "children": [],
                    }

            # If it's an image-like frame, mark as image
            if is_image and not self._has_text_children(node):
                return {
                    "id": node_id,
                    "name": name,
                    "type": "IMAGE",
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "imageRef": name,
                    "imageId": node_id,
                    "url": self._generate_asset_url(node_id, name, "image"),
                    "children": [],
                }

            return {
                "id": node_id,
                "name": name,
                "type": node_type,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "opacity": opacity,
                "strokes": strokes,
                "strokeWeight": stroke_weight,
                "effects": effects,
                "visible": visible,
                "layoutMode": node.get("layoutMode"),
                "paddingLeft": node.get("paddingLeft"),
                "paddingRight": node.get("paddingRight"),
                "paddingTop": node.get("paddingTop"),
                "paddingBottom": node.get("paddingBottom"),
                "itemSpacing": node.get("itemSpacing"),
                "primaryAxisAlignItems": node.get("primaryAxisAlignItems"),
                "counterAxisAlignItems": node.get("counterAxisAlignItems"),
                "backgroundColor": self._extract_color(node.get("backgroundColor")),
                "cornerRadius": node.get("cornerRadius"),
                "children": self._normalize_children(node),
            }

        elif node_type == "TEXT":
            return {
                "id": node_id,
                "name": name,
                "type": node_type,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "characters": node.get("characters", ""),
                "fontSize": self._extract_font_size(node.get("style")),
                "fontWeight": node.get("style", {}).get("fontWeight"),
                "fontFamily": node.get("style", {}).get("fontFamily"),
                "textAlignHorizontal": node.get("style", {}).get("textAlignHorizontal"),
                "color": self._extract_fill_color(node.get("fills")),
                "lineHeight": self._extract_line_height(node.get("style")),
                "letterSpacing": node.get("style", {}).get("letterSpacing"),
                "style": node.get("style"),
                "opacity": opacity,
                "visible": visible,
            }

        elif node_type == "RECTANGLE":
            return {
                "id": node_id,
                "name": name,
                "type": node_type,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "fillColor": self._extract_fill_color(node.get("fills")),
                "cornerRadius": node.get("cornerRadius"),
                "opacity": opacity,
                "strokes": strokes,
                "strokeWeight": stroke_weight,
                "effects": effects,
                "visible": visible,
            }

        elif node_type in [
            "VECTOR",
            "ELLIPSE",
            "LINE",
            "POLYGON",
            "STAR",
            "BOOLEAN_OPERATION",
        ]:
            # Check if it's an image fill
            fills = node.get("fills", [])
            if fills and isinstance(fills, list) and len(fills) > 0:
                first_fill = fills[0]
                if first_fill.get("type") == "IMAGE":
                    return {
                        "id": node_id,
                        "name": name,
                        "type": "IMAGE",
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height,
                        "imageRef": first_fill.get("imageRef") or name,
                        "imageId": node_id,
                        "url": self._generate_asset_url(node_id, name, "image"),
                    }

            # Otherwise treat as icon
            if is_icon or node_type in ["VECTOR", "ELLIPSE"]:
                return {
                    "id": node_id,
                    "name": name,
                    "type": "ICON",
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "iconName": name,
                    "iconId": node_id,
                    "url": self._generate_asset_url(node_id, name, "icon"),
                    "children": [],
                }

        return None

    def _has_text_children(self, node: Dict[str, Any]) -> bool:
        """Check if node has any text children"""
        children = node.get("children", [])
        for child in children:
            if child.get("type") == "TEXT":
                return True
            if child.get("children"):
                if self._has_text_children(child):
                    return True
        return False

    @staticmethod
    def _extract_color(color_data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract color as hex string"""
        if not color_data:
            return None

        r = int(color_data.get("r", 0) * 255)
        g = int(color_data.get("g", 0) * 255)
        b = int(color_data.get("b", 0) * 255)

        return f"#{r:02X}{g:02X}{b:02X}"

    @staticmethod
    def _extract_fill_color(fills: Optional[List[Dict[str, Any]]]) -> Optional[str]:
        """Extract fill color from fills array"""
        if not fills or not isinstance(fills, list) or len(fills) == 0:
            return None

        first_fill = fills[0]
        if first_fill.get("type") == "SOLID":
            return FigmaNormalizer._extract_color(first_fill.get("color"))

        return None

    @staticmethod
    def _extract_font_size(style: Optional[Dict[str, Any]]) -> Optional[float]:
        """Extract font size from style"""
        if not style:
            return None
        return style.get("fontSize")

    @staticmethod
    def _extract_line_height(style: Optional[Dict[str, Any]]) -> Optional[float]:
        """Extract line height from style"""
        if not style:
            return None
        return style.get("lineHeightPx")


class SemanticMapper:
    """Maps normalized nodes to semantic UI concepts"""

    def map_to_screens(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert normalized nodes to screen structures"""
        print("🎨 Mapping UI elements...")

        screens = []

        for node in nodes:
            # If the node is a Frame/Component with children, treat it as a screen
            if node.get("type") in ["FRAME", "COMPONENT", "INSTANCE"] and node.get(
                "children"
            ):
                screens.append(
                    {
                        "name": node["name"],
                        "children": self._map_children(node["children"]),
                    }
                )
            # If it has children that are frames, treat each as a screen
            elif node.get("children"):
                for child in node["children"]:
                    if child.get("type") in ["FRAME", "COMPONENT", "INSTANCE"]:
                        screens.append(
                            {
                                "name": child["name"],
                                "children": self._map_children(
                                    child.get("children", [])
                                ),
                            }
                        )

        return screens

    def _map_children(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map children nodes to UI elements"""
        return [self._map_node(node) for node in nodes if self._map_node(node)]

    def _map_node(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Map a single node to a UI element"""
        node_type = node.get("type")

        if node_type == "TEXT":
            # Skip empty text
            text_value = node.get("characters", "").strip()
            if not text_value:
                return None

            element = {"type": "text", "value": text_value}
            if node.get("id"):
                element["id"] = node["id"]
            if node.get("x") is not None:
                element["x"] = node["x"]
            if node.get("y") is not None:
                element["y"] = node["y"]
            if node.get("fontSize"):
                element["size"] = node["fontSize"]
            if node.get("fontWeight"):
                element["fontWeight"] = node["fontWeight"]
            if node.get("fontFamily"):
                element["fontFamily"] = node["fontFamily"]
            if node.get("color"):
                element["color"] = node["color"]
            if node.get("textAlignHorizontal"):
                element["align"] = node["textAlignHorizontal"].lower()
            return element

        elif node_type == "ICON":
            element = {
                "type": "icon",
                "name": node.get("iconName", node.get("name", "icon")),
            }
            if node.get("id"):
                element["id"] = node["id"]
            if node.get("url"):
                element["url"] = node.get("url")
            if node.get("width"):
                element["width"] = node["width"]
            if node.get("height"):
                element["height"] = node["height"]
            return element

        elif node_type == "IMAGE":
            element = {
                "type": "image",
                "name": node.get("imageRef", node.get("name", "image")),
            }
            if node.get("id"):
                element["id"] = node["id"]
            if node.get("url"):
                element["url"] = node.get("url")
            else:
                # Fallback to old path format if no URL
                element["path"] = (
                    f"assets/images/{node.get('imageRef', node.get('name', 'image'))}.png"
                )
            if node.get("width"):
                element["width"] = node["width"]
            if node.get("height"):
                element["height"] = node["height"]
            # include basic position when available
            if node.get("x") is not None:
                element["x"] = node["x"]
            if node.get("y") is not None:
                element["y"] = node["y"]
            return element

        elif node_type == "RECTANGLE":
            element = {"type": "container"}
            if node.get("width"):
                element["width"] = node["width"]
            if node.get("height"):
                element["height"] = node["height"]
            if node.get("fillColor"):
                element["background"] = node["fillColor"]
            if node.get("cornerRadius"):
                element["radius"] = node["cornerRadius"]
            if node.get("id"):
                element["id"] = node["id"]
            if node.get("x") is not None:
                element["x"] = node["x"]
            if node.get("y") is not None:
                element["y"] = node["y"]
            return element

        elif node_type in ["FRAME", "COMPONENT", "INSTANCE", "GROUP"]:
            # Handle icon/image frames without children
            children = self._map_children(node.get("children", []))

            # Simple button heuristic: a frame with background + corner radius and a single prominent text child
            text_children = [
                c
                for c in node.get("children", [])
                if c.get("type") == "TEXT" and c.get("characters", "").strip()
            ]
            if (
                node.get("backgroundColor")
                and node.get("cornerRadius")
                and text_children
                and len(node.get("children", [])) <= 4
            ):
                # Use the first text child as label
                label_node = text_children[0]
                label = label_node.get("characters") or label_node.get("name") or ""
                element = {
                    "type": "button",
                    "label": label.strip(),
                }
                if node.get("id"):
                    element["id"] = node["id"]
                if node.get("x") is not None:
                    element["x"] = node["x"]
                if node.get("y") is not None:
                    element["y"] = node["y"]
                if node.get("backgroundColor"):
                    element["background"] = node.get("backgroundColor")
                if node.get("cornerRadius"):
                    element["radius"] = node.get("cornerRadius")
                if node.get("width"):
                    element["width"] = node.get("width")
                if node.get("height"):
                    element["height"] = node.get("height")
                return element

            # If it's empty and looks like an icon/image, return it as such
            if not children:
                return None

            direction = self._infer_direction(node)
            element = {"type": direction}

            if node.get("id"):
                element["id"] = node["id"]
            if node.get("x") is not None:
                element["x"] = node["x"]
            if node.get("y") is not None:
                element["y"] = node["y"]

            padding = self._infer_padding(node)
            if padding:
                element["padding"] = padding

            if node.get("itemSpacing"):
                element["spacing"] = node["itemSpacing"]

            alignment = self._infer_alignment(node)
            if alignment:
                element["alignment"] = alignment

            if node.get("backgroundColor"):
                element["background"] = node["backgroundColor"]

            if node.get("cornerRadius"):
                element["radius"] = node["cornerRadius"]

            if node.get("width"):
                element["width"] = node["width"]

            if node.get("height"):
                element["height"] = node["height"]

            if children:
                element["children"] = children

            return element

        return None

    @staticmethod
    def _infer_direction(node: Dict[str, Any]) -> str:
        """Infer layout direction from node"""
        layout_mode = node.get("layoutMode")
        if layout_mode == "VERTICAL":
            return "column"
        elif layout_mode == "HORIZONTAL":
            return "row"
        return "stack"

    @staticmethod
    def _infer_padding(node: Dict[str, Any]) -> Optional[float]:
        """Infer average padding from node"""
        paddings = [
            node.get("paddingLeft"),
            node.get("paddingRight"),
            node.get("paddingTop"),
            node.get("paddingBottom"),
        ]
        paddings = [p for p in paddings if p is not None]

        if paddings:
            return sum(paddings) / len(paddings)
        return None

    @staticmethod
    def _infer_alignment(node: Dict[str, Any]) -> Optional[str]:
        """Infer alignment from node"""
        align = node.get("primaryAxisAlignItems")
        if align == "CENTER":
            return "center"
        elif align == "MIN":
            return "start"
        elif align == "MAX":
            return "end"
        return None


class YAMLConverter:
    """Converts UI screens to clean YAML format"""

    def convert_all(
        self, screens: List[Dict[str, Any]], output_dir: str = "generated"
    ) -> int:
        """Convert all screens to YAML files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        print(f"📝 Converting to YAML...")
        print(f"   Output directory: {output_dir}")
        print()

        written = 0
        for screen in screens:
            yaml_content = self._convert_screen(screen)
            filename = self._sanitize_filename(screen["name"]) + ".yaml"
            filepath = output_path / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(yaml_content)

            print(f"   ✅ {filename}")
            written += 1

        return written

    def _convert_screen(self, screen: Dict[str, Any]) -> str:
        """Convert a screen to YAML string"""
        output = {
            "screen": {"name": screen["name"], "children": screen.get("children", [])}
        }

        return yaml.dump(
            output, default_flow_style=False, sort_keys=False, allow_unicode=True
        )

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize filename"""
        name = name.lower()
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"[\s_]+", "_", name)
        name = name.strip("_")
        return name


def convert_figma_json(json_file: str, output_dir: str = "generated"):
    """Main conversion function"""

    # Load JSON
    print(f"📂 Loading: {json_file}")
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            figma_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON: {str(e)}")
        sys.exit(1)

    print("   ✅ JSON loaded successfully")
    print()

    # Normalize
    print("🔄 Processing Figma data...")
    normalizer = FigmaNormalizer()
    normalized_nodes = normalizer.normalize(figma_data)

    print(f"   ✅ Found {len(normalized_nodes)} root node(s)")

    if not normalized_nodes:
        print()
        print("⚠️  No nodes found to convert")
        print("💡 The JSON might be empty or have an unexpected structure")
        sys.exit(1)

    # Show what was found
    print()
    for node in normalized_nodes:
        children_count = len(node.get("children", []))
        print(f"   📄 \"{node['name']}\" ({node['type']}, {children_count} children)")
    print()

    # Map to screens
    mapper = SemanticMapper()
    screens = mapper.map_to_screens(normalized_nodes)

    print(f"   ✅ Identified {len(screens)} screen(s)")

    if not screens:
        print()
        print("⚠️  No screens found to convert")
        print("💡 The nodes might not contain UI elements")
        sys.exit(1)

    print()

    # Convert to YAML
    converter = YAMLConverter()
    written = converter.convert_all(screens, output_dir)

    print()
    print("=" * 60)
    print(f"✅ Success! Generated {written} YAML file(s)")
    print(f"📁 Location: {Path(output_dir).absolute()}")
    print("=" * 60)


def main():
    print_header()

    # Get JSON filename
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        print("📂 Enter the path to your Figma JSON file:")
        print("   Example: figma_file.json")
        json_file = input("   File: ").strip()
        print()

    if not json_file:
        print("❌ Error: JSON file is required")
        print()
        print("Usage: python 2_convert_to_yaml.py <json_file>")
        sys.exit(1)

    # Optional: Custom output directory
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = "generated"

    print("=" * 60)
    print()

    # Convert
    convert_figma_json(json_file, output_dir)


if __name__ == "__main__":
    main()
