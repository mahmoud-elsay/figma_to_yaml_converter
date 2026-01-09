<<<<<<< HEAD
#!/usr/bin/env python3
"""
Step 1: Download Figma File
Downloads a Figma file and saves it as JSON
"""

import os
import sys
import json
import requests
import re
from pathlib import Path


def print_header():
    print("=" * 60)
    print("📥 STEP 1: Download Figma File")
    print("=" * 60)
    print()


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

    raise ValueError("❌ Invalid Figma URL format")


def get_node_id_from_url(url: str) -> str:
    """Extract node ID from Figma URL (optional)"""
    match = re.search(r"node-id=([^&]+)", url)
    if match:
        return match.group(1).replace("-", ":")
    return None


def download_figma_file(
    token: str, file_key: str, node_id: str = None, output_file: str = None
):
    """Download Figma file via API"""

    # Construct API URL
    url = f"https://api.figma.com/v1/files/{file_key}"

    params = {}
    if node_id:
        params["ids"] = node_id
        print(f"📌 Node ID: {node_id}")

    headers = {"X-Figma-Token": token, "Content-Type": "application/json"}

    print(f"🔗 File Key: {file_key}")
    print(f"📡 Downloading from Figma API...")
    print()

    try:
        # Increased timeout to 300 seconds (5 minutes) for huge files
        response = requests.get(url, headers=headers, params=params, timeout=300, stream=True)

        # Check for errors
        if response.status_code == 401:
            print("❌ Error: Invalid Figma token")
            print("💡 Get your token from: https://www.figma.com/settings")
            sys.exit(1)

        if response.status_code == 403:
            print("❌ Error: Access denied")
            print("💡 Make sure you have access to this file")
            sys.exit(1)

        if response.status_code == 404:
            print("❌ Error: File not found")
            print("💡 Check your Figma URL")
            sys.exit(1)

        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            sys.exit(1)

        # Get content length if available
        content_length = response.headers.get('Content-Length')
        if content_length:
            estimated_mb = int(content_length) / (1024 * 1024)
            print(f"📦 Estimated size: {estimated_mb:.2f} MB")
            if estimated_mb > 10:
                print("⏳ Large file detected, this may take a while...")
        
        # Download with progress for large files
        print("⬇️  Downloading...")
        chunks = []
        downloaded_bytes = 0
        
        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
            if chunk:
                chunks.append(chunk)
                downloaded_bytes += len(chunk)
                if content_length:
                    progress = (downloaded_bytes / int(content_length)) * 100
                    print(f"   Progress: {progress:.1f}% ({downloaded_bytes / (1024*1024):.1f} MB)", end='\r')
        
        if content_length:
            print()  # New line after progress
        
        # Combine chunks and parse JSON
        print("🔄 Parsing JSON...")
        content = b''.join(chunks).decode('utf-8')
        data = json.loads(content)

        # Determine output filename
        if not output_file:
            output_file = f"{file_key}.json"

        # Save to file
        print("💾 Saving to file...")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Calculate file size
        file_size = os.path.getsize(output_file)
        size_mb = file_size / (1024 * 1024)

        print("✅ Download successful!")
        print(f"📁 Saved to: {output_file}")
        print(f"📊 File size: {size_mb:.2f} MB")
        print()
        print("=" * 60)
        print("✨ Next step: Run the converter script")
        print(f"   python 2_convert_to_yaml.py {output_file}")
        print("=" * 60)

    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out (300 seconds)")
        print("💡 The file is extremely large. Consider:")
        print("   1. Downloading a specific node instead of the entire file")
        print("   2. Checking your internet connection")
        print("   3. Breaking the file into smaller parts in Figma")
        sys.exit(1)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Connection failed")
        print("💡 Check your internet connection")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def main():
    print_header()

    # Get Figma token
    token = os.environ.get("FIGMA_TOKEN")

    if not token:
        print("🔑 Enter your Figma Personal Access Token:")
        print("   (Get it from: https://www.figma.com/settings)")
        token = input("   Token: ").strip()
        print()

        if not token:
            print("❌ Error: Token is required")
            sys.exit(1)
    else:
        print("✅ Using FIGMA_TOKEN from environment")
        print()

    # Get Figma URL
    print("🔗 Enter your Figma file URL:")
    print("   Example: https://www.figma.com/design/ABC123...")
    url = input("   URL: ").strip()
    print()

    if not url:
        print("❌ Error: URL is required")
        sys.exit(1)

    # Parse URL
    try:
        file_key = get_file_key_from_url(url)
        node_id = get_node_id_from_url(url)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    # Optional: Custom output filename
    print("💾 Output filename (press Enter for default):")
    output_file = input(f"   [{file_key}.json]: ").strip()
    if not output_file:
        output_file = f"{file_key}.json"
    print()

    print("=" * 60)
    print()

    # Download
    download_figma_file(token, file_key, node_id, output_file)


