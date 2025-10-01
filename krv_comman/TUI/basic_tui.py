# Basic TUI structure for reusable terminal user interface
import curses
from curses import wrapper

class BasicTUI:
    def __init__(self, title="Basic TUI"):
        self.title = title
        self.running = True
        self.stdscr = None
        
    def setup_curses(self, stdscr):
        """Initialize curses settings"""
        self.stdscr = stdscr
        self.stdscr.clear()
        self.stdscr.nodelay(True)  # Non-blocking mode
        curses.curs_set(0)  # Hide cursor
        
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    
    def draw_border(self):
        """Draw a border around the screen"""
        height, width = self.stdscr.getmaxyx()
        self.stdscr.border()
        self.stdscr.addstr(0, 2, f" {self.title} ", curses.color_pair(1))
    
    def draw_content(self):
        """Override this method in subclasses to draw specific content"""
        height, width = self.stdscr.getmaxyx()
        self.stdscr.addstr(height//2, width//2 - 10, "Basic TUI Framework", curses.color_pair(2))
        self.stdscr.addstr(height//2 + 2, width//2 - 15, "Press 'q' to quit", curses.color_pair(4))
    
    def handle_input(self, key):
        """Handle keyboard input - override in subclasses"""
        if key == ord('q') or key == ord('Q'):
            self.running = False
        elif key == curses.KEY_RESIZE:
            self.stdscr.clear()
            self.refresh()
    
    def refresh(self):
        """Refresh the display"""
        self.draw_border()
        self.draw_content()
        self.stdscr.refresh()
    
    def _tui_main(self, stdscr):
        """Internal method called by curses.wrapper"""
        try:
            self.setup_curses(stdscr)
            self.run()
        except KeyboardInterrupt:
            pass  # Handle Ctrl+C gracefully
    
    def run(self):
        """Main loop - override in subclasses for custom behavior"""
        while self.running:
            self.refresh()
            
            try:
                key = self.stdscr.getch()
                if key != -1:  # -1 means no key pressed
                    self.handle_input(key)
            except curses.error:
                pass  # Ignore curses errors
    
    def start(self):
        """Start the TUI application - call this instead of curses.wrapper"""
        try:
            wrapper(self._tui_main)
        except curses.error as e:
            print(f"Error initializing curses: {e}")
            print("Make sure you're running this in a proper terminal environment.")

def main():
    app = BasicTUI("Basic TUI Framework")
    app.start()

if __name__ == "__main__":
    main()