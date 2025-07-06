#!/usr/bin/env python3
"""
Notion Database Entry Script - JSON File Input

This script accepts a JSON file and adds its contents to your Notion database.

Usage: 
  python add_notion_entry.py path/to/your/data.json

The JSON file should contain the entry data with the appropriate fields for your Notion database.
"""

"""
MARKDOWN TO JSON CONVERSION GUIDELINES:
When converting markdown entries to JSON format, follow these rules:

VALID CATEGORIES - Always use one of these exact categories from notion_categories.md:
(Note: If your category contains commas, they will be automatically replaced with slashes)
- 1. Documentation
- 1.1 History of Assignments
- 1.1.1 Education
- 1.1.2 Employment History
- 1.2 Teaching
- 1.2.1 Documentation of Teaching Activities
- 1.2.1.1 Teaching Evaluations
- 1.2.1.2 Teaching History
- 1.2.1.3 Innovative Teaching Contributions
- 1.2.2 Publications Concerning Instruction (Only published items)
- 1.2.2.1 Textbooks
- 1.2.2.2 Pedagogical Publications
- 1.2.2.3 Edited Books
- 1.2.2.4 Recordings and Media
- 1.2.2.5 Instructional Materials
- 1.2.2.6 Miscellaneous
- 1.2.3 Publications Accepted but Not Yet Published
- 1.2.4 Participation in Teaching-Related Events
- 1.2.4.1 Professional Meetings / Symposia / Workshops / Conferences
- 1.2.4.2 Local Instructional Activities
- 1.2.5 Other Instructional Activities & Contributions
- 1.2.5.1 Professional Organization Membership
- 1.2.5.2 Administrative Duties
- 1.2.5.3 Innovation and Development
- 1.2.6 Awards and Recognition
- 1.2.7 Teaching-Related Research/Grants
- 1.3 Scholarship
- 1.3.1 Research Publications (Published items only)
- 1.3.1.1 Books and Monographs
- 1.3.1.2 Shorter Works
- 1.3.1.3 Edited Books
- 1.3.1.4 Collections of Unpublished Materials
- 1.3.1.5 Recordings and Media
- 1.3.1.6 Patents and Innovations
- 1.3.1.7 Electronic Dissemination of Research
- 1.3.1.8 Miscellaneous
- 1.3.1.9 Exhibition Catalogs / Media Coverage / Reviews / Conference Proceedings
- 1.3.2 Accepted but Unpublished Publications
- 1.3.3 Creative & Artistic Contributions (For faculty with creative activity obligations)
- 1.3.3.1 Original Creative Works & Presentations
- 1.3.3.2 Curation and Event Organization
- 1.3.4 Participation in Professional Academic Events
- 1.3.5 Other Scholarly/Creative Contributions
- 1.3.5.1 Professional Organizations
- 1.3.5.2 Administrative Duties
- 1.3.5.3 Standards and Equipment
- 1.3.5.4 Community-Engaged Scholarship
- 1.3.6 Awards / Lectureships / Prizes
- 1.3.7 Research Support/Grant Activities
- 1.3.8 Theses/Dissertations Directed
- 1.3.9 Major Areas of Research Interest
- 1.4 Service
- 1.4.1 Clinical and Professional Service
- 1.4.2 Student Organizations and Recruitment
- 1.4.3 University Service
- 1.4.4 Professional Service
- 1.4.5 Government and Community Service
- 1.4.6 Scholarly and Technical Service
- 2. Supporting Material
- 2.1 Teaching Portfolios and Evidence
- 2.2 Letters and Testimonials
- 2.3 Scholarly Evidence and Documentation
- 2.4 Creative and Artistic Work
- 2.5 Service Documentation

1. ROLE PLACEMENT: If the markdown mentions a role (PI, Co-PI, Presenter, Panel Chair, etc.), 
   put that role information at the BEGINNING of the description field.
   Example: "Panel Chair for ACM SIGGRAPH..." or "Invited speaker at..."

2. LOCATION PLACEMENT: If the markdown mentions a location (city, venue, institution), 
   put that location information towards the END of the description field.
   Example: "...presented at the conference in Austin, TX." or "...held in Los Angeles, CA."

3. URL INCLUSION: If the markdown includes a URL, include that URL somewhere in the description field.
   The URL should also be added to the separate "URL" field.
   Example: "...more details available at https://example.com" or "...see https://example.com for full presentation"

4. DESCRIPTION STRUCTURE: Build descriptions in this order:
   - Role (if mentioned) at the beginning
   - Main content/details in the middle  
   - URL (if mentioned) in the middle or end
   - Location (if mentioned) at the end

5. LOCATION FIELD: Use the separate "Location" field only for "City State" format 
   (e.g., "Austin TX", "Los Angeles CA"). Always include full location details in description too.

6. DATE FORMAT: Use YYYY-MM-DD format. If only year is provided, use YYYY-01-01.
   For date ranges, use an object with "start" and "end" properties:
   {"start": "2011-01-01", "end": "2023-12-31"}
   For single dates, use a string: "2023-01-01"
   For ongoing activities (present, current, ongoing), use "present" as the end date:
   {"start": "2011-01-01", "end": "present"}
   The script will automatically convert "present" to today's date.
   If no date is provided or mentioned in the source material, simply omit the "Date"
   field from the JSON entirely. Don't guess or make up dates.

Example conversion:
Markdown: "1.3.6 Other awards, lectureships, or prizes - ACM SIGGRAPH Award in Los Angeles, see https://siggraph.org"
JSON: {
  "Name": "ACM SIGGRAPH Award",
  "Description": "Recipient of ACM SIGGRAPH Award, details at https://siggraph.org, presented in Los Angeles, CA.",
  "Location": "Los Angeles CA",
  "Role": "Recipient",
  "URL": "https://siggraph.org",
  "Category": "1.3.6 Awards, Lectureships, Prizes"
}
"""

