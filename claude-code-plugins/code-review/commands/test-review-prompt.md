---
description: Code review a pull request
---

Provide a code review for the given pull request.
If $ARGUMENTS exists review the branch / pull request $ARGUMENTS.

To do this, follow these steps precisely:

1. Summarise the STATUS of the pull request (but without doing a code review), and whether the code is already checked out (if CI environment variable is set)

   > Url, Title, Author, Created, Summary (summary of the intent of the PR from the description)

2. Find the pre-existing issues comment which contains `## Code Review`. It will be in the format within the <example_review_format> tags. Use this information in subsequent steps in order to dermine if an issue has already been resolved and should not be raised again.
   For each issue in the comment extract the following information

   - Path: Path of the file
   - Issue description
   - ThreadId: Graphql thread ID so it can be programmtically resolved
   - DatabaseId: Comment ID used to link to the comment
   - Status

3. Review the code by doing the following EXACT substeps and in order:
   3.1. Launch the following two agents in parallel :
   3.2.1 launch (uptick-code-review:code-review) to perform a code review of the changed files
   3.2.2 launch a general agent to determine if the issues in step 2 have been fixed by the most recent changes
   3.2. Launch an agent (uptick-code-review:false-positive-review) that takes the PR, issue description, and list of relevant rules from CLAUDE.md files (from step 3.1), and returns a score to indicate the agent's level of confidence for each issue is real or false positive.
   3.3. Filter out any issues with a score less than 80 (not critical). If there are no issues that meet this criteria, do not proceed.
   3.4. For each issue in 3.3 that isn't a duplicate or already resolved, create an inline comment using the (uptick-code-review:gh-inline-commenter) agent. Retrieve the Path/ThreadId/DatabaseId of each new comment so that it can be used in future steps

4. Use the combined issues from step 2 (if they exist) and any issues from steps 3 to create or update a comment on the pull request
   - Indicate and link to the commit that was reviewed
   - A line per issue in a table. For each column:
     - File: (Link to the underying file in this format: https://github.com/anthropics/claude-code/blob/1d54823877c4de72b2316a64032a54afc404e619/README.md#L13-L17) with the text being the path to the file
     - Description: A short 10-15 word max description of the issue
     - Status: One of [Resolved/Open/Ignored]. The link should be a link to the comment (databaseId) and with threadId of graphql comment embedded as a query parameter. eg: [Resolved](https://github.com/uptick/actions/pull/58#discussion_r2480207921?threadId=PRRC_kwDOGfhp7M6T1Pgx)
       - Use resolved if it has been fixed by the user (or manually resolved)
       - Use Open if it is still not fixed
       - Ignored if the user has left a comment indicating that it is not an issue
       - The databaze id will bein the format of `_rXXXXXXXXX`
   - Finally include a summary describing the quality of the pull request. If there are no issues; recommend it to be merged.

<example_review_format>

## Code Review

Reviewed changes as of < commit link >

Found <3> issues:

| File                                                                                                                            | Description                     | Status                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| scripts.py#123-123                                                                                                              | Command Injection Vulnerability | [Resolved](https://github.com/uptick/actions/pull/58#discussion_r2480207921?threadId=PRRC_kwDOGfhp7M6T1Pgx) |
| [scripts.py#123-123](https://github.com/anthropics/claude-code/blob/1d54823877c4de72b2316a64032a54afc404e619/README.md#L13-L17) | Command Injection Vulnerability | [Open](https://github.com/uptick/actions/pull/58#discussion_r2480207921?threadId=PRRC_kwDOGfhp7M6T1Pgx)     |
| [scripts.py#123-123](https://github.com/anthropics/claude-code/blob/1d54823877c4de72b2316a64032a54afc404e619/README.md#L13-L17) | Command Injection Vulnerability | [Ignored](https://github.com/uptick/actions/pull/58#discussion_r2480207921?threadId=PRRC_kwDOGfhp7M6T1Pgx)  |

<summary of review>

🤖 Generated with [Claude Code](https://claude.ai/code)
</example_review_format>

Notes:

- Use `gh` to interact with Github (eg. to fetch a pull request, or to create inline comments), rather than web fetch
- Make a todo list first
- You must cite and link each bug (eg. if referring to a CLAUDE.md, you must link it)
- Only ever leave 1 top level comment; update it and never make a new one.
- You must never make more then 1 top level comment. Do not post if you cannot.
