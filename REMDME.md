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
The script generates a YAML file (The output file is named: {experiment_id}_experiment_data_versions.yaml) with the following structure:

yaml
experiment_info:
  expid: o01v
  hpcarch: MARENOSTRUM5
  data_dir: /path/to/experiment/data
  simulation: ifs-fesom-storylines-historical-tco1279
  grid_atm: tco1279l137
  aqua_experiment_name: my_experiment

component_versions:
  model_path: /full/path/to/model/DE_CY48R1.0_climateDT_20250521bis
  data_portfolio_version: 2.1.0
  workflow_version: 1.2.3
  autosubmit_version: 4.5.6
  aqua_container_version: 2.1.0
  gsv_interface_version: 1.0.0
  hydroland_version: 1.0
  wildfires_fwi_version: 2.0
  wildfires_wise_version: 1.5
  hydromet_version: 3.2
  energy_indicators_version: 1.1
  energy_offshore_version: 2.0
  opa_version: 4.3

resources:
  nodes: 48
  
