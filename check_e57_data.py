# Quick diagnostic script to check E57 data structure
import e57
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

e57_file = config['e57_files'][0]
print(f"Checking file: {e57_file}")

# Read E57 data
e57_data = e57.read_points(e57_file)

print(f"\n=== E57 Data Structure ===")
print(f"Points shape: {e57_data.points.shape}")
print(f"Points dtype: {e57_data.points.dtype}")

if hasattr(e57_data, 'color') and e57_data.color is not None:
    print(f"\nColor shape: {e57_data.color.shape}")
    print(f"Color dtype: {e57_data.color.dtype}")
else:
    print("\nColor: NOT AVAILABLE")

if hasattr(e57_data, 'intensity') and e57_data.intensity is not None:
    print(f"\nIntensity shape: {e57_data.intensity.shape}")
    print(f"Intensity dtype: {e57_data.intensity.dtype}")
else:
    print("\nIntensity: NOT AVAILABLE")

print(f"\n=== Available attributes ===")
print([attr for attr in dir(e57_data) if not attr.startswith('_')])
