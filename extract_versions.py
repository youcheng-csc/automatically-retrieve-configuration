#!/usr/bin/env python3
"""
Script to extract component versions and configuration parameters from Autosubmit YAML configuration.
Extracts model version, EXPID, HPCARCH, SIMULATION, GRID_ATM, AQUA EXPERIMENT_NAME, and DATA_DIR.

Usage: python3 extract_versions.py /path/to/experiment_data.yml
"""

import yaml
import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List


def get_data_portfolio_version(expid: str, base_path: str = "/appl/AS/AUTOSUBMIT_DATA") -> Optional[str]:
    """
    Get the data-portfolio version by running git describe in the data-portfolio directory.
    
    Args:
        expid: The experiment ID (e.g., 'o01v')
        base_path: Base path for Autosubmit data
    
    Returns:
        Version string or None if not found
    """
    # Construct the path to data-portfolio
    data_portfolio_path = Path(base_path) / expid / "proj" / "git_project" / "data-portfolio"
    
    if not data_portfolio_path.exists():
        print(f"\n⚠️ Warning: data-portfolio directory not found at {data_portfolio_path}")
        return None
    
    try:
        # Run git describe --exact-match --tags in the data-portfolio directory
        result = subprocess.run(
            ['git', 'describe', '--exact-match', '--tags'],
            cwd=data_portfolio_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            version = result.stdout.strip()
            # Remove 'v' prefix if present
            if version.startswith('v'):
                version = version[1:]
            return version
        else:
            print(f"\n⚠️ Warning: No git tag found in {data_portfolio_path}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"\n⚠️ Warning: Git command timed out for {data_portfolio_path}")
        return None
    except Exception as e:
        print(f"\n⚠️ Warning: Error getting data-portfolio version: {e}")
        return None


def parse_yaml_config(file_path: str, expid: str) -> Dict[str, Any]:
    """Parse YAML configuration file and extract available component versions and parameters."""

    print(f"\n📖 Reading configuration from: {file_path}")

    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)

    results = {}

    # Extract DEFAULT section parameters
    if 'DEFAULT' in config:
        default = config['DEFAULT']
        if 'EXPID' in default:
            results['expid'] = default['EXPID']
        if 'HPCARCH' in default:
            results['hpcarch'] = default['HPCARCH']
        if 'HPCROOTDIR' in default:
            # HPCROOTDIR: Main working directory on HPC where rundir, restarts, and AQUA APP output are located
            results['hpcrootdir'] = default['HPCROOTDIR']
        if 'STARTDATES' in default:
            # Extract STARTDATES as a list of dates without quotes in display
            startdates = default['STARTDATES']
            if isinstance(startdates, list):
                results['startdates'] = [str(date).strip("'") for date in startdates]
            else:
                results['startdates'] = [str(startdates).strip("'")]
        elif 'STARTDATE' in default:
            results['startdates'] = [str(default['STARTDATE']).strip("'")]
        elif 'START_DATE' in default:
            results['startdates'] = [str(default['START_DATE']).strip("'")]

    # Also check top-level keys for HPCROOTDIR and STARTDATES
    if 'HPCROOTDIR' in config:
        # HPCROOTDIR: Main working directory on HPC where rundir, restarts, and AQUA APP output are located
        results['hpcrootdir'] = config['HPCROOTDIR']
    
    if 'STARTDATES' in config:
        # Extract STARTDATES as a list of dates without quotes in display
        startdates = config['STARTDATES']
        if isinstance(startdates, list):
            results['startdates'] = [str(date).strip("'") for date in startdates]
        else:
            results['startdates'] = [str(startdates).strip("'")]
    elif 'STARTDATE' in config:
        results['startdates'] = [str(config['STARTDATE']).strip("'")]

    # Extract Model inputs (replaces data_dir)
    if 'MODEL' in config:
        model = config['MODEL']
        if 'SIMULATION' in model:
            results['simulation'] = model['SIMULATION']
        if 'GRID_ATM' in model:
            results['grid_atm'] = model['GRID_ATM']
        if 'INPUTS' in model:
            # MODEL_INPUTS: Path to model input data (static files, initial conditions, etc.)
            results['model_inputs'] = model['INPUTS']
        
        # Extract full model path from MODEL.PATH
        if 'PATH' in model:
            # MODEL_PATH: Full path to the model executable and source code
            results['model_path'] = model['PATH']

    # Extract experiment members and numchunks
    if 'EXPERIMENT' in config:
        experiment = config['EXPERIMENT']
        if 'MEMBERS' in experiment:
            # EXPERIMENT_MEMBERS: List of ensemble members (e.g., fc0, fc1, fc2, etc.)
            results['experiment_members'] = experiment['MEMBERS']
        if 'NUMCHUNKS' in experiment:
            # EXPERIMENT_NUMCHUNKS: Total number of time chunks for the experiment
            results['experiment_numchunks'] = experiment['NUMCHUNKS']
        elif 'NUM_CHUNKS' in experiment:
            results['experiment_numchunks'] = experiment['NUM_CHUNKS']
        if 'DATELIST' in experiment:
            results['datelist'] = experiment['DATELIST']

    # Extract DATA_DIR from PLATFORMS section based on HPCARCH
    if 'hpcarch' in results and 'PLATFORMS' in config:
        hpcarch = results['hpcarch']
        platforms = config['PLATFORMS']
        
        if hpcarch in platforms:
            platform_config = platforms[hpcarch]
            if 'DATA_DIR' in platform_config:
                # MODEL_INPUTS: Path to model input data (from PLATFORMS section)
                results['model_inputs'] = platform_config['DATA_DIR']

    # Extract AQUA experiment name - try multiple possible locations
    if 'AQUA' in config:
        aqua = config['AQUA']
        
        # Try different possible keys for experiment name
        if 'EXPERIMENT_NAME' in aqua:
            # AQUA_EXPERIMENT_NAME: Name of the AQUA experiment for cataloging and output
            results['aqua_experiment_name'] = aqua['EXPERIMENT_NAME']
        elif 'experiment_name' in aqua:
            results['aqua_experiment_name'] = aqua['experiment_name']
        elif 'NAME' in aqua:
            results['aqua_experiment_name'] = aqua['NAME']
        elif 'name' in aqua:
            results['aqua_experiment_name'] = aqua['name']
        else:
            # If not found, print available keys in AQUA section for debugging
            print(f"\n⚠️ Warning: 'EXPERIMENT_NAME' not found in AQUA section")
            print(f"Available keys in AQUA: {list(aqua.keys())}")
            results['aqua_experiment_name'] = 'NOT FOUND'
    else:
        print(f"\n⚠️ Warning: 'AQUA' section not found in YAML file")
        results['aqua_experiment_name'] = 'NOT FOUND'

    # Get data-portfolio version from git
    data_portfolio_version = get_data_portfolio_version(expid)
    if data_portfolio_version:
        # DATA_PORTFOLIO_VERSION: Version of the data-portfolio repository (from git tag)
        results['data_portfolio_version'] = data_portfolio_version
    else:
        results['data_portfolio_version'] = 'NOT FOUND'

    # Extract workflow version
    if 'GIT' in config and 'PROJECT_BRANCH' in config['GIT']:
        branch = config['GIT']['PROJECT_BRANCH']
        # WORKFLOW_VERSION: Version of the workflow repository (from git branch)
        results['workflow_version'] = branch.replace('v', '')

    # Extract autosubmit version
    if 'CONFIG' in config and 'AUTOSUBMIT_VERSION' in config['CONFIG']:
        # AUTOSUBMIT_VERSION: Version of Autosubmit workflow manager
        results['autosubmit_version'] = config['CONFIG']['AUTOSUBMIT_VERSION']

    # Extract AQUA container version
    if 'AQUA' in config and 'CONTAINER_VERSION' in config['AQUA']:
        # AQUA_CONTAINER_VERSION: Version of the AQUA container
        results['aqua_container_version'] = config['AQUA']['CONTAINER_VERSION']

    # Extract GSV interface version
    if 'GSV' in config and 'VERSION' in config['GSV']:
        # GSV_INTERFACE_VERSION: Version of the GSV (Grid Specification and Visualization) interface
        results['gsv_interface_version'] = config['GSV']['VERSION']

    # Extract post-processing tools versions
    for tool in ['HYDROLAND', 'WILDFIRES_FWI', 'WILDFIRES_WISE', 'HYDROMET',
                 'ENERGY_INDICATORS', 'ENERGY_OFFSHORE', 'OPA']:
        if tool in config and 'VERSION' in config[tool]:
            # Version of the respective post-processing tool
            results[f'{tool.lower()}_version'] = config[tool]['VERSION']

    # Extract nodes from the appropriate platform
    if 'hpcarch' in results and 'PLATFORMS' in config:
        hpcarch = results['hpcarch']
        platforms = config['PLATFORMS']
        
        if hpcarch in platforms and 'NODES' in platforms[hpcarch]:
            # NODES: Number of compute nodes allocated for the experiment
            results['nodes'] = platforms[hpcarch]['NODES']

    return results


def display_table(results: Dict[str, Any]) -> None:
    """Display extracted information in a clean table without headers or subtitles."""
    
    # Define all parameters to display in desired order
    parameters = [
        'expid', 'hpcarch', 'hpcrootdir', 'startdates',
        'experiment_members', 'experiment_numchunks', 'model_inputs', 
        'simulation', 'grid_atm', 'model_path', 'aqua_experiment_name', 
        'data_portfolio_version', 'workflow_version', 'autosubmit_version', 
        'aqua_container_version', 'gsv_interface_version', 'hydroland_version', 
        'wildfires_fwi_version', 'wildfires_wise_version', 'hydromet_version', 
        'energy_indicators_version', 'energy_offshore_version', 'opa_version', 'nodes'
    ]
    
    # Display names for readability
    display_names = {
        'expid': 'EXPID',
        'hpcarch': 'HPCARCH',
        'hpcrootdir': 'HPCROOTDIR',
        'startdates': 'STARTDATES',
        'experiment_members': 'EXPERIMENT_MEMBERS',
        'experiment_numchunks': 'EXPERIMENT_NUMCHUNKS',
        'model_inputs': 'MODEL_INPUTS',
        'simulation': 'SIMULATION',
        'grid_atm': 'GRID_ATM',
        'model_path': 'MODEL_PATH',
        'aqua_experiment_name': 'aqua_experiment_name',
        'data_portfolio_version': 'data_portfolio_version',
        'workflow_version': 'workflow_version',
        'autosubmit_version': 'autosubmit_version',
        'aqua_container_version': 'aqua_container_version',
        'gsv_interface_version': 'gsv_interface_version',
        'hydroland_version': 'hydroland_version',
        'wildfires_fwi_version': 'wildfires_fwi_version',
        'wildfires_wise_version': 'wildfires_wise_version',
        'hydromet_version': 'hydromet_version',
        'energy_indicators_version': 'energy_indicators_version',
        'energy_offshore_version': 'energy_offshore_version',
        'opa_version': 'opa_version',
        'nodes': 'nodes',
    }
    
    # Print comments and data
    print("\n")
    # Comment for HPCROOTDIR
    print("# HPCROOTDIR: Main working directory on HPC where rundir, restarts, and AQUA APP output are located")
    
    for param in parameters:
        if param in results:
            # Handle list formatting for STARTDATES
            if param == 'startdates' and isinstance(results[param], list):
                # Print each date on a new line without quotes and without dash prefix
                for date in results[param]:
                    print(f"{display_names[param]:<25} {date}")
            else:
                print(f"{display_names[param]:<25} {results[param]}")
        else:
            print(f"{display_names[param]:<25} NOT FOUND")
    print("\n")


def save_results_to_yaml(results: Dict[str, Any], yaml_file: str) -> None:
    """Save results to a YAML file with comment only for hpcrootdir."""
    
    # Create output filename based on input file
    input_path = Path(yaml_file)
    base_name = input_path.stem
    experiment_id = input_path.parent.parent.parent.name
    
    yaml_output = f"{experiment_id}_{base_name}_versions.yaml"
    
    # Handle startdates formatting
    startdates_value = results.get('startdates', 'NOT FOUND')
    if isinstance(startdates_value, list):
        startdates_value = ' '.join(str(date) for date in startdates_value)
    
    # Build the YAML content as a string with comment only for hpcrootdir
    yaml_content = f"""experiment_info:
  expid: {results.get('expid', 'NOT FOUND')}
  hpcarch: {results.get('hpcarch', 'NOT FOUND')}
  # HPCROOTDIR: Main working directory on HPC where rundir, restarts, and AQUA APP output are located
  hpcrootdir: {results.get('hpcrootdir', 'NOT FOUND')}
  startdates: '{startdates_value}'
  experiment_members: {results.get('experiment_members', 'NOT FOUND')}
  experiment_numchunks: {results.get('experiment_numchunks', 'NOT FOUND')}
  model_inputs: {results.get('model_inputs', 'NOT FOUND')}
  simulation: {results.get('simulation', 'NOT FOUND')}
  grid_atm: {results.get('grid_atm', 'NOT FOUND')}
  aqua_experiment_name: {results.get('aqua_experiment_name', 'NOT FOUND')}

component_versions:
  model_path: {results.get('model_path', 'NOT FOUND')}
  data_portfolio_version: {results.get('data_portfolio_version', 'NOT FOUND')}
  workflow_version: {results.get('workflow_version', 'NOT FOUND')}
  autosubmit_version: {results.get('autosubmit_version', 'NOT FOUND')}
  aqua_container_version: {results.get('aqua_container_version', 'NOT FOUND')}
  gsv_interface_version: {results.get('gsv_interface_version', 'NOT FOUND')}
  hydroland_version: {results.get('hydroland_version', 'NOT FOUND')}
  wildfires_fwi_version: {results.get('wildfires_fwi_version', 'NOT FOUND')}
  wildfires_wise_version: {results.get('wildfires_wise_version', 'NOT FOUND')}
  hydromet_version: {results.get('hydromet_version', 'NOT FOUND')}
  energy_indicators_version: {results.get('energy_indicators_version', 'NOT FOUND')}
  energy_offshore_version: {results.get('energy_offshore_version', 'NOT FOUND')}
  opa_version: {results.get('opa_version', 'NOT FOUND')}

resources:
  nodes: {results.get('nodes', 'NOT FOUND')}
"""
    
    # Save to YAML file
    with open(yaml_output, 'w') as f:
        f.write(yaml_content)
    
    print(f"💾 Results saved to {yaml_output}")


def debug_yaml_structure(file_path: str) -> None:
    """Debug function to print the structure of the YAML file."""
    print("\n🔍 Debugging YAML structure...")
    print("="*50)
    
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    
    print("\nTop-level sections in YAML:")
    for key in config.keys():
        print(f"  - {key}")
    
    # Look for specific keys at top level
    top_keys = ['HPCROOTDIR', 'STARTDATES', 'ROOTDIR', 'PROJDIR']
    print("\nChecking top-level keys:")
    for key in top_keys:
        if key in config:
            print(f"  - {key}: {config[key]}")
    
    if 'DEFAULT' in config:
        print("\nDEFAULT section content:")
        default = config['DEFAULT']
        for key, value in default.items():
            print(f"  - {key}: {value}")
    
    if 'EXPERIMENT' in config:
        print("\nEXPERIMENT section content:")
        experiment = config['EXPERIMENT']
        for key, value in experiment.items():
            print(f"  - {key}: {value}")
    
    if 'MODEL' in config:
        print("\nMODEL section content:")
        model = config['MODEL']
        for key, value in model.items():
            print(f"  - {key}: {value}")
    
    if 'PLATFORMS' in config:
        print("\nPLATFORMS section content (first platform):")
        platforms = config['PLATFORMS']
        first_platform = list(platforms.keys())[0] if platforms else None
        if first_platform:
            print(f"  Platform: {first_platform}")
            for key, value in platforms[first_platform].items():
                if key == 'DATA_DIR':
                    print(f"    - {key}: {value}")
    
    if 'AQUA' in config:
        print("\nAQUA section content:")
        aqua = config['AQUA']
        for key, value in aqua.items():
            if key in ['EXPERIMENT_NAME', 'CONTAINER_VERSION', 'START_DATE']:
                print(f"  - {key}: {value}")
    
    print("="*50)


def main():
    """Main function."""

    # Check if YAML file path is provided
    if len(sys.argv) < 2:
        print("❌ Error: Please provide the path to experiment_data.yml")
        print("\nUsage:")
        print("  python3 extract_versions.py /path/to/experiment_data.yml")
        print("\nExample:")
        print("  python3 extract_versions.py /appl/AS/AUTOSUBMIT_DATA/o021/conf/metadata/experiment_data.yml")
        sys.exit(1)

    yaml_file = sys.argv[1]

    # Check if file exists
    if not os.path.exists(yaml_file):
        print(f"❌ Error: File '{yaml_file}' not found.")
        sys.exit(1)

    # Check if it's a file (not a directory)
    if not os.path.isfile(yaml_file):
        print(f"❌ Error: '{yaml_file}' is not a file.")
        sys.exit(1)

    # Extract experiment ID from the path
    input_path = Path(yaml_file)
    expid = input_path.parent.parent.parent.name
    
    # Optional: Add --debug flag to see YAML structure
    if len(sys.argv) > 2 and sys.argv[2] == '--debug':
        debug_yaml_structure(yaml_file)
    
    try:
        results = parse_yaml_config(yaml_file, expid)
        display_table(results)
        save_results_to_yaml(results, yaml_file)

    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
