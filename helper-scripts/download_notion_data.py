#!/usr/bin/env python3
"""
Download all data from Notion database and save as JSON file
"""

import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Configuration
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_API_URL = "https://api.notion.com/v1"

# Headers for Notion API
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_all_pages():
    """Get all pages from the Notion database."""
    all_pages = []
    has_more = True
    next_cursor = None
    
    print("🔍 Fetching all pages from Notion database...")
    
    while has_more:
        url = f"{NOTION_API_URL}/databases/{DATABASE_ID}/query"
        
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor
            
        response = requests.post(url, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            all_pages.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
            print(f"   Retrieved {len(all_pages)} pages so far...")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
    
    return all_pages

def extract_text_from_page(page):
    """Extract readable text from a Notion page."""
    extracted = {
        "id": page.get("id", ""),
        "created_time": page.get("created_time", ""),
        "last_edited_time": page.get("last_edited_time", ""),
        "properties": {}
    }
    
    props = page.get("properties", {})
    
    for prop_name, prop_data in props.items():
        prop_type = prop_data.get("type", "")
        
        if prop_type == "title":
            # Extract title text
            title_list = prop_data.get("title", [])
            if title_list:
                extracted["properties"][prop_name] = title_list[0].get("text", {}).get("content", "")
            else:
                extracted["properties"][prop_name] = ""
                
        elif prop_type == "rich_text":
            # Extract rich text
            rich_text_list = prop_data.get("rich_text", [])
            if rich_text_list:
                extracted["properties"][prop_name] = rich_text_list[0].get("text", {}).get("content", "")
            else:
                extracted["properties"][prop_name] = ""
                
        elif prop_type == "select":
            # Extract select option
            select_data = prop_data.get("select")
            if select_data:
                extracted["properties"][prop_name] = select_data.get("name", "")
            else:
                extracted["properties"][prop_name] = ""
                
        elif prop_type == "date":
            # Extract date
            date_data = prop_data.get("date")
            if date_data:
                extracted["properties"][prop_name] = date_data.get("start", "")
            else:
                extracted["properties"][prop_name] = ""
                
        elif prop_type == "url":
            # Extract URL
            extracted["properties"][prop_name] = prop_data.get("url", "")
            
        elif prop_type == "checkbox":
            # Extract checkbox
            extracted["properties"][prop_name] = prop_data.get("checkbox", False)
            
        elif prop_type == "files":
            # Extract files
            files_list = prop_data.get("files", [])
            extracted["properties"][prop_name] = [f.get("name", "") for f in files_list]
            
        elif prop_type == "relation":
            # Extract relation
            relation_list = prop_data.get("relation", [])
            extracted["properties"][prop_name] = [r.get("id", "") for r in relation_list]
            
        elif prop_type == "created_time":
            # Extract created time
            extracted["properties"][prop_name] = prop_data.get("created_time", "")
            
        else:
            # For other types, just store the raw data
            extracted["properties"][prop_name] = prop_data
    
    return extracted

def main():
    print("🚀 Starting Notion database download...")
    
    # Get all pages
    pages = get_all_pages()
    print(f"📊 Found {len(pages)} total pages")
    
    # Extract text from all pages
    print("📝 Extracting text from all pages...")
    extracted_data = []
    
    for i, page in enumerate(pages, 1):
        extracted_page = extract_text_from_page(page)
        extracted_data.append(extracted_page)
        
        if i % 10 == 0:
            print(f"   Processed {i}/{len(pages)} pages...")
    
    # Create output data structure
    output_data = {
        "database_id": DATABASE_ID,
        "download_time": datetime.now().isoformat(),
        "total_pages": len(pages),
        "pages": extracted_data
    }
    
    # Save to JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"notion_database_export_{timestamp}.json"
    
    print(f"💾 Saving data to {filename}...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully exported {len(pages)} pages to {filename}")
    
    # Print summary
    print(f"\n📈 Summary:")
    print(f"   Total pages: {len(pages)}")
    print(f"   File size: {os.path.getsize(filename)} bytes")
    print(f"   Export time: {output_data['download_time']}")
    
    # Show categories summary
    categories = {}
    for page in extracted_data:
        category = page.get("properties", {}).get("Category", "")
        if category:
            categories[category] = categories.get(category, 0) + 1
    
    print(f"\n📊 Categories found:")
    for category, count in sorted(categories.items()):
        print(f"   {category}: {count}")

if __name__ == "__main__":
    main()
