# Author: Navneet Singh
# MobilEye_DataVisualizer.py
# Plotly Dash app to visualize the data from the MobilEye sensor.

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import callback_context
import asyncio
import threading
import time
import numpy as np
from typing import Dict, List, Optional
from collections import deque
import json
from datetime import datetime
import webbrowser
import socket


class MobilEyeVisualizer:
    """Real-time MobilEye data visualization using Plotly Dash"""
    
    def __init__(self, host='0.0.0.0', port=8050, max_data_points=100):
        """
        Initialize the visualizer
        
        Args:
            host: Host address (0.0.0.0 for remote access)
            port: Port number for the web server
            max_data_points: Maximum number of data points to store
        """
        self.host = host
        self.port = port
        self.max_data_points = max_data_points
        
        # Control flags
        self.is_running = False
        self.update_interval = 50  # milliseconds - much faster updates (20 FPS)
        
        self.enable_obstacle_detection = False  

        # Data storage
        self.lane_data_history = {
            'left': deque(maxlen=max_data_points),
            'right': deque(maxlen=max_data_points)
        }
        self.obstacle_data_history = deque(maxlen=max_data_points)
        self.timestamps = deque(maxlen=max_data_points)
        
        # Performance optimization: Cache for plot data
        self._plot_cache = {}
        self._last_update_time = 0
        
        # Initialize Dash app
        self.app = dash.Dash(__name__)
        self.setup_dash_app()
        
    def setup_dash_app(self):
        """Setup the Dash application layout"""
        self.app.layout = html.Div([
            html.H1("MobilEye CAN Data Visualization", 
                   style={'textAlign': 'center', 'color': '#2c3e50'}),
            
            # Control panel
            html.Div([
                html.Button('Start Visualization', id='start-btn', n_clicks=0),
                html.Button('Stop Visualization', id='stop-btn', n_clicks=0),
                html.Button('Clear Data', id='clear-btn', n_clicks=0),
                html.Button('Enable Obstacle Detection', id='enable-obstacle-btn', n_clicks=0),
                html.Button('Disable Obstacle Detection', id='disable-obstacle-btn', n_clicks=0),
                html.Div(id='status-display', style={'marginTop': '10px'})
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),
            
            # Lane visualization
            html.Div([
                html.H3("Lane Detection Visualization"),
                dcc.Graph(id='lane-plot', style={'height': '500px'}),
                dcc.Interval(
                    id='lane-interval',
                    interval=self.update_interval,
                    n_intervals=0,
                    disabled=True
                )
            ]),
            
            # Lane parameters
            html.Div([
                html.H3("Lane Parameters"),
                html.Div([
                    html.Div([
                        html.H4("Left Lane"),
                        html.Div(id='left-lane-params')
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    html.Div([
                        html.H4("Right Lane"),
                        html.Div(id='right-lane-params')
                    ], style={'width': '50%', 'display': 'inline-block'})
                ])
            ]),

            # Data table
            html.Div([
                html.H3("Latest Data"),
                html.Div(id='data-table')
            ]),
            # Footer
            html.Footer([
                html.Hr(),
                html.P(
                    "Created by Navneet Singh",
                    style={
                        'textAlign': 'center',
                        'color': '#7f8c8d',
                        'padding': '20px',
                        'marginTop': '40px',
                        'borderTop': '1px solid #eee'
                    }
                )
            ])
        ])
        
        # Setup callbacks
        self.setup_callbacks()
        
    def setup_callbacks(self):
        """Setup Dash callbacks for interactivity"""
        
        @self.app.callback(
            [Output('lane-plot', 'figure'),
             Output('left-lane-params', 'children'),
             Output('right-lane-params', 'children')],
            [Input('lane-interval', 'n_intervals')]
        )
        def update_lane_plot(n):
            return self.create_lane_plot(), self.get_lane_params('left'), self.get_lane_params('right')
        

        
        @self.app.callback(
            Output('data-table', 'children'),
            [Input('lane-interval', 'n_intervals')]
        )
        def update_data_table(n):
            return self.create_data_table()
        
        @self.app.callback(
            [Output('lane-interval', 'disabled'),
             Output('status-display', 'children')],
            [Input('start-btn', 'n_clicks'),
             Input('stop-btn', 'n_clicks'),
             Input('clear-btn', 'n_clicks'),
             Input('enable-obstacle-btn', 'n_clicks'),
             Input('disable-obstacle-btn', 'n_clicks')]
        )
        def control_visualization(start_clicks, stop_clicks, clear_clicks, enable_obstacle_clicks, disable_obstacle_clicks):
            ctx = callback_context
            if not ctx.triggered:
                return True, "Ready to start"
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'start-btn':
                self.is_running = True
                return False, "Visualization running..."
            elif button_id == 'stop-btn':
                self.is_running = False
                return True, "Visualization stopped"
            elif button_id == 'clear-btn':
                self.clear_data()
                return True, "Data cleared"
            elif button_id == 'enable-obstacle-btn':
                self.enable_obstacle_detection = True
                return False, "Obstacle detection enabled - obstacles overlaid on lane plot"
            elif button_id == 'disable-obstacle-btn':
                self.enable_obstacle_detection = False
                return False, "Obstacle detection disabled"
            return True, "Ready to start"
    
    def create_lane_plot(self):
        """Create the lane visualization plot with optional obstacle overlay"""
        # Performance optimization: Check if we need to update
        current_time = time.time()
        if current_time - self._last_update_time < 0.005:  # Only update every 50ms max
            if 'lane_plot' in self._plot_cache:
                return self._plot_cache['lane_plot']
        
        # Check if any lane has "Very Low Quality" - if so, force update
        force_update = False
        if self.lane_data_history['left'] and self.is_good_quality(self.lane_data_history['left'][-1].quality):
            force_update = True
        if self.lane_data_history['right'] and self.is_good_quality(self.lane_data_history['right'][-1].quality):
            force_update = True
            
        if force_update:
            self._plot_cache.clear()
            print("Force clearing cache due to Very Low Quality")
        
        fig = go.Figure()
        
        # Add vehicle representation (static, can be cached)
        vehicle_x = [0, -1, 1, 0]
        vehicle_y = [0, -2, -2, 0]
        fig.add_trace(go.Scatter(
            x=vehicle_x, y=vehicle_y,
            fill='toself',
            fillcolor='blue',
            line=dict(color='darkblue'),
            name='Vehicle',
            showlegend=True
        ))
        
        # Plot left lane - only if good quality
        if self.lane_data_history['left']:
            left_data = self.lane_data_history['left'][-1]
            print(f"Left lane quality: '{left_data.quality}' (type: {type(left_data.quality)})")
            if self.is_good_quality(left_data.quality):
                print(f"  -> Plotting left lane with quality: {left_data.quality}")
                x, y = self.calculate_lane_points(left_data, 'left')
                if x and y:
                    line_dict = {
                        'color': 'blue',
                        'width': 3,
                    }
                    fig.add_trace(go.Scatter(
                        x=x, y=y,
                        mode='lines',
                        line=line_dict,
                        name=f'Left Lane ({left_data.quality})',
                        showlegend=True
                    ))
                    lane_width = 3.5
                    boundary_y = [yi + lane_width/2 for yi in y]
                    boundary_line_dict = {
                        'color': 'blue',
                        'width': 1,
                        'dash': 'dash'
                    }
                    fig.add_trace(go.Scatter(
                        x=x, y=boundary_y,
                        mode='lines',
                        line=boundary_line_dict,
                        name='Left Boundary',
                        showlegend=False
                    ))
            else:
                print(f"  -> NOT plotting left lane (Very Low Quality)")
        
        # Plot right lane - only if good quality
        if self.lane_data_history['right']:
            right_data = self.lane_data_history['right'][-1]
            print(f"Right lane quality: '{right_data.quality}' (type: {type(right_data.quality)})")
            if self.is_good_quality(right_data.quality):
                print(f"  -> Plotting right lane with quality: {right_data.quality}")
                x, y = self.calculate_lane_points(right_data, 'right')
                if x and y:
                    line_dict = {
                        'color': 'green',
                        'width': 3
                    }
                    fig.add_trace(go.Scatter(
                        x=x, y=y,
                        mode='lines',
                        line=line_dict,
                        name=f'Right Lane ({right_data.quality})',
                        showlegend=True
                    ))
                    lane_width = 3.5
                    boundary_y = [yi - lane_width/2 for yi in y]
                    boundary_line_dict = {
                        'color': 'green',
                        'width': 1,
                        'dash': 'dash'
                    }
                    fig.add_trace(go.Scatter(
                        x=x, y=boundary_y,
                        mode='lines',
                        line=boundary_line_dict,
                        name='Right Boundary',
                        showlegend=False
                    ))
            else:
                print(f"  -> NOT plotting right lane (Very Low Quality)")
        
        # OVERLAY OBSTACLES ON THE SAME PLOT (optimized)
        if self.enable_obstacle_detection and self.obstacle_data_history:
            obstacle_list = self.obstacle_data_history[-1]
            
            if obstacle_list:
                # Extract individual obstacles from the Obstacle_Data_List
                obstacles = [
                    obstacle_list.object1, obstacle_list.object2, obstacle_list.object3,
                    obstacle_list.object4, obstacle_list.object5, obstacle_list.object6,
                    obstacle_list.object7, obstacle_list.object8, obstacle_list.object9,
                    obstacle_list.object10
                ]
                
                # Batch process obstacles for better performance
                valid_obstacles = [obs for obs in obstacles if obs and obs.last_update > 0]
                
                if valid_obstacles:
                    # Create batch scatter plot for better performance
                    x_coords = [obs.longitudinal_distance for obs in valid_obstacles]
                    y_coords = [obs.lateral_distance for obs in valid_obstacles]
                    colors = ['red' if obs.object_class == 1 else 'orange' for obs in valid_obstacles]
                    texts = [f'ID: {obs.id}<br>Class: {obs.object_class}<br>Velocity: {obs.absolute_long_velocity:.1f} m/s' 
                            for obs in valid_obstacles]
                    
                    fig.add_trace(go.Scatter(
                        x=x_coords, y=y_coords,
                        mode='markers',
                        marker=dict(
                            size=15,
                            color=colors,
                            symbol='circle'
                        ),
                        text=texts,
                        hoverinfo='text',
                        name='Obstacles',
                        showlegend=True
                    ))
        
        # Update layout (optimized)
        fig.update_layout(
            title="Real-time Lane Detection with Obstacles" if self.enable_obstacle_detection else "Real-time Lane Detection",
            xaxis_title="Distance Ahead (m)",
            yaxis_title="Lateral Position (m)",
            xaxis=dict(range=[0, 100]),
            yaxis=dict(range=[-20, 20]),
            height=500,
            showlegend=True,
            # Performance optimizations
            uirevision=True,  # Prevents unnecessary re-renders
            dragmode=False,   # Disable drag to improve performance
        )
        
        # Cache the result
        self._plot_cache['lane_plot'] = fig
        self._last_update_time = current_time
        
        return fig
    
    def is_good_quality(self, quality):
        # Only show line if quality is not 'Very Low Quality'
        if hasattr(quality, 'name') and hasattr(quality, 'value'):
            qname = quality.name.strip().lower()
            qval = int(quality.value)
            return not (qname == "very low quality" or qval == 0)
        if isinstance(quality, str):
            return quality.strip().lower() != "very low quality"
        elif isinstance(quality, (int, float)):
            return int(quality) != 0
        return False
    
    def create_obstacle_plot(self):
        """Create the obstacle visualization plot"""
        # Run the plot if not exclusively plotted in lane plot
        if self.enable_obstacle_detection:
            return None
        
        # Performance optimization: Check if we need to update
        current_time = time.time()
        if current_time - self._last_update_time < 0.05:  # Only update every 50ms max
            if 'obstacle_plot' in self._plot_cache:
                return self._plot_cache['obstacle_plot']
        
        fig = go.Figure()
        
        if self.obstacle_data_history:
            obstacle_list = self.obstacle_data_history[-1]
            
            if obstacle_list:
                # Extract individual obstacles from the Obstacle_Data_List
                obstacles = [
                    obstacle_list.object1, obstacle_list.object2, obstacle_list.object3,
                    obstacle_list.object4, obstacle_list.object5, obstacle_list.object6,
                    obstacle_list.object7, obstacle_list.object8, obstacle_list.object9,
                    obstacle_list.object10
                ]
                
                # Batch process obstacles for better performance
                valid_obstacles = [obs for obs in obstacles if obs and obs.last_update > 0]
                
                if valid_obstacles:
                    # Create batch scatter plot for better performance
                    x_coords = [obs.longitudinal_distance for obs in valid_obstacles]
                    y_coords = [obs.lateral_distance for obs in valid_obstacles]
                    colors = ['red' if obs.object_class == 1 else 'orange' for obs in valid_obstacles]
                    texts = [f'ID: {obs.id}<br>Class: {obs.object_class}<br>Velocity: {obs.absolute_long_velocity:.1f} m/s' 
                            for obs in valid_obstacles]
                    
                    fig.add_trace(go.Scatter(
                        x=x_coords, y=y_coords,
                        mode='markers',
                        marker=dict(
                            size=15,
                            color=colors,
                            symbol='circle'
                        ),
                        text=texts,
                        hoverinfo='text',
                        name='Obstacles'
                    ))
        
        fig.update_layout(
            title="Obstacle Detection",
            xaxis_title="Longitudinal Distance (m)",
            yaxis_title="Lateral Distance (m)",
            xaxis=dict(range=[0, 100]),
            yaxis=dict(range=[-20, 20]),
            height=400,
            # Performance optimizations
            uirevision=True,  # Prevents unnecessary re-renders
            dragmode=False,   # Disable drag to improve performance
        )
        
        # Cache the result
        self._plot_cache['obstacle_plot'] = fig
        self._last_update_time = current_time
        
        return fig
    
    def calculate_lane_points(self, lane_data, side='left'):
        """Calculate lane points using cubic polynomial model"""
        if not lane_data or lane_data.last_update == 0:
            return [], []
        
        # Get lane parameters
        if side == 'left':
            c0 = lane_data.LaneMarkPosition_C0_Lh_ME
            c1 = lane_data.LaneMarkHeadingAngle_C1_Lh_ME
            c2 = lane_data.LaneMarkModelA_C2_Lh_ME
            c3 = lane_data.LaneMarkModelDerivA_C3_Lh_ME
        else:  # right
            c0 = lane_data.LaneMarkPosition_C0_Rh_ME
            c1 = lane_data.LaneMarkHeadingAngle_C1_Rh_ME
            c2 = lane_data.LaneMarkModelA_C2_Rh_ME
            c3 = lane_data.LaneMarkModelDerivA_C3_Rh_ME
        
        # Generate x coordinates (distance ahead) - reduced resolution for better performance
        x = np.linspace(0, 100, 100)  # Reduced from 200 to 100 points
        
        # Calculate y coordinates using cubic polynomial
        # Jimmy told me to use the cubic polynomial model
        y = c0 + c1*x + c2*x**2 + c3*x**3
        
        return x.tolist(), y.tolist()
    
    def get_lane_params(self, side):
        """Get formatted lane parameters for display"""
        if side == 'left' and self.lane_data_history['left']:
            data = self.lane_data_history['left'][-1]
            return html.Div([
                html.P(f"Classification: {data.classification}"),
                html.P(f"Quality: {data.quality}"),
                html.P(f"Position (C0): {data.LaneMarkPosition_C0_Lh_ME:.3f} m"),
                html.P(f"Heading (C1): {data.LaneMarkHeadingAngle_C1_Lh_ME:.3f} rad"),
                html.P(f"Curvature (C2): {data.LaneMarkModelA_C2_Lh_ME:.6f} 1/m"),
                html.P(f"Curvature Rate (C3): {data.LaneMarkModelDerivA_C3_Lh_ME:.8f} 1/m²"),
                html.P(f"Last Update: {datetime.fromtimestamp(data.last_update).strftime('%H:%M:%S')}")
            ])
        elif side == 'right' and self.lane_data_history['right']:
            data = self.lane_data_history['right'][-1]
            return html.Div([
                html.P(f"Classification: {data.classification}"),
                html.P(f"Quality: {data.quality}"),
                html.P(f"Position (C0): {data.LaneMarkPosition_C0_Rh_ME:.3f} m"),
                html.P(f"Heading (C1): {data.LaneMarkHeadingAngle_C1_Rh_ME:.3f} rad"),
                html.P(f"Curvature (C2): {data.LaneMarkModelA_C2_Rh_ME:.6f} 1/m"),
                html.P(f"Curvature Rate (C3): {data.LaneMarkModelDerivA_C3_Rh_ME:.8f} 1/m²"),
                html.P(f"Last Update: {datetime.fromtimestamp(data.last_update).strftime('%H:%M:%S')}")
            ])
        else:
            return html.P("No data available")
    
    def create_data_table(self):
        """Create a data table showing latest values"""
        if not self.timestamps:
            return html.P("No data available")
        
        latest_time = datetime.fromtimestamp(self.timestamps[-1]).strftime('%H:%M:%S')
        
        return html.Div([
            html.H4(f"Latest Update: {latest_time}"),
            html.P(f"Total Data Points: {len(self.timestamps)}"),
            html.P(f"Left Lane Data: {'Available' if self.lane_data_history['left'] else 'None'}"),
            html.P(f"Right Lane Data: {'Available' if self.lane_data_history['right'] else 'None'}"),
            html.P(f"Obstacle Data: {'Available' if self.obstacle_data_history else 'None'}")
        ])
    
    def add_lane_data(self, left_lane_data=None, right_lane_data=None):
        """Add new lane data for visualization"""
        current_time = time.time()
        
        if left_lane_data:
            self.lane_data_history['left'].append(left_lane_data)
            # print(f"Added left lane data: {left_lane_data}")
            
        if right_lane_data:
            self.lane_data_history['right'].append(right_lane_data)
            # print(f"Added right lane data: {right_lane_data}")
            
        if left_lane_data or right_lane_data:
            self.timestamps.append(current_time)
            # Clear cache to force update with new data
            self._plot_cache.clear()
            # print(f"Cache cleared, total left: {len(self.lane_data_history['left'])}, total right: {len(self.lane_data_history['right'])}")
    
    def add_obstacle_data(self, obstacle_data):
        """Add new obstacle data for visualization"""
        if obstacle_data:
            self.obstacle_data_history.append(obstacle_data)
            # Clear cache to force update with new data
            self._plot_cache.clear()
    
    def clear_data(self):
        """Clear all stored data"""
        self.lane_data_history['left'].clear()
        self.lane_data_history['right'].clear()
        self.obstacle_data_history.clear()
        self.timestamps.clear()
        # Clear cache
        self._plot_cache.clear()
    
    def get_server_url(self):
        """Get the server URL for remote access"""
        return f"http://{self.host}:{self.port}"
    
    async def start_server(self):
        """Start the Dash server asynchronously"""
        def run_server():
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False
            )
        
        # Run server in a separate thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait a moment for server to start
        await asyncio.sleep(2)
        
        # Print access information
        server_url = self.get_server_url()
        print(f"🌐 MobilEye Visualizer is running at: {server_url}")
        print(f"📱 Access from any device on the network using this URL")
        print(f"🖥️  Local access: http://localhost:{self.port}")
        
        # Try to open browser (works on local machine)
        try:
            webbrowser.open(server_url)
        except:
            pass
    
    async def stop_server(self):
        """Stop the visualization server"""
        self.is_running = False
        print("🛑 MobilEye Visualizer stopped")

# Example usage function
async def create_and_start_visualizer(host='0.0.0.0', port=8050):
    """Create and start the visualizer"""
    visualizer = MobilEyeVisualizer(host=host, port=port)
    await visualizer.start_server()
    return visualizer

if __name__ == "__main__":
    # Test the visualizer
    async def test():
        visualizer = await create_and_start_visualizer()
        
        # Keep the server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await visualizer.stop_server()
    
    asyncio.run(test())
