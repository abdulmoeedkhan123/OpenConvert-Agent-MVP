#!/bin/zsh
# MVP Finder Quick Action script. Receives selected file paths as arguments.
# Recommended Automator setup: Quick Action receives "files or folders" in Finder,
# add "Run Shell Script", shell=/bin/zsh, pass input="as arguments".
set -u

if ! command -v openconvert >/dev/null 2>&1; then
  osascript -e 'display alert "OpenConvert not installed" message "Install OpenConvert and ensure its command is available in PATH."'
  exit 1
fi

failures=0
for file in "$@"; do
  [[ -f "$file" ]] || continue
  ext="${file##*.}"
  ext="${ext:l}"
  case "$ext" in
    png|jpg|jpeg|webp|bmp|tif|tiff)
      target="webp"
      ;;
    doc|docx|odt|rtf|txt|html|htm|odp|ppt|pptx|ods|xls|xlsx)
      target="pdf"
      ;;
    *)
      osascript -e "display notification \"Unsupported file: ${file:t}\" with title \"OpenConvert\""
      failures=1
      continue
      ;;
  esac
  if ! openconvert convert "$file" --to "$target"; then
    failures=1
  fi
done

if [[ "$failures" -eq 0 ]]; then
  osascript -e 'display notification "Selected files processed." with title "OpenConvert"'
else
  osascript -e 'display notification "Some files could not be converted. Check Terminal output." with title "OpenConvert"'
fi
exit "$failures"
