# footwork

A HEMA footwork caller. It plays the instructor, voicing random "forward" or
"backward" calls so you step in the called direction; shorten the gap between
calls as your reaction improves. Two modes:

- **Calls**: N random calls with a fixed gap between them.
- **Steps + lunge**: each rep is a random number of steps (between a min and a
  max you set, equal for a fixed count) followed by a beep, on which you lunge;
  repeated N times with a configurable rest after each lunge.

Run it with:

```bash
htools footwork
```

Notes:
- it opens a local browser page by default; use `--no-browser` for the URL only
- pick a mode, set its numbers, then press Start (or Space); there is a 3 second
  "ready" lead-in before the first call
- the voice is the browser's built-in speech synthesis and the beep is a Web Audio
  oscillator, so no extra dependencies;
  pick any installed English voice from the dropdown (the choice is remembered)
- for a much smoother voice, install an "Enhanced" or "Premium" English voice in
  macOS System Settings → Accessibility → Spoken Content → System Voice; it shows
  up in the dropdown automatically
- the server only serves the page; all logic runs in the browser
