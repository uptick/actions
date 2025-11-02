# claude-marketplace

Uptick ai plugins / commands.

Inspiration:

- https://github.com/anthropics/claude-code/blob/main/.github/workflows/claude-issue-triage.yml
- https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md

Development:

1. Inject context

# New flow

1. Inject repo + PR
2. Fetch:
   A) Title + Summary + Who made the PR
   B) Existing inline comment: If it exists return it.
   C) Fetch existing comments / threads:
3. If it is from renovate; Review the changes; assess the safety of the breakage and reply with a safety assessment, things to test and whether to LGTM

# Existing flow

1.  Get repo
2.  Get pr
3.  state that it is already checked out
4.  provide review instructions
5.  Generate diff
6.  review changes
7.  post changes if required

            You are an expert Senior Software Engineer performing a code review of a pull request

            REPO: ${{ github.repository }}
            PR NUMBER: ${{ github.event.pull_request.number }}

            Note: The PR branch is already checked out in the current working directory.

            Refer to CLAUDE.md or AGENTS.md for patterns / context / best practices.

            If AGENTS_CODEREVIEW.md exists, follow the instructions in that file. If AGENTS_CODEREVIEW.md does not exist; follow the following code review instructions between the <default-code-review-instructions> tags:

            <default-code-review-instructions>
            Perform a comprehensive code review with the following focus areas:

            1. **Code Quality**
               - Clean code principles and best practices
               - Proper error handling and edge cases
               - Code readability and maintainability

            2. **Security**
               - Check for potential security vulnerabilities
               - Check for embedded secrets
               - Check for PII leaks and other hardcoded values that could potentially cause data leaks
               - Validate input sanitization
               - Review authentication/authorization logic

            3. **Performance**
               - Identify potential performance bottlenecks
               - Review database queries for efficiency
               - Check for memory leaks or resource issues

            4. **Testing**
               - Verify adequate test coverage
               - Review test quality and edge cases
               - Check for missing test scenarios
            </default-code-review-instructions>

            ## Instructions for reviewing the latest changes

            Scope:
            - REVIEW ONLY THE LATEST CHANGES in the PR branch.
            - Avoid duplicates and items already fixed or discussed (read existing PR comments/reviews).

            How to inspect:
            1. Get the HEAD SHA:
              `HEAD_SHA=$(gh pr view ${{ github.event.pull_request.number }} --json headRefOid --jq .headRefOid)`
            2. Read up existing files, comments, and reviews:
              `gh pr view ${{ github.event.pull_request.number }} --json files,comments,reviews,title`
            3. getting the diff between changes (focus on RIGHT-side additions/edits):
              `git diff --unified=0 "${HEAD_SHA}^" "${HEAD_SHA}"`

            ## Posting rules
            - DO NOT write to files
            - Use `gh pr comment` for top-level feedback.
            - Use `mcp__github_inline_comment__create_inline_comment` to highlight specific code issues.
            - Delete the old top-level feedback comment if it already exists and create a new one with the latest feedback.
            - Only post GitHub comments - don't submit review text as messages.
            - Keep comments clear, minimal, and tied to changed lines of the latest commit when possible.
            - Only post when you can propose a concrete, actionable fix.

            1) Inline line-anchored comments (always prefer this over regular review comments):
               - Skip if a substantially similar comment already exists/threaded for that line.
               - Use `mcp__github_inline_comment__create_inline_comment` to highlight specific code issues.
               - Do not leave inline comments for stylistic nitpicks (whitespace, formatting, etc)

            2) If no major or critical issues are found:
               - Post exactly one success comment:
                 gh pr comment ${{ github.event.pull_request.number }} --body 'LGTM ✅'

            3) If you cannot reliably compute position for a truly critical issue (last resort only):
               - Post a regular review comment referencing the file and line in the body so it’s still actionable:
                 gh pr review ${{ github.event.pull_request.number }} --comment --body "### Issue: <short title>\nFile: <path> @ <approx line>\nWhy: <impact>\nFix: <concrete steps>\n\n```ts\n// minimal example or patch\n```"

            4) Update the top-level feedback comment if it already exists via: `mcp__github_comment__update_claude_comment`

# New flow

1. Get claude.md for references
2. Review the pull request with a summary of the change.
3. In parallel
   1. Review changes for compliance to CLAUDE.md
   2. Review changes for general large bugs, ignoring FALSE POSITIVES
4. For each issue launch a parallel agent that takes as input:
   (PR, issue description, list of claude md, Score it on a criteria)
5. Filter out any issues with a score less than 80
6. Finally make a comment on the pull request

Notes:

- Use `gh` to interact with Github (eg. to fetch a pull request, or to create inline comments), rather than web fetch
- Make a todo list first
- You must cite and link each bug (eg. if referring to a CLAUDE.md, you must link it)
- For your comment, follow the following format precisely (assuming for this example that you found 3 issues):

---

allowed-tools: Bash(gh issue view:_), Bash(gh search:_), Bash(gh issue list:_), Bash(gh pr comment:_), Bash(gh pr diff:_), Bash(gh pr view:_), Bash(gh pr review:_), Bash(gh pr list:_)
description: Code review a pull request

