import os
import yaml
import pandas as pd
from tqdm import tqdm

# Input and output directories
input_dir = r"D:\Stock-Analysis\Data-yaml"
output_dir = r"D:\Stock-Analysis\CSV_Output"
os.makedirs(output_dir, exist_ok=True)

all_data = []

# Step 1: Read all YAML files
for root, dirs, files in os.walk(input_dir):
    for file in tqdm(files, desc="Reading YAML files"):
        if file.endswith(".yaml"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    # Some YAMLs might contain a single record or a list
                    if isinstance(data, list):
                        all_data.extend(data)
                    elif isinstance(data, dict):
                        all_data.append(data)
            except Exception as e:
                print(f"⚠️ Skipping invalid YAML: {file_path} ({e})")

print(f"\n✅ Total records loaded: {len(all_data)}")

# Step 2: Convert to DataFrame
df = pd.DataFrame(all_data)

# Step 3: Group by Ticker and save each group as CSV
for ticker, group in df.groupby('Ticker'):
    output_file = os.path.join(output_dir, f"{ticker}.csv")
    group.to_csv(output_file, index=False)
    print(f"📁 Saved {ticker}.csv with {len(group)} rows")

print("\n🎉 All CSV files generated successfully!")
