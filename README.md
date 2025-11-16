# Reddit Post Logger – Free to Use Python Script

This Python script tracks new Reddit posts and logs them into an OpenDocument Spreadsheet (ODS). Each post gets a unique ID, and the script records the subreddit name, post title, and a shortened Reddit link. It keeps counting IDs across restarts so nothing gets overwritten. While it prints new posts to the console as they happen, it doesn’t immediately write every post to the ODS file.

The script uses a tiny caching system: new posts are temporarily kept in memory while running and only written to the spreadsheet periodically or when the script is stopped. The amount of memory used is minimal, so it won’t affect your system or performance. You’ll need Python 3.10 or newer and the praw and odfpy libraries, along with a JSON config file containing your Reddit API credentials (client_id, client_secret, user_agent).

This script is free to use, modify, and share. You can adapt it for your own projects or learning purposes without any restrictions.