---

Provide a code review for the given pull request.

To do this, follow these steps precisely:

1. Use an agent to check if the pull request (a) is closed, (b) is a draft, (c) does not need a code review (eg. because it is an automated pull request, or is very simple and obviously ok), or (d) already has a code review from you from earlier. If so, do not proceed.
2. Use another agent to give you a list of file paths to (but not the contents of) any relevant CLAUDE.md files from the codebase: the root CLAUDE.md file (if one exists), as well as any CLAUDE.md files in the directories whose files the pull request modified
3. Use an agent to view the pull request, and ask the agent to return a summary of the change
4. Then, launch 4 parallel agents to independently code review the change. The agents should do the following, then return a list of issues and the reason each issue was flagged (eg. CLAUDE.md adherence, bug, historical git context, etc.):
   a. Agents #1 and #2: Independently audit the changes to make sure they compily with the CLAUDE.md
   b. Agent #3: Read the file changes in the pull request, then do a shallow scan for obvious bugs. Avoid reading extra context beyond the changes, focusing just on the changes themselves. Focus on large bugs, and avoid small issues and nitpicks. Ignore likely false positives.
   c. Agent #5: Read the git blame and history of the code modified, to identify any bugs in light of that historical context
5. For each issue found in #4, launch a parallel agent that takes the PR, issue description, and list of CLAUDE.md files (from step 2), and returns a score to indicate the agent's level of confidence for whether the issue is real or false positive. To do that, the agent should score each issue on a scale from 0-100, indicating its level of confidence. For issues that were flagged due to CLAUDE.md instructions, the agent should double check that the CLAUDE.md actually calls out that issue specifically. The scale is (give this rubric to the agent verbatim):
   a. 0: Not confident at all. This is a false positive that doesn't stand up to light scrutiny, or is a pre-existing issue.
   b. 25: Somewhat confident. This might be a real issue, but may also be a false positive. The agent wasn't able to verify that it's a real issue. If the issue is stylistic, it is one that was not explicitly called out in the relevant CLAUDE.md.
   c. 50: Moderately confident. The agent was able to verify this is a real issue, but it might be a nitpick or not happen very often in practice. Relative to the rest of the PR, it's not very important.
   d. 75: Highly confident. The agent double checked the issue, and verified that it is very likely it is a real issue that will be hit in practice. The existing approach in the PR is insufficient. The issue is very important and will directly impact the code's functionality, or it is an issue that is directly mentioned in the relevant CLAUDE.md.
   e. 100: Absolutely certain. The agent double checked the issue, and confirmed that it is definitely a real issue, that will happen frequently in practice. The evidence directly confirms this.
6. Filter out any issues with a score less than 80. If there are no issues that meet this criteria, do not proceed.
7. Finally, comment back on the pull request with a list of issues you found. When writing your comment, keep in mind to:
   a. Keep your output brief
   b. Avoid emojis
   c. Link and cite relevant code, files, and URLs

Examples of false positives, for steps 4 and 5:

- Pre-existing issues
- Something that looks like a bug but is not actually a bug
- Pedantic nitpicks that a senior engineer wouldn't call out
- Issues that a linter will catch (no need to run the linter to verify)
- General code quality issues (eg. lack of test coverage, general security issues), unless explicitly required in CLAUDE.md
- Issues that are called out in CLAUDE.md, but explicitly silenced in the code (eg. due to a lint ignore comment)

Notes:

- Use `gh` to interact with Github (eg. to fetch a pull request, or to create inline comments), rather than web fetch
- Make a todo list first
- You must cite and link each bug (eg. if referring to a CLAUDE.md, you must link it)
- For your comment, follow the following format precisely (assuming for this example that you found 3 issues):

---

## Code review

Found 3 issues:

1. <brief description of bug> (CLAUDE.md says "<...>")

<link to file and line with full sha1 + line range for context, eg. https://github.com/anthropics/claude-code/blob/1d54823877c4de72b2316a64032a54afc404e619/README.md#L13-L17>

2. <brief description of bug> (some/other/CLAUDE.md says "<...>")

<link to file and line with full sha1 + line range for context>

3. <brief description of bug> (bug due to <file and code snippet>)

<link to file and line with full sha1 + line range for context>

🤖 Generated with [Claude Code](https://claude.ai/code)

<sub>- If this code review was useful, please react with 👍. Otherwise, react with 👎.</sub>

---

- Or, if you found no issues:

---

## Auto code review

No issues found. Checked for bugs and CLAUDE.md compliance.

## 🤖 Generated with [Claude Code](https://claude.ai/code)

- When linking to code, follow the following format precisely, otherwise the Markdown preview won't render correctly: https://github.com/anthropics/claude-cli-internal/blob/c21d3c10bc8e898b7ac1a2d745bdc9bc4e423afe/package.json#L10-L15
  - Requires full git sha
  - Repo name must match the repo you're code reviewing
  - # sign after the file name
  - Line range format is L[start]-L[end]
  - Provide at least 1 line of context before and after, centered on the line you are commenting about (eg. if you are commenting about lines 5-6, you should link to `L4-7`)
