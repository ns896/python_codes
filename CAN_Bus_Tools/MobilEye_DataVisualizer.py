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
        self.update_interval = 200  # milliseconds
        
        self.enable_obstacle_detection = False  

        # Data storage
        self.lane_data_history = {
            'left': deque(maxlen=max_data_points),
            'right': deque(maxlen=max_data_points)
        }
        self.obstacle_data_history = deque(maxlen=max_data_points)
        self.timestamps = deque(maxlen=max_data_points)
        
        # Initialize Dash app
        self.app = dash.Dash(__name__)
        self.setup_dash_app()
        
    def setup_dash_app(self):
        """Setup the Dash application layout"""
        self.app.layout = html.Div([
            html.H1("MobilEye CAN Data Visualization", 
                   style={'textAlign': 'center', 'color': '#2c3e50'}),
            html.H2("By Navneet Singh", style={'textAlign': 'center', 'color': '#2c3e50'}),
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
            
            # Obstacle visualization
            html.Div([
                html.H3("Obstacle Detection"),
                dcc.Graph(id='obstacle-plot', style={'height': '400px'}),
                dcc.Interval(
                    id='obstacle-interval',
                    interval=self.update_interval,
                    n_intervals=0,
                    disabled=True
                )
            ]),
            
            # Data table
            html.Div([
                html.H3("Latest Data"),
                html.Div(id='data-table')
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
            Output('obstacle-plot', 'figure'),
            [Input('obstacle-interval', 'n_intervals')]
        )
        def update_obstacle_plot(n):
            return self.create_obstacle_plot()
        
        @self.app.callback(
            Output('data-table', 'children'),
            [Input('lane-interval', 'n_intervals')]
        )
        def update_data_table(n):
            return self.create_data_table()
        
        @self.app.callback(
            [Output('lane-interval', 'disabled'),
             Output('obstacle-interval', 'disabled'),
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
                return True, True, "Ready to start"
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'start-btn':
                self.is_running = True
                return False, False, "Visualization running..."
            elif button_id == 'stop-btn':
                self.is_running = False
                return True, True, "Visualization stopped"
            elif button_id == 'clear-btn':
                self.clear_data()
                return True, True, "Data cleared"
            elif button_id == 'enable-obstacle-btn':
                self.enable_obstacle_detection = True
                return False, False, "Obstacle detection enabled - obstacles overlaid on lane plot"
            elif button_id == 'disable-obstacle-btn':
                self.enable_obstacle_detection = False
                return False, False, "Obstacle detection disabled"
            return True, True, "Ready to start"
    
    def create_lane_plot(self):
        """Create the lane visualization plot with optional obstacle overlay"""
        fig = go.Figure()
        
        # Add vehicle representation
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
        
        # Plot left lane
        if self.lane_data_history['left']:
            left_data = self.lane_data_history['left'][-1]
            x, y = self.calculate_lane_points(left_data, 'left')
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                line=dict(color='red', width=3),
                name='Left Lane',
                showlegend=True
            ))
            
            # Lane boundary
            # Ignore this line in plot only for Navneets Stupid eyes
            lane_width = 3.5
            fig.add_trace(go.Scatter(
                x=x, y=[yi + lane_width/2 for yi in y],
                mode='lines',
                line=dict(color='red', width=1, dash='dash'),
                name='Left Boundary',
                showlegend=False
            ))
        
        # Plot right lane
        if self.lane_data_history['right']:
            right_data = self.lane_data_history['right'][-1]
            x, y = self.calculate_lane_points(right_data, 'right')
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                line=dict(color='green', width=3),
                name='Right Lane',
                showlegend=True
            ))
            
            # Lane boundary
            # Ignore this line in plot only for Navneets Stupid eyes
            lane_width = 3.5
            fig.add_trace(go.Scatter(
                x=x, y=[yi - lane_width/2 for yi in y],
                mode='lines',
                line=dict(color='green', width=1, dash='dash'),
                name='Right Boundary',
                showlegend=False
            ))
        
        # OVERLAY OBSTACLES ON THE SAME PLOT
        if hasattr(self, 'enable_obstacle_detection') and self.enable_obstacle_detection:
            if self.obstacle_data_history:
                obstacle_list = self.obstacle_data_history[-1] if self.obstacle_data_history else None
                
                if obstacle_list:
                    # Extract individual obstacles from the Obstacle_Data_List
                    obstacles = [
                        obstacle_list.object1, obstacle_list.object2, obstacle_list.object3,
                        obstacle_list.object4, obstacle_list.object5, obstacle_list.object6,
                        obstacle_list.object7, obstacle_list.object8, obstacle_list.object9,
                        obstacle_list.object10
                    ]
                    
                    for obstacle in obstacles:
                        # Only plot obstacles that have valid data
                        if obstacle and obstacle.last_update > 0:
                            fig.add_trace(go.Scatter(
                                x=[obstacle.longitudinal_distance],
                                y=[obstacle.lateral_distance],
                                mode='markers',
                                marker=dict(
                                    size=15,
                                    color='red' if obstacle.object_class == 1 else 'orange',
                                    symbol='circle'
                                ),
                                name=f'Obstacle {obstacle.id}',
                                text=f'ID: {obstacle.id}<br>Class: {obstacle.object_class}<br>Velocity: {obstacle.absolute_long_velocity:.1f} m/s',
                                hoverinfo='text',
                                showlegend=True
                            ))
        
        # Update layout
        fig.update_layout(
            title="Real-time Lane Detection with Obstacles" if hasattr(self, 'enable_obstacle_detection') and self.enable_obstacle_detection else "Real-time Lane Detection",
            xaxis_title="Distance Ahead (m)",
            yaxis_title="Lateral Position (m)",
            xaxis=dict(range=[0, 100]),
            yaxis=dict(range=[-20, 20]),
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_obstacle_plot(self):
        """Create the obstacle visualization plot"""
        # Run the plot if not exclusively plotted in lane plot
        if self.enable_obstacle_detection:
            return None
        
        fig = go.Figure()
        
        if self.obstacle_data_history:
            obstacle_list = self.obstacle_data_history[-1] if self.obstacle_data_history else None
            
            if obstacle_list:
                # Extract individual obstacles from the Obstacle_Data_List
                obstacles = [
                    obstacle_list.object1, obstacle_list.object2, obstacle_list.object3,
                    obstacle_list.object4, obstacle_list.object5, obstacle_list.object6,
                    obstacle_list.object7, obstacle_list.object8, obstacle_list.object9,
                    obstacle_list.object10
                ]
                
                for obstacle in obstacles:
                    # Only plot obstacles that have valid data
                    if obstacle and obstacle.last_update > 0:
                        fig.add_trace(go.Scatter(
                            x=[obstacle.longitudinal_distance],
                            y=[obstacle.lateral_distance],
                            mode='markers',
                            marker=dict(
                                size=15,
                                color='red' if obstacle.object_class == 1 else 'orange',
                                symbol='circle'
                            ),
                            name=f'Obstacle {obstacle.id}',
                            text=f'ID: {obstacle.id}<br>Class: {obstacle.object_class}<br>Velocity: {obstacle.absolute_long_velocity:.1f} m/s',
                            hoverinfo='text'
                        ))
        
        fig.update_layout(
            title="Obstacle Detection",
            xaxis_title="Longitudinal Distance (m)",
            yaxis_title="Lateral Distance (m)",
            xaxis=dict(range=[0, 100]),
            yaxis=dict(range=[-20, 20]),
            height=400
        )
        
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
        
        # Generate x coordinates (distance ahead)
        x = np.linspace(0, 100, 200)
        
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
            
        if right_lane_data:
            self.lane_data_history['right'].append(right_lane_data)
            
        self.timestamps.append(current_time)
    
    def add_obstacle_data(self, obstacle_data):
        """Add new obstacle data for visualization"""
        if obstacle_data:
            self.obstacle_data_history.append(obstacle_data)
    
    def clear_data(self):
        """Clear all stored data"""
        self.lane_data_history['left'].clear()
        self.lane_data_history['right'].clear()
        self.obstacle_data_history.clear()
        self.timestamps.clear()
    
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
