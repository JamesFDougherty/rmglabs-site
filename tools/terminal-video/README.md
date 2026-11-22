# Terminal clip generator

Makes the short "see it run" clips used in blog posts that show PowerShell or PowerCLI scripts.

    python3 tools/terminal-video/make_video.py tools/terminal-video/scenarios/<name>.json blog/videos/<name>.mp4

Writes `<name>.mp4` and a poster `<name>.jpg`. Needs python3 with Playwright (Chromium) and ffmpeg.

The clips are scripted replays, not recordings of a real vCenter. They always carry a
"SAMPLE OUTPUT | simulated lab data" badge, use placeholder names (example.local) and never
real hostnames, usernames or data. Timings and counts in a scenario are illustrative.

Scenario steps: `prompt`, `type`, `wait`, `dialog` (credential prompt), `table` (formatted like
Format-Table -AutoSize), `out` (plain lines), and for a GUI clip `form`, `msgbox`, `formclose`.
Add `cap` to a step to show a caption under the window. See the existing files in `scenarios/`.
