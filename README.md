
# Todo
* [DONE] Get account with Hertzner
* [DONE] Get account with Google Drive 100GB
* [DONE] Setup Google Drive API
* [DONE] Customer View
* [DONE] Admin View
* [DONE] Customer Inventory
* Email notification on inventory change
* [DONE] Download table buttons
  * [DONE] Inventory
  * [DONE] Report
  * [DONE] Report Historical
* [DONE] Move inventory logic out of inventory views
* [DONE] Make inventory tests
* Home page
* Sort download table
* Paginate tables

# DB Migration

1. Download and extract old SQL database "runners_inventorymanagement.sql"
2. Convert sql file to sqlite format using https://brunocassol.com/mysql2sqlite/ and save as "old.sqlite3"
3. Remove all LOCK and UNLOCK commands manually (8 count)
4. Initialize db using command "sqlite3 old_processed.sqlite3 -init old.sqlite3"

# Meeting Notes

## Things to Cover

1. Email server and template
2. Download table format
3. Data import scheme (100% remarks or no-duplicate)
4. Products that no longer exist (db migration)
5. Missing fields (db migration)

Current plan for data migration. Auto-categorize data when possible. If any data can't be categorized automatically add it to the remarks section.

## Changes

1.