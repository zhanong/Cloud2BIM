# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cloud2BIM is a Python-based tool that automates the Scan-to-BIM process by converting point cloud data (.e57 or .xyz formats) into 3D parametric building models in IFC format. The system segments point clouds into building elements (slabs, walls, windows, doors) and generates spaces/zones, producing OpenBIM-compatible output.

## Core Architecture

### Main Processing Pipeline (`cloud2entities.py`)

The main script orchestrates the entire conversion process:
1. **Configuration Loading**: Reads YAML config via `aux_functions.load_config_and_variables()`
2. **Point Cloud Import**: Handles E57 to XYZ conversion if needed, loads and dilutes point clouds
3. **Slab Segmentation**: Identifies horizontal surfaces parallel to XY-plane using density analysis (`identify_slabs`)
4. **Storey Splitting**: Divides point cloud into storeys based on detected slabs
5. **Wall Detection**: Segments walls per storey using `identify_walls` with grid-based analysis
6. **Opening Classification**: Detects and classifies windows/doors via `identify_openings` using histograms and morphological operations
7. **Space Generation**: Divides storeys into zones/spaces (`identify_zones` from `space_generator.py`)
8. **IFC Generation**: Creates IFC model with all detected elements using `generate_ifc.IFCmodel`

### Key Modules

- **`aux_functions.py`**: Utility functions including config loading, E57/XYZ file handling, point cloud processing, slab identification, wall segmentation, opening detection
- **`generate_ifc.py`**: `IFCmodel` class wrapping ifcopenshell for creating IFC entities (walls, slabs, windows, doors, spaces, materials, relationships)
- **`space_generator.py`**: Zone/space segmentation from wall boundaries using Shapely geometry operations
- **`plotting_functions.py`**: Visualization utilities for debugging and validation

### Configuration System

The project uses YAML configuration files (`config.yaml` by default) with the following key sections:
- **Input/Output**: E57/XYZ file paths, dilution settings, output IFC path
- **Point Cloud Parameters**: `pc_resolution`, `grid_coefficient`, `exterior_scan` flag
- **Slab Settings**: `bfs_thickness` (bottom floor slab), `tfs_thickness` (top floor slab)
- **Wall Parameters**: min/max wall thickness, min wall length, exterior wall thickness
- **IFC Metadata**: Project name, author info, building type, site coordinates, material assignments

## Development Commands

### Running the Main Pipeline

```bash
# Run with default config.yaml
python cloud2entities.py

# Run with specific config file
python cloud2entities.py path/to/config.yaml
```

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Testing and Validation

The project generates diagnostic outputs in the `images/` directory:
- `images/wall_outputs_images/`: Wall segmentation visualizations
- `images/pdf/`: PDF plots for spaces and geometries
- `log.txt`: Timestamped execution log with elapsed times

## Key Technical Details

### Coordinate System
- Point clouds use standard XYZ coordinates (meters)
- Z-axis is vertical (building height)
- IFC placement uses local coordinate systems relative to building storeys

### Segmentation Algorithm Flow
1. **Slab detection**: Scans Z-axis with `z_step=0.15m` intervals, identifies density peaks
2. **Wall segmentation**: Projects storey point clouds to 2D grid, applies morphological closing, extracts wall centerlines
3. **Opening detection**: Analyzes wall point clouds in local 2D coordinate system, uses histogram peaks for width/height, classifies doors (z_min < 0.1m, height > 1.6m) vs windows

### Wall Representation
Walls are stored as dictionaries with:
- `start_point`, `end_point`: Centerline endpoints (X, Y)
- `thickness`: Wall thickness (meters)
- `z_placement`: Base elevation
- `height`: Wall height
- `label`: 'exterior' or 'interior'
- `storey`: Storey number (1-indexed)

### Opening Detection Parameters
Key thresholds in `identify_openings()`:
- `min_opening_width`: 0.4m
- `min_opening_height`: 0.6m
- `max_opening_aspect_ratio`: 4
- `door_z_max`: 0.1m (max ground clearance for doors)
- `door_min_height`: 1.6m

### IFC Model Structure
The generated IFC hierarchy follows:
```
IfcProject
└── IfcSite (with lat/lon/elevation)
    └── IfcBuilding
        └── IfcBuildingStorey (per floor)
            ├── IfcSlab
            ├── IfcWall (with IfcMaterialLayerSetUsage)
            │   ├── IfcOpeningElement
            │   │   └── IfcWindow / IfcDoor (via IfcRelFillsElement)
            └── IfcSpace (zones/rooms)
```

## Important Implementation Notes

### Configuration Validation
`load_config_and_variables()` validates all required YAML keys on startup. Missing keys cause immediate exit with error messages.

### E57 Processing
When `e57_input: true`, the system:
1. Reads E57 files using the `e57` library
2. Converts to XYZ format via `e57_data_to_xyz()` with chunking (chunk_size=1e10)
3. Saves intermediate XYZ files for reuse

### Exterior vs Interior Scans
The `exterior_scan` flag changes wall height calculation logic:
- **Interior scan**: Walls extend from slab bottom to next slab bottom
- **Exterior scan**: Walls extend from slab top to next slab bottom

### Material Assignment
- Materials use RGB colors defined in `cloud2entities.py` (doors, windows, columns, beams, stairs)
- Walls/slabs use material name from `material_for_objects` config
- Colors are assigned via `create_material_with_color()` with optional transparency

### Wall Type Classification
Walls are classified as 'exterior' or 'interior' during segmentation. This is stored as an IFC property 'IsExternal' in the 'wall properties' property set.

## Diagnostic Features

### Logging System
All major operations are logged to `log.txt` with:
- Timestamp (YYYY-MM-DD, HH:MM:SS)
- Operation description
- Elapsed time since last log entry

### Visualization Outputs
The codebase includes extensive plotting capabilities (mostly optional via flags):
- `plot_xyz`: 3D point cloud visualization
- `plot_segmented_plane`: Slab segmentation results
- `plot_histograms_for_openings`: Opening detection analysis
- `plot_zones`: Space/zone boundaries

Enable these by setting corresponding parameters to `True` in function calls.

## Dependencies

Key libraries and their purposes:
- **ifcopenshell**: IFC file creation and manipulation (v0.8.1)
- **open3d**: Point cloud processing and visualization (v0.19.0)
- **e57 / pye57**: E57 point cloud format handling
- **shapely**: 2D geometry operations for space generation
- **opencv-python**: Image processing for wall segmentation
- **scikit-image**: Morphological operations
- **scipy**: Signal processing (peak finding for opening detection)
- **numpy**: Numerical operations
- **matplotlib/plotly**: Visualization

## Recent Development Context

Recent commits indicate work on:
- Wall axis calculation diagnostics and validation
- E57 to XYZ conversion improvements
- Project configuration updates for specific buildings (454 Natoma St)
- Preserving folder structure with .gitignore files
- Slab diagnostic tools

## File Organization

```
Cloud2BIM/
├── cloud2entities.py          # Main pipeline script
├── generate_ifc.py            # IFC model generation
├── space_generator.py         # Zone/space segmentation
├── aux_functions.py           # Core utilities and algorithms
├── plotting_functions.py      # Visualization helpers
├── config.yaml                # Configuration (project-specific)
├── requirements.txt           # Python dependencies
├── output_xyz/                # Intermediate XYZ files
├── output_IFC/                # Generated IFC models
├── images/                    # Diagnostic visualizations
└── input_e57/                 # Input point cloud files
```