if __name__ == "__main__":
    main()
=======
#!/usr/bin/env python3
"""
Step 1: Download Figma File
Downloads a Figma file and saves it as JSON
"""

import os
import sys
import json
import requests
import re
from pathlib import Path


def print_header():
    print("=" * 60)
    print("📥 STEP 1: Download Figma File")
    print("=" * 60)
    print()


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

    raise ValueError("❌ Invalid Figma URL format")


def get_node_id_from_url(url: str) -> str:
    """Extract node ID from Figma URL (optional)"""
    match = re.search(r"node-id=([^&]+)", url)
    if match:
        return match.group(1).replace("-", ":")
    return None


def download_figma_file(
    token: str, file_key: str, node_id: str = None, output_file: str = None
):
    """Download Figma file via API"""

    # Construct API URL
    url = f"https://api.figma.com/v1/files/{file_key}"

    params = {}
    if node_id:
        params["ids"] = node_id
        print(f"📌 Node ID: {node_id}")

    headers = {"X-Figma-Token": token, "Content-Type": "application/json"}

    print(f"🔗 File Key: {file_key}")
    print(f"📡 Downloading from Figma API...")
    print()

    try:
        response = requests.get(url, headers=headers, params=params, timeout=60)

        # Check for errors
        if response.status_code == 401:
            print("❌ Error: Invalid Figma token")
            print("💡 Get your token from: https://www.figma.com/settings")
            sys.exit(1)

        if response.status_code == 403:
            print("❌ Error: Access denied")
            print("💡 Make sure you have access to this file")
            sys.exit(1)

        if response.status_code == 404:
            print("❌ Error: File not found")
            print("💡 Check your Figma URL")
            sys.exit(1)

        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            sys.exit(1)

        # Parse JSON
        data = response.json()

        # Determine output filename
        if not output_file:
            output_file = f"{file_key}.json"

        # Save to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Calculate file size
        file_size = os.path.getsize(output_file)
        size_mb = file_size / (1024 * 1024)

        print("✅ Download successful!")
        print(f"📁 Saved to: {output_file}")
        print(f"📊 File size: {size_mb:.2f} MB")
        print()
        print("=" * 60)
        print("✨ Next step: Run the converter script")
        print(f"   python 2_convert_to_yaml.py {output_file}")
        print("=" * 60)

    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out (60 seconds)")
        print("💡 The file might be too large. Try again or check your connection.")
        sys.exit(1)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Connection failed")
        print("💡 Check your internet connection")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def main():
    print_header()

    # Get Figma token
    token = os.environ.get("FIGMA_TOKEN")

    if not token:
        print("🔑 Enter your Figma Personal Access Token:")
        print("   (Get it from: https://www.figma.com/settings)")
        token = input("   Token: ").strip()
        print()

        if not token:
            print("❌ Error: Token is required")
            sys.exit(1)
    else:
        print("✅ Using FIGMA_TOKEN from environment")
        print()

    # Get Figma URL
    print("🔗 Enter your Figma file URL:")
    print("   Example: https://www.figma.com/design/ABC123...")
    url = input("   URL: ").strip()
    print()

    if not url:
        print("❌ Error: URL is required")
        sys.exit(1)

    # Parse URL
    try:
        file_key = get_file_key_from_url(url)
        node_id = get_node_id_from_url(url)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    # Optional: Custom output filename
    print("💾 Output filename (press Enter for default):")
    output_file = input(f"   [{file_key}.json]: ").strip()
    if not output_file:
        output_file = f"{file_key}.json"
    print()

    print("=" * 60)
    print()

    # Download
    download_figma_file(token, file_key, node_id, output_file)


if __name__ == "__main__":
    main()
>>>>>>> 7f8c21ed401cad84e5bd773bf2ed8098230a339e
