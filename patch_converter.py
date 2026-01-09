#!/usr/bin/env python3
"""
Patch script to update 2_convert_to_yaml.py for better handling of large files
"""

import sys
import os

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Read the original file
print("Reading 2_convert_to_yaml.py...")
with open('2_convert_to_yaml.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the convert_figma_json function's JSON loading section
old_code = '''    # Load JSON
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
    print()'''

new_code = '''    # Load JSON
    print(f"📂 Loading: {json_file}")
    
    # Check file size before loading
    try:
        file_size = os.path.getsize(json_file)
        size_mb = file_size / (1024 * 1024)
        print(f"   📊 File size: {size_mb:.2f} MB")
        
        if size_mb > 50:
            print(f"   ⚠️  Large file detected ({size_mb:.2f} MB)")
            print("   ⏳ This may take several minutes and use significant memory...")
        
        if size_mb > 200:
            print("   ⚠️  WARNING: Very large file!")
            print("   💡 Consider using a specific node-id instead of downloading the entire file")
            print("   💡 You can add '?node-id=X:Y' to your Figma URL")
            response = input("   Continue anyway? (y/n): ").strip().lower()
            if response != 'y':
                print("   ❌ Cancelled by user")
                sys.exit(0)
    except OSError:
        pass  # File not found, will be caught below
    
    try:
        print("   🔄 Loading JSON into memory...")
        with open(json_file, "r", encoding="utf-8") as f:
            figma_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON: {str(e)}")
        sys.exit(1)
    except MemoryError:
        print(f"❌ Error: Out of memory")
        print("💡 The file is too large to process. Try:")
        print("   1. Downloading only a specific node (use node-id in URL)")
        print("   2. Breaking the design into smaller files in Figma")
        print("   3. Running on a machine with more RAM")
        sys.exit(1)

    print("   ✅ JSON loaded successfully")
    print()'''

# Replace
if old_code in content:
    content = content.replace(old_code, new_code)
    print("✅ Successfully updated the code")
    
    # Write back
    with open('2_convert_to_yaml.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ File 2_convert_to_yaml.py updated successfully!")
else:
    print("❌ Could not find the target code to replace")
    print("This might be because:")
    print("  - The file was already updated")
    print("  - The file has been modified")
    print("  - Line ending differences")
