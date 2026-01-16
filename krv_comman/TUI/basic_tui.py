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
    
    def get_header_text(self):
        """Override this method in subclasses to return header text"""
        return None
    
    def get_footer_text(self):
        """Override this method in subclasses to return footer text"""
        return None
    
    def draw_header(self):
        """Draw header section - override get_header_text() to customize"""
        header_text = self.get_header_text()
        if header_text:
            height, width = self.stdscr.getmaxyx()
            # Draw header on line 1, separator on line 2
            try:
                self.stdscr.addstr(1, 2, header_text[:width-4], curses.color_pair(1))
                self.stdscr.addstr(2, 2, "-" * (width - 4))
            except curses.error:
                pass  # Ignore if out of bounds
    
    def draw_footer(self):
        """Draw footer section - override get_footer_text() to customize"""
        footer_text = self.get_footer_text()
        if footer_text:
            height, width = self.stdscr.getmaxyx()
            footer_y = height - 2
            try:
                self.stdscr.addstr(footer_y, 2, footer_text[:width-4], curses.color_pair(4))
            except curses.error:
                pass  # Ignore if out of bounds
    
    def get_content_area(self):
        """Get the available area for content (y_start, y_end, width)"""
        height, width = self.stdscr.getmaxyx()
        y_start = 4 if self.get_header_text() else 1
        y_end = height - 3 if self.get_footer_text() else height - 1
        return y_start, y_end, width
    
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
        self.draw_header()
        self.draw_content()
        self.draw_footer()
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