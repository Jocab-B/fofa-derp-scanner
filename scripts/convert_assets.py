import json
import argparse
import sys

def convert_asset_to_derp(input_file, output_file, start_region_id=900):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            assets = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    derp_data = {"Regions": {}}
    current_region_id = start_region_id

    for i, asset in enumerate(assets):
        # Extract IP and Port
        ip = asset.get("ip", "")
        port_str = asset.get("port", "")
        domain = asset.get("domain", "")

        if not ip or not port_str:
            continue

        try:
            port = int(port_str)
        except ValueError:
            continue

        region_id_str = str(current_region_id)

        # Decide HostName vs IPv4 based on domain presence
        node = {
            "Name": f"{region_id_str}-{domain if domain else ip}",
            "RegionID": current_region_id,
            "DERPPort": port,
            "InsecureForTests": True
        }

        if domain:
            node["HostName"] = domain
        else:
            node["IPv4"] = ip

        region = {
            "RegionID": current_region_id,
            "RegionCode": f"custom{current_region_id}",
            "RegionName": asset.get("city", "") or "",
            "Nodes": [node]
        }

        derp_data["Regions"][region_id_str] = region
        current_region_id += 1

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(derp_data, f, indent=4, ensure_ascii=False)
        print(f"Successfully converted {len(derp_data['Regions'])} nodes.")
        print(f"Region IDs used: {start_region_id} to {current_region_id - 1}")
        print(f"Saved to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert FOFA JSON assets to DERP map JSON.')
    parser.add_argument('--input', type=str, required=True, help='Path to the FOFA assets JSON file')
    parser.add_argument('--output', type=str, default='derp.json', help='Path for the output DERP JSON file')
    parser.add_argument('--start', type=int, default=900, help='Start ID for generated regions')

    args = parser.parse_args()
    convert_asset_to_derp(args.input, args.output, args.start)
