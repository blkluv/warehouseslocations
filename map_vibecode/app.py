from flask import Flask, render_template
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Read the CSV file
    df = pd.read_csv('california_warehouses_nospp.csv')

    # Create a map centered on California
    california_map = folium.Map(
        location=[36.7783, -119.4179],  # Center of California
        zoom_start=6,
        tiles='OpenStreetMap',
        control_scale=True
    )

    # Create a marker cluster for better performance with many markers
    marker_cluster = MarkerCluster().add_to(california_map)

    # Add markers for each warehouse
    for idx, row in df.iterrows():
        # Create popup content with warehouse information
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 250px;">
            <h4 style="margin: 0 0 10px 0; color: #232F3E;">{row['name']}</h4>
            <p style="margin: 5px 0;"><strong>Type:</strong> {row['type']}</p>
            <p style="margin: 5px 0;"><strong>Status:</strong> {row['status']}</p>
            <p style="margin: 5px 0;"><strong>Address:</strong> {row['address']}</p>
            <p style="margin: 5px 0;"><strong>ZIP:</strong> {row['zip']}</p>
        </div>
        """

        # Determine marker color based on status
        if row['status'] == 'Active':
            icon_color = 'green'
        else:
            icon_color = 'red'

        # Add marker to cluster
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['name'],
            icon=folium.Icon(color=icon_color, icon='warehouse', prefix='fa')
        ).add_to(marker_cluster)

    # Save map to HTML string
    map_html = california_map._repr_html_()

    return render_template('index.html', map_html=map_html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