import requests
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_API_URL = "https://api.notion.com/v1"

# Check if required environment variables are set
if not DATABASE_ID or not NOTION_TOKEN:
    print("❌ Error: Missing required environment variables.")
    print("Please make sure DATABASE_ID and NOTION_TOKEN are set in your .env file.")
    exit(1)

# Headers for Notion API
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def load_json_file(json_file_path):
    """Load and parse the JSON file."""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"❌ Error: File '{json_file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in file '{json_file_path}': {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading file '{json_file_path}': {e}")
        return None


def create_notion_page(entry_data):
    """Create a new page in the Notion database with the specified data."""
    
    # Build the page content blocks
    children = []
    for content_item in entry_data.get("page_content", []):
        if content_item["type"] == "paragraph":
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": content_item["text"]}
                    }]
                }
            })
        elif content_item["type"] == "heading_2":
            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": content_item["text"]}
                    }]
                }
            })
        elif content_item["type"] == "heading_1":
            children.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": content_item["text"]}
                    }]
                }
            })
        elif content_item["type"] == "heading_3":
            children.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": content_item["text"]}
                    }]
                }
            })
    
    # Build the page data
    page_data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {},
        "children": children
    }
    
    # Add properties based on what's provided in entry_data
    if "Name" in entry_data:
        page_data["properties"]["Name"] = {
            "title": [{
                "text": {"content": entry_data["Name"]}
            }]
        }
    
    if "Description" in entry_data:
        page_data["properties"]["Description"] = {
            "rich_text": [{
                "text": {"content": entry_data["Description"]}
            }]
        }
    
    if "Category" in entry_data:
        # Replace commas with slashes to avoid Notion API issues
        category_value = entry_data["Category"].replace(",", " /")
        page_data["properties"]["Category"] = {
            "select": {"name": category_value}
        }
    
    if "Location" in entry_data:
        page_data["properties"]["Location"] = {
            "select": {"name": entry_data["Location"]}
        }
    
    if "Role" in entry_data:
        page_data["properties"]["Role"] = {
            "select": {"name": entry_data["Role"]}
        }
    
    if "Date" in entry_data:
        date_data = entry_data["Date"]
        if isinstance(date_data, dict):
            # Handle date range with start and end
            date_prop = {}
            if "start" in date_data:
                date_prop["start"] = date_data["start"]
            if "end" in date_data:
                end_date = date_data["end"]
                # Convert "present" or similar terms to today's date
                if end_date.lower() in ["present", "ongoing", "current", "now"]:
                    end_date = datetime.now().strftime("%Y-%m-%d")
                date_prop["end"] = end_date
            page_data["properties"]["Date"] = {
                "date": date_prop
            }
        else:
            # Handle single date (string format)
            page_data["properties"]["Date"] = {
                "date": {"start": date_data}
            }
    
    if "URL" in entry_data:
        page_data["properties"]["URL"] = {
            "url": entry_data["URL"]
        }
    
    if "Show Page Contents" in entry_data:
        page_data["properties"]["Show Page Contents"] = {
            "checkbox": entry_data["Show Page Contents"]
        }
    
    if "Pinned" in entry_data:
        page_data["properties"]["Pinned"] = {
            "checkbox": entry_data["Pinned"]
        }
    
    # Make the API request
    print(f"📤 Sending to Notion API:")
    if "Category" in entry_data:
        category_value = entry_data["Category"].replace(",", "/")
        print(f"   Original Category: '{entry_data['Category']}'")
        print(f"   Modified Category: '{category_value}'")
        print(f"   Category property structure: {page_data['properties']['Category']}")
    else:
        print(f"   Category value: 'Not provided'")
    
    response = requests.post(
        f"{NOTION_API_URL}/pages",
        headers=HEADERS,
        json=page_data
    )
    
    if response.status_code == 200:
        result = response.json()
        page_id = result.get("id", "Unknown")
        page_url = result.get("url", "Unknown")
        print(f"✅ Successfully created page!")
        print(f"   Page ID: {page_id}")
        print(f"   Page URL: {page_url}")
        print(f"   Title: {entry_data.get('Name', 'Unknown')}")
        
        # Check if category was actually set
        if "Category" in entry_data:
            print(f"   Expected Category: {entry_data['Category']}")
        
        return True
    else:
        print(f"❌ Error creating page:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Try to parse error details
        try:
            error_data = response.json()
            if "message" in error_data:
                print(f"   Error Message: {error_data['message']}")
            # Print the full error response for debugging
            print(f"   Full Error Response: {json.dumps(error_data, indent=2)}")
        except:
            pass
        return False


def main():
    """Main function to run the script."""
    if len(sys.argv) != 2:
        print("❌ Error: Please provide a JSON file path.")
        print("Usage: python add_notion_entry.py path/to/your/data.json")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    # Load the JSON file
    data = load_json_file(json_file_path)
    if data is None:
        sys.exit(1)
    
    # Check if data is an array or single entry
    if isinstance(data, list):
        # Multiple entries
        entries = data
        print(f"🚀 Adding {len(entries)} entries to Notion database...")
        print(f"   Database ID: {DATABASE_ID}")
        print(f"   JSON File: {json_file_path}")
        print("=" * 50)
        
        successful = 0
        failed = 0
        
        for i, entry_data in enumerate(entries, 1):
            print(f"\n[{i}/{len(entries)}] Processing: {entry_data.get('Name', 'Unknown')}")
            
            # Create the Notion page
            success = create_notion_page(entry_data)
            if success:
                successful += 1
            else:
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Batch addition complete!")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📋 Total: {len(entries)}")
        
        if failed > 0:
            sys.exit(1)
    else:
        # Single entry
        entry_data = data
        print("🚀 Adding entry to Notion database...")
        print(f"   Database ID: {DATABASE_ID}")
        print(f"   JSON File: {json_file_path}")
        print(f"   Entry Name: {entry_data.get('Name', 'Unknown')}")
        print()
        
        # Create the Notion page
        success = create_notion_page(entry_data)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
