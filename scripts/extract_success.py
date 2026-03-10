import json
import re
import os
import argparse
from bs4 import BeautifulSoup

def process(html_file, json_file, output_file, start_region, end_region):
    # Load HTML
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading HTML: {e}")
        return

    # Parse HTML and find all successful nodes
    soup = BeautifulSoup(html_content, 'html.parser')

    # Track successful region IDs
    successful_regions = set()

    # The structure has a row for each probe
    rows = soup.find_all('tr')
    for row in rows:
        tds = row.find_all('td')
        if len(tds) < 6:
            continue

        # Check if the row indicates success
        status_td = tds[5]
        if 'succeeded' in status_td.text:
            # Extract region ID from the name column (1st column) or labels column (2nd column)
            labels_td = tds[1]
            labels_text = labels_td.text

            # Look for region_id=XXXX
            match = re.search(r'region_id=(\d+)', labels_text)
            if match:
                region_id = match.group(1)
                successful_regions.add(region_id)

    print(f"Found {len(successful_regions)} successful region IDs")

    # Load original derp.json
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    # Filter the regions
    original_regions_count = len(data.get("Regions", {}))
    new_regions = {}

    for region_id, region_data in data.get("Regions", {}).items():
        try:
            if region_id in successful_regions and start_region <= int(region_id) <= end_region:
                new_regions[region_id] = region_data
        except ValueError:
            pass

    data["Regions"] = new_regions

    # Save to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Original regions: {original_regions_count}")
    print(f"Filtered regions: {len(new_regions)}")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract successful DERP regions from HTML report.')
    parser.add_argument('--html', type=str, required=True, help='Path to the HTML file saved from DERP Prober')
    parser.add_argument('--json', type=str, required=True, help='Path to the original derp.json file')
    parser.add_argument('--output', type=str, default='derp-success-prober.json', help='Path for the output JSON file')
    parser.add_argument('--start', type=int, default=900, help='Start of region ID range (inclusive)')
    parser.add_argument('--end', type=int, default=999, help='End of region ID range (inclusive)')

    args = parser.parse_args()
    process(args.html, args.json, args.output, args.start, args.end)
