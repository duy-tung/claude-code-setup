# View Mode

Server-free viewing. Route by what the resolved path is:

## HTML file

Open directly in the default browser — the file is self-contained:

- macOS: `open "<path>"`
- Linux: `xdg-open "<path>"`
- Windows: `start "<path>"`

Report the file path and confirm the browser opened. If the open command fails (headless/remote session), report the absolute path so the user can open it themselves.

## Markdown file

1. Read the file and present it in the conversation: keep heading structure, render tables and code blocks as-is. For long documents (> ~300 lines), present the heading outline plus the section the user most likely cares about, then offer to show more.
2. For a browser-quality reading experience, offer to convert: generate a self-contained HTML rendering of the document (same rules as `--html` generation — read `html-design-guidelines.md` and `html-css-patterns.md`, include the mandatory theme toggle), save to `{plan_dir}/visuals/{filename-slug}.html` (or `plans/visuals/` when no active plan), and open it in the browser as above.

## Directory

1. List the contents (one level, names + sizes; note subdirectory counts).
2. Use `AskUserQuestion` to let the user pick a file, then view it per the rules above.

## Image file

Open with the OS default viewer using the same open commands as HTML files.

## Any other text/code file

Read and present in the conversation with the appropriate language context. Same long-file handling as markdown.
