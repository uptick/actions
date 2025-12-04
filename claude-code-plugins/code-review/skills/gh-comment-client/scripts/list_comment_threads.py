#!/usr/bin/env python3
import sys
import json
import subprocess

def main():
    if len(sys.argv) != 3:
        print("Usage: list_comment_threads.py <owner/repo> <pr_number>")
        sys.exit(1)

    owner_repo = sys.argv[1]
    pr_number = sys.argv[2]
    owner, repo = owner_repo.split('/')

    query = """
 query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              isOutdated
              path
              line
              resolvedBy {
                login
              }
              comments(first: 100) {
                nodes {
                  id
                  fullDatabaseId
                  createdAt
                  body
                  path
                  author {
                    login
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    result = subprocess.run(
        ['gh', 'api', 'graphql', '-f', f'query={query}', '-f', f'owner={owner}', '-f', f'repo={repo}', '-F', f'pr={pr_number}'],
        capture_output=True,
        text=True
    )

    data = json.loads(result.stdout)

    threads = data['data']['repository']['pullRequest']['reviewThreads']['nodes']

    # Filter for Claude's comments
    claude_threads = [
        thread for thread in threads
        if any(comment['author']['login'] == 'claude' for comment in thread['comments']['nodes'])
    ]

    for thread in claude_threads:
        print("---")
        print(f"Thread ID: {thread['id']}")
        print(f"Path: {thread['path']}")
        if thread['isOutdated']:
            print(f"IsOutdated: {thread['isOutdated']}")
        else:
            print(f"Line: {thread['line']}")
        print(f"Resolved By: {thread['resolvedBy']['login'] if thread['resolvedBy'] else 'Not resolved'}")
        print(f"Comments: {len(thread['comments']['nodes'])}")
        for comment in thread['comments']['nodes']:
            if comment['author']['login'] == 'claude':
                print(f"Comment ID: {comment['id']}")
                print(f"Issue: |\n{comment['body']}")
            else:
                print(f"Comment Author: {comment['author']['login']}")
                print(f"Comment: {comment['body']}")


if __name__ == '__main__':
    main()
