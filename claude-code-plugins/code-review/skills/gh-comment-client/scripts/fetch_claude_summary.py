#!/usr/bin/env python3
"""
Fetch and parse Claude Code Review summary comments from GitHub PRs.

This script finds PR comments starting with "## Code Review" and optionally
parses the embedded issue table.
"""
import sys
import json
import subprocess
import re
from urllib.parse import urlparse, parse_qs


def extract_thread_id(url):
    """
    Extract the threadId query parameter from a GitHub comment URL.

    Args:
        url: GitHub comment URL, e.g. https://github.com/org/repo/pull/1#discussion_r123?threadId=PRRC_xxx

    Returns:
        threadId string or None if not found
    """
    if not url or url == '-':
        return None

    # Extract query parameters
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    return params.get('threadId', [None])[0]


def extract_file_info(file_cell):
    """
    Extract file path and URL from the File column cell.

    Args:
        file_cell: Markdown cell content, e.g. "[scripts.py#123-123](url)" or "scripts.py#123-123"

    Returns:
        dict with 'path', 'lines', 'url' keys
    """
    # Match markdown link: [text](url)
    link_match = re.match(r'\[(.*?)\]\((.*?)\)', file_cell.strip())

    if link_match:
        text = link_match.group(1)
        url = link_match.group(2)
    else:
        text = file_cell.strip()
        url = None

    # Parse file path and line numbers
    # Format: path/to/file.py#123-456 or path/to/file.py#123
    path_match = re.match(r'(.+?)#(\w+(?:-\w+)?)$', text)
    breakpoint()

    if path_match:
        path = path_match.group(1)
        lines = path_match.group(2) if path_match.group(2) else None
    else:
        path = text
        lines = None

    return {
        'path': path,
        'lines': lines,
        'url': url
    }


def extract_status_info(status_cell):
    """
    Extract status and threadId from the Status column cell.

    Args:
        status_cell: Markdown cell content, e.g. "[Resolved](url?threadId=xxx)"

    Returns:
        dict with 'status', 'url', 'thread_id' keys
    """
    # Match markdown link: [status](url)
    link_match = re.match(r'\[(.*?)\]\((.*?)\)', status_cell.strip())

    if link_match:
        status = link_match.group(1)
        url = link_match.group(2)
        thread_id = extract_thread_id(url)
    else:
        status = status_cell.strip()
        url = None
        thread_id = None

    return {
        'status': status,
        'url': url,
        'thread_id': thread_id
    }


def parse_review_table(table_text):
    """
    Parse the GitHub markdown table from a Code Review comment.

    Expected format:
    | File | Description | Status |
    | --- | --- | --- |
    | [path#lines](url) | Issue description | [Status](url?threadId=xxx) |

    Args:
        table_text: Markdown text containing the table

    Returns:
        List of dicts with parsed issue data
    """
    lines = table_text.strip().split('\n')

    # Find table lines (starting with |)
    table_lines = [line.strip() for line in lines if line.strip().startswith('|')]

    if len(table_lines) < 3:  # Need header, separator, and at least one data row
        return []

    # Parse header to identify columns
    header = table_lines[0]
    headers = [h.strip() for h in header.split('|')[1:-1]]

    # Skip separator line (index 1)
    # Parse data rows (index 2+)
    issues = []
    for line in table_lines[2:]:
        cells = [c.strip() for c in line.split('|')[1:-1]]

        if len(cells) != len(headers):
            continue

        file_text, description_text, status_text = cells

        # Extract structured data
        issue = {}

        file_info = extract_file_info(file_text)
        issue.update(file_info)

        issue['description'] = description_text.strip()
        issue.update(extract_status_info(status_text))

        issues.append(issue)

    return issues


def fetch_review_comment(owner, repo, pr_number):
    """
    Fetch PR comments and find the one starting with "## Code Review".

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name
        pr_number: Pull request number

    Returns:
        dict with comment data or None if not found
    """
    query = """
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      comments(first: 100) {
        nodes {
          id
          databaseId
          author {
            login
          }
          body
          createdAt
          updatedAt
        }
      }
    }
  }
}
"""

    result = subprocess.run(
        [
            'gh', 'api', 'graphql',
            '-f', f'query={query}',
            '-f', f'owner={owner}',
            '-f', f'repo={repo}',
            '-F', f'pr={pr_number}'
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error fetching comments: {result.stderr}", file=sys.stderr)
        return None

    data = json.loads(result.stdout)
    comments = data['data']['repository']['pullRequest']['comments']['nodes']

    # Find comment starting with "## Code Review"
    for comment in comments:
        if comment['body'].strip().startswith('## Code Review'):
            return comment

    return None


def main():
    if len(sys.argv) < 3:
        print("Usage: fetch_claude_summary.py <owner/repo> <pr_number> [--parse-table]")
        sys.exit(1)

    owner_repo = sys.argv[1]
    pr_number = sys.argv[2]
    parse_table = '--parse-table' in sys.argv

    try:
        owner, repo = owner_repo.split('/')
    except ValueError:
        print("Error: owner/repo must be in format 'owner/repo'", file=sys.stderr)
        sys.exit(1)

    # Fetch the review comment
    comment = fetch_review_comment(owner, repo, pr_number)

    if not comment:
        print("No Code Review comment found.")
        sys.exit(0)

    # Print comment metadata
    print("=== Code Review Comment ===")
    print(f"Author: {comment['author']['login']}")
    print(f"Created: {comment['createdAt']}")
    print(f"Updated: {comment['updatedAt']}")
    print(f"Comment ID: {comment['databaseId']}")
    print()

    if parse_table:
        # Extract and parse the table
        body = comment['body']

        # Find the table in the body
        # Table starts after "Found X issues:" and ends before the summary
        issues = parse_review_table(body)

        if issues:
            print(f"Found {len(issues)} issue(s) in table:")
            print()

            for i, issue in enumerate(issues, 1):
                print(f"Issue #{i}:")
                print(f"  File: {issue.get('path', 'N/A')}")
                if issue.get('lines'):
                    print(f"  Lines: {issue['lines']}")
                if issue.get('url'):
                    print(f"  File URL: {issue['url']}")
                print(f"  Description: {issue.get('description', 'N/A')}")
                print(f"  Status: {issue.get('status', 'N/A')}")
                if issue.get('thread_id'):
                    print(f"  Thread ID: {issue['thread_id']}")
                if issue.get('url'):
                    print(f"  Comment URL: {issue['url']}")
                print()
        else:
            print("No issues found in table.")
    else:
        # Just print the comment body
        print("Comment Body:")
        print(comment['body'])


if __name__ == '__main__':
    main()
