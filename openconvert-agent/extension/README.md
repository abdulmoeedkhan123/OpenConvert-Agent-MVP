# OpenConvert Agent browser extension scaffold

This folder contains a minimal browser extension wrapper for the local OpenConvert Agent desktop app.

## Notes
- Browser extensions cannot safely access arbitrary local files in a universal way.
- This scaffold is intended as an installable UI wrapper and a reminder to launch the desktop app.
- For real end-user operations, use the desktop app and CLI entry points.

## Load in Chrome or Edge
1. Open `chrome://extensions`.
2. Turn on **Developer mode**.
3. Choose **Load unpacked**.
4. Select this folder.

## Useful next step
Replace the placeholder `chrome.tabs.create` logic with a real local app launcher flow when you want a dedicated browser-to-desktop bridge.
