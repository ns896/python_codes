#!/usr/bin/env python3
"""
Example usage of BasicTUI framework
This demonstrates how to create a custom TUI application
"""

import curses
from basic_tui import BasicTUI

class ExampleTUI(BasicTUI):
    def __init__(self):
        super().__init__("Example TUI Application")
        self.counter = 0
        self.message = "Hello from Example TUI!"
        
    def draw_content(self):
        """Override to draw custom content"""
        height, width = self.stdscr.getmaxyx()
        
        # Title
        title = "Example TUI Application"
        self.stdscr.addstr(2, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
        # Dynamic content
        self.stdscr.addstr(height//2 - 2, width//2 - len(self.message)//2, self.message, curses.color_pair(1))
        
        # Counter display
        counter_text = f"Counter: {self.counter}"
        self.stdscr.addstr(height//2, width//2 - len(counter_text)//2, counter_text, curses.color_pair(3))
        
        # Instructions
        instructions = [
            "Press 'i' to increment counter",
            "Press 'd' to decrement counter", 
            "Press 'c' to clear counter",
            "Press 'm' to change message",
            "Press 'q' to quit"
        ]
        
        y_start = height//2 + 3
        for i, instruction in enumerate(instructions):
            self.stdscr.addstr(y_start + i, 5, instruction, curses.color_pair(4))
    
    def handle_input(self, key):
        """Handle custom keyboard input"""
        super().handle_input(key)  # Call parent for 'q' and resize
        
        if key == ord('i') or key == ord('I'):
            self.counter += 1
        elif key == ord('d') or key == ord('D'):
            self.counter -= 1
        elif key == ord('c') or key == ord('C'):
            self.counter = 0
        elif key == ord('m') or key == ord('M'):
            self.message = "Message changed!" if self.message == "Hello from Example TUI!" else "Hello from Example TUI!"

def main():
    app = ExampleTUI()
    app.start()

if __name__ == "__main__":
    main()
