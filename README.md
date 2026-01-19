# 🎨 Figma to YAML Converter

> Transform your Figma designs into clean, structured YAML files with full support for icons, images, and layouts.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ Features

- 📝 **Text Elements** - Preserves text content with complete style metadata
- 🎯 **Layout Detection** - Automatically identifies rows, columns, and frames
- 🎭 **Icon Support** - Detects icons using name patterns and size heuristics
- 🖼️ **Image Handling** - Extracts images from fills with proper dimensions
- 🏗️ **Semantic Structure** - Maintains your design hierarchy in clean YAML

---

## 🚀 Quick Start

### Prerequisites

Ensure you have Python 3.8 or higher installed on your system.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/figma_to_yaml.git
   cd figma_to_yaml
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📖 Usage Guide

### 🎥 Video Tutorial

**Watch the complete walkthrough on YouTube:**

[![Figma to YAML Converter Tutorial](https://img.shields.io/badge/YouTube-Watch%20Tutorial-red?style=for-the-badge&logo=youtube)](YOUR_YOUTUBE_VIDEO_LINK)

Learn how to use the converter step-by-step with practical examples and tips!

---

### Basic Workflow

#### Step 1️⃣: Download Figma File (Optional)

If you already have a Figma JSON export, skip to Step 2.

```bash
python 1_download_figma.py <figma_file_id> <output.json>
```

**Example:**
```bash
python 1_download_figma.py abc123xyz my_design.json
```

#### Step 2️⃣: Convert to YAML

```bash
python 2_convert_to_yaml.py <figma_file.json> <output_dir>
```

**Example using the included sample:**
```bash
python 2_convert_to_yaml.py ucrbA01Va5RCZ2x6HgTjvB.json generated
```

#### Step 3️⃣: Review Your Output

Check the `generated/` directory for your YAML files:
```
generated/
├── home.yaml
├── profile.yaml
└── settings.yaml
```

---

## 🎯 What Gets Converted

| Element Type | YAML Output | Details |
|-------------|-------------|---------|
| **Text** | `type: text` | Includes value and style metadata |
| **Containers** | `row`, `column`, `frame` | Layout hierarchy preserved |
| **Icons** | `type: icon` | Name, width, height, and ID |
| **Images** | `type: image` | Path, dimensions, and ID |

### Example Output

```yaml
type: frame
name: Header
children:
  - type: row
    children:
      - type: icon
        name: menu
        width: 24
        height: 24
      - type: text
        value: Welcome Back
        fontSize: 24
        fontWeight: bold
      - type: image
        path: avatar.png
        width: 40
        height: 40
```

---

## 🌐 Streamlit Web Interface

Launch the interactive web app for a visual conversion experience:

```bash
streamlit run streamlit_app.py
```

This provides a user-friendly interface where you can:
- 📤 Upload Figma JSON files directly
- 👀 Preview the conversion in real-time
- 💾 Download generated YAML files
- 🎨 Visualize your design structure

---

## 🛠️ Troubleshooting

### Missing Icons or Images?

- ✅ Verify your input JSON contains proper frames or fills for these elements
- ✅ Check element naming conventions (icons often need specific name patterns)
- ✅ Review the conversion logic in `2_convert_to_yaml.py`

### Conversion Errors?

- ✅ Ensure your Figma JSON file is properly formatted
- ✅ Check that all dependencies are installed: `pip install -r requirements.txt`
- ✅ Try the `patch_converter.py` script for fixing common issues

---

## 🔧 Advanced Tools

### Patch Converter

Use `patch_converter.py` to fix or enhance existing conversions:

```bash
python patch_converter.py <input_yaml> <output_yaml>
```

This utility can help with:
- Fixing malformed YAML structures
- Enhancing element detection
- Applying custom transformations

To customize conversion behavior, edit the core logic in `2_convert_to_yaml.py`.

---

## 📂 Project Structure

```
figma_to_yaml_converter/
├── 1_download_figma.py       # Figma file downloader
├── 2_convert_to_yaml.py      # Main converter script
├── patch_converter.py        # YAML patching utility
├── streamlit_app.py          # Web interface
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. 🍴 Fork the repository
2. 🌱 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🎉 Open a Pull Request

### Ideas for Contributions

- 🎨 Improve icon/image detection algorithms
- 📏 Add support for more Figma element types
- 🧹 Enhance YAML output formatting
- 📚 Expand documentation and examples
- 🐛 Report bugs or suggest features via Issues

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built for designers and developers working with Figma
- Inspired by the need for structured design-to-code workflows
- Community feedback and contributions welcome!

---

## 📞 Support

- 🐛 **Found a bug?** [Open an issue](https://github.com/yourusername/figma_to_yaml/issues)
- 💡 **Have a feature request?** [Start a discussion](https://github.com/yourusername/figma_to_yaml/discussions)
- 📧 **Need help?** Reach out via [elsayedmahmoud763@gmail.com](mailto:elsayedmahmoud763@gmail.com)
- 🎥 **Learn more:** Check out the [YouTube tutorial](YOUR_YOUTUBE_VIDEO_LINK)

---

<div align="center">

Made with ❤️ by the community

**[⭐ Star this repo](https://github.com/yourusername/figma_to_yaml)** if you find it useful!

</div>
