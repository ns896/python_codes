# Remote Interactive Plots via SSH Tunnel

Serve and interact with Plotly HTML plots saved on a remote machine (`shinobi`) through an SSH tunnel.

---

## The Two Commands

**On the remote machine (shinobi) — start the file server:**
```bash
python3 -m http.server 8988
```

**On your local machine — open the tunnel:**
```bash
ssh -L 8988:localhost:8988 nsingh@shinobi.local
```

Then open your browser to:
```
http://localhost:8988
```

You'll see a file browser. Click any `.html` plot file to open it and interact with it fully (zoom, hover, pan, etc.).

---

## Python / Plotly Side — Saving the Plots

To save a Plotly figure as a standalone interactive HTML file on shinobi:

```python
import plotly.express as px  # or plotly.graph_objects as go

fig = px.scatter(df, x="x_col", y="y_col", title="My Plot")

# Save as self-contained HTML (no internet needed to view)
fig.write_html("my_plot.html")
```

Run `python3 -m http.server 8988` from the same directory where the `.html` files live.

### Useful `write_html` options

```python
fig.write_html(
    "my_plot.html",
    include_plotlyjs="cdn",   # smaller file; needs internet to view
    # include_plotlyjs=True   # default: fully self-contained (~3 MB)
    full_html=True,           # default; set False to embed in another page
)
```

---

## How It Works

```
Browser (localhost:8988)
        |
   SSH tunnel (local port 8988 → shinobi port 8988)
        |
   python3 -m http.server 8988  (running on shinobi)
        |
   HTML plot files on shinobi's disk
```

---

## Tips & Gotchas

- Run `python3 -m http.server 8988` **from the folder containing your `.html` files**, or navigate into it first.
- The SSH tunnel command keeps the tunnel open as long as the terminal stays open. Use `tmux` or `screen` on shinobi to keep the server running if you disconnect.
- If port 8988 is already in use, pick any free port (e.g. `8989`) — just keep both numbers the same in both commands.
- `shinobi.local` uses mDNS (Bonjour). If it doesn't resolve, try the machine's IP address instead.
