# Autosubmit Configuration Extractor

A Python tool to automatically extract configuration parameters and component versions from Autosubmit experiment YAML configuration files.

## 📋 Requirements

- Python 3.6 or higher
- PyYAML library
- Git (for data-portfolio version extraction)

## 🔧 Installation

### 1. Clone the repository


git clone https://github.com/youcheng-csc/automatically-retrieve-information-about-end-to-end-simulation-.git
cd automatically-retrieve-information-about-end-to-end-simulation-

# Basic Usage

python3 extract_versions.py /path/to/experiment_data.yml

Example

python3 extract_versions.py /appl/AS/AUTOSUBMIT_DATA/o021/conf/metadata/experiment_data.yml

## Output
The output file is named: {experiment_id}_experiment_data_versions.yaml.
  
