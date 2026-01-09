# Demo GIF Recording Instructions

This document provides instructions for creating the demo GIF for the README.

## Target Output

- **File**: `demo.gif`
- **Size**: < 5MB
- **Duration**: 30-60 seconds
- **Resolution**: 800x600 or similar

## Recording Tools

### Windows
- [ScreenToGif](https://www.screentogif.com/) (Recommended)
- [ShareX](https://getsharex.com/)

### macOS
- [Kap](https://getkap.co/) (Recommended)
- QuickTime Player + conversion

### Linux
- [Peek](https://github.com/phw/peek)
- [Gifcurry](https://github.com/lettier/gifcurry)

## Demo Script

Record the following workflow (approximate timing):

| Step | Action | Duration |
|------|--------|----------|
| 1 | Navigate to localhost:8000 | 2s |
| 2 | Click "Upload Video" button | 2s |
| 3 | Select sample video file | 3s |
| 4 | Watch progress bar (speed up 4x) | 10-15s |
| 5 | Show Events panel | 3s |
| 6 | Show Transcript panel | 3s |
| 7 | Type search query | 5s |
| 8 | Show search results | 3s |
| 9 | Click Export > Markdown | 3s |
| 10 | Show downloaded file | 2s |

**Total**: ~30-45 seconds

## Recording Tips

1. **Clean browser**: Use incognito/private window
2. **Resize window**: 800x600 for consistent size
3. **Cursor visible**: Ensure cursor is visible in recording
4. **Smooth movements**: Move mouse slowly and deliberately
5. **Pause on results**: Give viewers time to read

## Post-Processing

### Optimize with gifsicle

```bash
# Install gifsicle
# macOS: brew install gifsicle
# Ubuntu: sudo apt install gifsicle
# Windows: download from https://www.lcdf.org/gifsicle/

# Optimize the GIF
gifsicle -O3 --colors 128 demo.gif -o demo-optimized.gif

# If still too large, reduce colors further
gifsicle -O3 --colors 64 demo.gif -o demo-small.gif
```

### Online Alternatives

If command-line tools aren't available:
- [ezgif.com](https://ezgif.com/optimize) - Free online optimizer
- [gifcompressor.com](https://gifcompressor.com/)

## Placement

After creating `demo.gif`, place it in this directory:
```
docs/assets/demo.gif
```

Then update README.md:
```markdown
## See it in Action

![Lecture Mind Demo](docs/assets/demo.gif)
```

## Quality Checklist

### Pre-Recording
- [ ] Browser window resized to 800x600
- [ ] Clean browser state (incognito/private)
- [ ] Sample video ready (use any short MP4, 1-2 minutes)

### Post-Recording
- [ ] GIF file size is under 5MB
- [ ] Duration is 30-60 seconds
- [ ] Text is readable at 50% zoom
- [ ] Complete workflow shown (upload → results → search → export)
- [ ] No sensitive information visible

### Verification Steps
1. Open GIF in browser to verify playback
2. Preview in GitHub by pushing to a test branch
3. Check rendering on mobile device/emulator

---

*Note: This file can be deleted once demo.gif is created.*
