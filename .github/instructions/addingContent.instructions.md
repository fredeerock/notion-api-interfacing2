---
applyTo: '**'
---

When the user asks to add markdown content to a Notion database:

1. **File Organization**: Always create JSON files in the `json-files/` directory:
   - Path: `/Users/dostrenko/Documents/devwork/notion-api-interfacing2/json-files/filename.json`
   - Create the directory if it doesn't exist

2. **File Naming**: Use descriptive names:
   - `education_batch.json`, `employment_history_batch.json`, `teaching_history_batch.json`, etc.

3. **Conversion Rules**: Follow all guidelines in `add_notion_entry.py` for JSON structure, categories, and field formatting.

4. **Execution**: After creating the JSON file, run:
   ```bash
   cd /Users/dostrenko/Documents/devwork/notion-api-interfacing2 && pipenv run python add_notion_entry.py json-files/filename.json
   ``` 