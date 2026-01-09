#!/usr/bin/env python3
"""
Figma to YAML Converter - Streamlit Dashboard
Beautiful UI for converting Figma designs to YAML files
"""

import streamlit as st
import os
import json
import requests
import re
import yaml
import tempfile
import zipfile
from pathlib import Path
from io import BytesIO
from typing import Dict, List, Optional, Any

# Import the converter classes
from importlib.util import spec_from_file_location, module_from_spec

# Load the converter module
spec = spec_from_file_location("converter", "2_convert_to_yaml.py")
converter_module = module_from_spec(spec)
spec.loader.exec_module(converter_module)

FigmaNormalizer = converter_module.FigmaNormalizer
SemanticMapper = converter_module.SemanticMapper
YAMLConverter = converter_module.YAMLConverter


def set_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Figma to YAML Converter",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_custom_css():
    """Apply custom CSS for better design"""
    st.markdown(
        """
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #0066FF;
            color: white;
            font-weight: 600;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            border: none;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #0052CC;
            box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
        }
        .success-box {
            background-color: #D4EDDA;
            border-left: 4px solid #28A745;
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }
        .error-box {
            background-color: #F8D7DA;
            border-left: 4px solid #DC3545;
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }
        .info-box {
            background-color: #D1ECF1;
            border-left: 4px solid #17A2B8;
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }
        h1 {
            color: #1F2937;
            font-weight: 700;
        }
        h2, h3 {
            color: #374151;
        }
        .step-header {
            background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_file_key_from_url(url: str) -> str:
    """Extract file key from Figma URL"""
    patterns = [
        r"figma\.com/design/([a-zA-Z0-9]+)",
        r"figma\.com/file/([a-zA-Z0-9]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid Figma URL format")


def download_figma_file(token: str, file_key: str) -> Dict[str, Any]:
    """Download Figma file via API"""
    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {"X-Figma-Token": token, "Content-Type": "application/json"}

    response = requests.get(url, headers=headers, timeout=60)

    if response.status_code == 401:
        raise Exception("Invalid Figma token. Get your token from: https://www.figma.com/settings")
    elif response.status_code == 403:
        raise Exception("Access denied. Make sure you have access to this file")
    elif response.status_code == 404:
        raise Exception("File not found. Check your Figma URL")
    elif response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")

    return response.json()


def convert_to_yaml(figma_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert Figma JSON to YAML files"""
    normalizer = FigmaNormalizer()
    normalized_nodes = normalizer.normalize(figma_data)

    if not normalized_nodes:
        raise Exception("No nodes found to convert")

    mapper = SemanticMapper()
    screens = mapper.map_to_screens(normalized_nodes)

    if not screens:
        raise Exception("No screens found to convert")

    return screens


def create_yaml_files(screens: List[Dict[str, Any]]) -> Dict[str, str]:
    """Convert screens to YAML files and return as dict"""
    yaml_files = {}
    filename_counts = {}

    for screen in screens:
        output = {
            "screen": {"name": screen["name"], "children": screen.get("children", [])}
        }
        yaml_content = yaml.dump(
            output, default_flow_style=False, sort_keys=False, allow_unicode=True
        )

        base_filename = re.sub(r"[^\w\s-]", "", screen["name"].lower())
        base_filename = re.sub(r"[\s_]+", "_", base_filename).strip("_")

        if base_filename in filename_counts:
            filename_counts[base_filename] += 1
            filename = f"{base_filename}_{filename_counts[base_filename]}.yaml"
        else:
            filename_counts[base_filename] = 1
            filename = f"{base_filename}.yaml"

        yaml_files[filename] = yaml_content

    return yaml_files


def create_zip_file(yaml_files: Dict[str, str]) -> BytesIO:
    """Create a zip file containing all YAML files"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in yaml_files.items():
            zip_file.writestr(f"generated/{filename}", content)
    zip_buffer.seek(0)
    return zip_buffer


def main():
    set_page_config()
    apply_custom_css()

    # Header
    st.markdown(
        """
        <div style='text-align: center; padding: 2rem 0;'>
            <h1>🎨 Figma to YAML Converter</h1>
            <p style='font-size: 1.2rem; color: #6B7280;'>
                Transform your Figma designs into structured YAML files
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.markdown("### 📖 Instructions")
        st.markdown(
            """
            1. Get your Figma Personal Access Token from [Figma Settings](https://www.figma.com/settings)
            2. Copy your Figma file URL
            3. Paste both in the form
            4. Click **Convert** and download your YAML files!
            """
        )
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown(
            """
            This tool converts Figma designs into clean, structured YAML files
            that can be used for code generation and documentation.
            """
        )

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="step-header"><h3>🔑 Step 1: Enter Your Credentials</h3></div>', unsafe_allow_html=True)

        token = st.text_input(
            "Figma Personal Access Token",
            type="password",
            placeholder="figd_xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            help="Get your token from https://www.figma.com/settings",
        )

        figma_url = st.text_input(
            "Figma File URL",
            placeholder="https://www.figma.com/design/ABC123.../...",
            help="Paste the URL of your Figma design file",
        )

        st.markdown("---")

        convert_button = st.button("🚀 Convert to YAML", type="primary", use_container_width=True)

    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**💡 Quick Tips**")
        st.markdown("- Token starts with `figd_`")
        st.markdown("- URL should contain `/design/` or `/file/`")
        st.markdown("- Process takes 5-30 seconds")
        st.markdown("</div>", unsafe_allow_html=True)

    # Processing
    if convert_button:
        if not token or not figma_url:
            st.error("❌ Please provide both Figma token and URL")
        else:
            try:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Extract file key
                status_text.text("🔍 Extracting file information...")
                progress_bar.progress(20)
                file_key = get_file_key_from_url(figma_url)

                # Step 2: Download from Figma
                status_text.text("📥 Downloading from Figma API...")
                progress_bar.progress(40)
                figma_data = download_figma_file(token, file_key)

                # Step 3: Convert to YAML
                status_text.text("🔄 Converting to YAML format...")
                progress_bar.progress(60)
                screens = convert_to_yaml(figma_data)

                # Step 4: Generate YAML files
                status_text.text("📝 Generating YAML files...")
                progress_bar.progress(80)
                yaml_files = create_yaml_files(screens)

                # Step 5: Create ZIP
                status_text.text("📦 Creating download package...")
                progress_bar.progress(90)
                zip_buffer = create_zip_file(yaml_files)

                progress_bar.progress(100)
                status_text.text("✅ Conversion complete!")

                # Success message
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown(f"### ✅ Success!")
                st.markdown(f"**Generated {len(yaml_files)} YAML file(s)**")
                st.markdown("</div>", unsafe_allow_html=True)

                # Display files
                st.markdown("### 📄 Generated Files")
                for filename in yaml_files.keys():
                    st.markdown(f"- `{filename}`")

                # Download button
                st.markdown("---")
                st.download_button(
                    label="⬇️ Download ZIP File",
                    data=zip_buffer,
                    file_name=f"figma_yaml_{file_key}.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                )

                # Preview
                st.markdown("### 👀 Preview")
                preview_file = st.selectbox("Select a file to preview:", list(yaml_files.keys()))
                if preview_file:
                    st.code(yaml_files[preview_file], language="yaml")

            except ValueError as e:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.markdown(f"**❌ Invalid URL**")
                st.markdown(str(e))
                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.markdown(f"**❌ Error**")
                st.markdown(str(e))
                st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #9CA3AF; padding: 2rem 0;'>
            <p>Made with ❤️ using Streamlit | Figma to YAML Converter</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
