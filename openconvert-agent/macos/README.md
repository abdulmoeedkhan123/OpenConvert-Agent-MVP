# macOS app and quick action setup (MVP)

## Finder Quick Action
1. Install the project into a virtual environment and verify `openconvert convert ...` works.
2. Make the script executable: `chmod +x macos/finder_quick_action.sh`.
3. Open Automator and create a new **Quick Action**.
4. Set “Workflow receives current” to **files or folders** in **Finder**.
5. Add **Run Shell Script**, choose `/bin/zsh`, and set “Pass input” to **as arguments**.
6. Paste the contents of `finder_quick_action.sh` into the action.
7. Save as **OpenConvert**.
8. In Finder, right-click a supported file and choose Quick Actions → OpenConvert.

Notes:
- Automator's environment PATH may not include your Python virtual environment. If needed, replace `openconvert` in the script with the absolute path to `.venv/bin/openconvert`.
- This MVP uses a fixed default mapping: images → WebP; office/text documents → PDF. The desktop app provides explicit target selection.
- For a distributable consumer product, prefer a signed app bundle with a robust Quick Action installation experience and tested launch environment.

## App bundle scaffold
A minimal `.app` bundle is included at `macos/OpenConvert Agent.app`.

```bash
open "macos/OpenConvert Agent.app"
```

This is a local launcher scaffold, not a notarized production-grade app.
