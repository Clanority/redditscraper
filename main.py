# Reddit Post Logger Script
# Tracks new Reddit posts across all subreddits and logs them into an OpenDocument Spreadsheet (ODS)
# Requires Python 3.10+, praw, and odfpy
# Make sure to create a reddit_config.json with your Reddit API credentials
# This script prints posts to the console as they happen and stores them in an ODS file.

import praw
import json
import time
import os
from odf.opendocument import OpenDocumentSpreadsheet, load
from odf.table import Table, TableRow, TableCell
from odf.text import P

# ---------------- CONFIGURATION ---------------- #

CONFIG_FILE = "reddit_config.json"  # JSON file containing Reddit API credentials
ODS_FILE = "reddit_output.ods"      # File to store logged posts

# ---------------- LOAD CONFIG ------------------ #

# Make sure the config file exists
if not os.path.exists(CONFIG_FILE):
    print(f"{CONFIG_FILE} not found! Please create it with your Reddit API credentials.")
    exit()

# Load Reddit credentials from the JSON config file
with open(CONFIG_FILE) as f:
    config = json.load(f)

# Create a Reddit instance using PRAW
reddit = praw.Reddit(
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    user_agent=config["user_agent"]
)

# ---------------- LOAD OR CREATE ODS FILE ---------------- #

if os.path.exists(ODS_FILE):
    # If the ODS file exists, load it
    doc = load(ODS_FILE)
    table = doc.spreadsheet.getElementsByType(Table)[0]
    try:
        # Try to read the last used ID from the last row
        last_row = table.getElementsByType(TableRow)[-1]
        last_id_cell = last_row.getElementsByType(TableCell)[0]
        last_id = last_id_cell.getElementsByType(P)[0].firstChild.data
    except Exception:
        # If anything fails, start from scratch
        last_id = None
else:
    # If the ODS file doesn't exist, create a new one
    doc = OpenDocumentSpreadsheet()
    table = Table(name="RedditPosts")
    doc.spreadsheet.addElement(table)

    # Add a header row
    header = TableRow()
    for h in ["ID", "Subreddit", "Title", "URL"]:
        cell = TableCell()
        cell.addElement(P(text=h))
        header.addElement(cell)
    table.addElement(header)

    last_id = None

# ---------------- FUNCTION TO GENERATE NEXT ID ---------------- #

def next_id(last):
    """
    Generates the next ID in the sequence.
    Starts at A001, then A002, ..., A999, then B001, etc.
    Supports multi-letter prefixes like Z999 -> AA001.
    """
    if not last:
        return "A001"

    # Split last ID into letters and number
    prefix = last[:-3]  # e.g., 'A', 'AB'
    number = int(last[-3:])

    # Increment the number
    number += 1

    if number > 999:
        # Reset number and increment letters
        number = 1
        if prefix == "":
            prefix = "A"
        else:
            # Increment the string prefix like a counter
            prefix_list = list(prefix)
            i = len(prefix_list) - 1
            while i >= 0:
                if prefix_list[i] != 'Z':
                    prefix_list[i] = chr(ord(prefix_list[i]) + 1)
                    break
                else:
                    prefix_list[i] = 'A'
                    i -= 1
            else:
                prefix_list.insert(0, 'A')
            prefix = "".join(prefix_list)

    return f"{prefix}{number:03d}"

# Initialize last_id
last_id = next_id(last_id)

# Keep track of already seen post IDs to avoid duplicates
seen_posts = set()

print(f"Starting Reddit console scraper. Last ID = {last_id}")
print("Press CTRL+C to stop.\n")

# ---------------- MAIN SCRAPER LOOP ---------------- #

try:
    # Stream new submissions from all of Reddit
    for post in reddit.subreddit("all").stream.submissions(skip_existing=True):

        # Skip if we've already seen this post
        if post.id in seen_posts:
            continue
        seen_posts.add(post.id)

        # Create a new row for the ODS file
        row = TableRow()

        # Add ID cell
        cell = TableCell()
        cell.addElement(P(text=last_id))
        row.addElement(cell)

        # Add Subreddit cell
        cell = TableCell()
        cell.addElement(P(text=post.subreddit.display_name))
        row.addElement(cell)

        # Add Title cell
        cell = TableCell()
        cell.addElement(P(text=post.title))
        row.addElement(cell)

        # Add URL cell
        cell = TableCell()
        cell.addElement(P(text=f"https://redd.it/{post.id}"))
        row.addElement(cell)

        # Add row to the table
        table.addElement(row)

        # Save the ODS file (optional: can be delayed for caching)
        doc.save(ODS_FILE)

        # Print to console
        print(f"[{last_id}] {post.subreddit.display_name}: {post.title} (https://redd.it/{post.id})")

        # Generate next ID
        last_id = next_id(last_id)

except KeyboardInterrupt:
    print("\nScraper stopped by user.")

