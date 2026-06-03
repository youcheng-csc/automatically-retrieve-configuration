# Autosubmit Configuration Extractor

A Python tool to automatically extract configuration parameters and component versions from Autosubmit experiment YAML configuration files.

## 🎯 Purpose

This tool automatically retrieves information about end-to-end simulations by parsing Autosubmit YAML configuration files and extracting:
- Experiment parameters (EXPID, HPCARCH, DATA_DIR)
- Model configuration (SIMULATION, GRID_ATM, MODEL.PATH)
- Component versions from various tools and platforms

## ✨ Features

- **Automatic Information Extraction**: Reads YAML configuration files and extracts all relevant parameters
- **Dynamic Platform Detection**: Automatically detects HPC platform (MARENOSTRUM5, LUMI, etc.) and retrieves platform-specific configuration
- **Git Integration**: Fetches data-portfolio version directly from git tags
- **Comprehensive Component Coverage**: Extracts versions for:
  - Model path
  - Data portfolio
  - Workflow
  - Autosubmit
  - AQUA (container and experiment name)
  - GSV interface
  - Post-processing tools (HYDROLAND, WILDFIRES, HYDROMET, ENERGY_INDICATORS, OPA)
- **YAML Output**: Generates clean, structured YAML output files
- **Debug Mode**: Built-in debugging to inspect YAML structure when needed

## 📋 Requirements

- Python 3.6 or higher
- PyYAML library
- Git (for data-portfolio version extraction)

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/youcheng-csc/automatically-retrieve-information-about-end-to-end-simulation-.git
cd automatically-retrieve-information-about-end-to-end-simulation-
