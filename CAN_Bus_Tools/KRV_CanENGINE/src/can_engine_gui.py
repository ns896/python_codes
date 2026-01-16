# can_engine_gui.py

import threading
import time
import curses
from collections import OrderedDict
from krv_comman.TUI.basic_tui import BasicTUI
from can_engine import KRV_CanEngine

class CANMessageStore:
    """Thread-safe store for CAN messages"""
    def __init__(self, database=None):
        self.messages = OrderedDict()  # Maintains insertion order
        self.lock = threading.Lock()
        self.total_count = 0
        self.database = database
    
    def update(self, message_data):
        """Update or add a message"""
        with self.lock:
            msg_id = message_data['message_id']
            if msg_id not in self.messages:
                # New message - add to end
                self.messages[msg_id] = {
                    'id': msg_id,
                    'name': self._get_message_name(msg_id, self.database),
                    'decoded': message_data.get('decoded'),
                    'raw_data': message_data.get('data'),
                    'dlc': message_data.get('dlc'),
                    'last_update': time.time(),
                    'count': 1,
                    'error': message_data.get('error')
                }
            else:
                # Update existing message in place
                self.messages[msg_id].update({
                    'decoded': message_data.get('decoded'),
                    'raw_data': message_data.get('data'),
                    'last_update': time.time(),
                    'count': self.messages[msg_id]['count'] + 1,
                    'error': message_data.get('error')
                })
            self.total_count += 1
    
    def get_all(self):
        """Get all messages (thread-safe)"""
        with self.lock:
            return list(self.messages.values())
    
    def _get_message_name(self, msg_id, database=None):
        # Try to get name from DBC, fallback to hex
        if database:
            try:
                message = database.get_message_by_frame_id(msg_id)
                return message.name
            except (KeyError, AttributeError):
                pass
        return f"0x{msg_id:03X}"

class CANMessageTUI(BasicTUI):
    def __init__(self, can_engine: KRV_CanEngine, filter_ids=None):
        super().__init__("KRV CAN Bus Monitor")
        self.can_engine = can_engine
        self.message_store = CANMessageStore(database=can_engine.database)
        self.filter_ids = set(filter_ids) if filter_ids else None
        self.receiver_thread = None
        self.running = True
        self.scroll_offset = 0
        self.selected_line = 0
        
    def start_can_receiver(self):
        """Start CAN message receiver in separate thread"""
        def receiver_loop():
            while self.running:
                try:
                    message = self.can_engine.next(timeout_value=0.1)
                    if message:
                        # Apply filter if specified
                        if self.filter_ids is None or message['message_id'] in self.filter_ids:
                            self.message_store.update(message)
                except Exception as e:
                    # Handle errors gracefully
                    pass
        
        self.receiver_thread = threading.Thread(target=receiver_loop, daemon=True)
        self.receiver_thread.start()
    
    def draw_content(self):
        """Draw the CAN message display"""
        height, width = self.stdscr.getmaxyx()
        
        # Header
        self._draw_header(width)
        
        # Message list
        self._draw_message_list(height, width)
        
        # Footer
        self._draw_footer(height, width)
    
    def _draw_header(self, width):
        """Draw header with stats"""
        header = f"CAN Port: {self.can_engine.can_port} | "
        header += f"Messages: {self.message_store.total_count} | "
        header += f"Unique IDs: {len(self.message_store.get_all())}"
        if self.filter_ids:
            header += f" | Filtered: {len(self.filter_ids)} IDs"
        
        self.stdscr.addstr(1, 2, header[:width-4], curses.color_pair(1))
        self.stdscr.addstr(2, 2, "-" * (width - 4))
    
    def _draw_message_list(self, height, width):
        """Draw the list of messages"""
        messages = self.message_store.get_all()
        start_y = 4
        max_lines = height - start_y - 3  # Leave space for footer
        
        # Apply scroll offset
        display_messages = messages[self.scroll_offset:self.scroll_offset + max_lines]
        
        for idx, msg in enumerate(display_messages):
            y_pos = start_y + idx
            if y_pos >= height - 3:
                break
            
            # Format message line
            line = self._format_message_line(msg, width - 4)
            color = curses.color_pair(3) if msg.get('error') else curses.color_pair(2)
            try:
                self.stdscr.addstr(y_pos, 2, line, color)
            except curses.error:
                pass  # Ignore if line is too long or out of bounds
    
    def _format_message_line(self, msg, max_width):
        """Format a single message for display"""
        # Format: ID | Name | Signals | Count | Time
        id_str = f"0x{msg['id']:03X}"
        name_str = msg.get('name', 'Unknown')[:20]  # Limit name length
        
        # Build fixed parts
        fixed_prefix = f"{id_str:8} | {name_str:20} | "
        count_str = f"#{msg['count']}"
        time_str = time.strftime("%H:%M:%S", time.localtime(msg['last_update']))
        fixed_suffix = f" | {count_str} | {time_str}"
        
        # Calculate available width for signals
        available_width = max_width - len(fixed_prefix) - len(fixed_suffix)
        
        if msg.get('decoded'):
            # Show ALL decoded signals
            signal_parts = [f"{k}={v}" for k, v in msg['decoded'].items()]
            signal_str = ", ".join(signal_parts)
            
            # If signals are too long, truncate but try to show as many as possible
            if len(signal_str) > available_width:
                # Try to fit as many complete signals as possible
                truncated = ""
                for signal in signal_parts:
                    test_str = truncated + (", " if truncated else "") + signal
                    if len(test_str) <= available_width - 3:  # Reserve space for "..."
                        truncated = test_str
                    else:
                        break
                signal_str = truncated + "..." if truncated else signal_str[:available_width-3] + "..."
        else:
            # Show raw data
            raw_data = msg.get('raw_data', '')
            signal_str = f"Raw: {raw_data[:available_width-10]}" if len(raw_data) > available_width - 10 else f"Raw: {raw_data}"
        
        line = f"{fixed_prefix}{signal_str}{fixed_suffix}"
        return line[:max_width]
    
    def _draw_footer(self, height, width):
        """Draw footer with controls"""
        footer_y = height - 2
        controls = "q=Quit | ↑↓=Scroll | f=Filter | r=Refresh | s=Sort"
        self.stdscr.addstr(footer_y, 2, controls[:width-4], curses.color_pair(4))
    
    def handle_input(self, key):
        """Handle keyboard input"""
        super().handle_input(key)
        
        if key == curses.KEY_UP:
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif key == curses.KEY_DOWN:
            messages = self.message_store.get_all()
            max_scroll = max(0, len(messages) - (self.stdscr.getmaxyx()[0] - 7))
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        elif key == ord('f') or key == ord('F'):
            # Toggle filter mode
            pass
        elif key == ord('r') or key == ord('R'):
            # Force refresh
            self.refresh()
    
    def run(self):
        """Main TUI loop - override BasicTUI.run()"""
        self.start_can_receiver()
        
        while self.running:
            self.refresh()
            time.sleep(0.1)  # Update UI 10 times per second
            
            try:
                key = self.stdscr.getch()
                if key != -1:  # -1 means no key pressed
                    self.handle_input(key)
            except curses.error:
                pass
        
        # Cleanup
        self.running = False
        if self.receiver_thread:
            self.receiver_thread.join(timeout=1)
        self.can_engine.can_receiver_destructor()