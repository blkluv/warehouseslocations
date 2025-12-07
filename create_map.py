import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo


def inject_custom_styling(html_file):
    """Add custom styling and search bar to the generated HTML file"""
    with open(html_file, 'r') as f:
        html_content = f.read()

    # Custom CSS styling inspired by professional warehouse/logistics design
    custom_css = """
    <style>
        body {
            background: linear-gradient(135deg, #232F3E 0%, #FF9900 100%);
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
        }

        .plotly-graph-div {
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            overflow: hidden;
            background: white;
        }

        /* Glass morphism effect container */
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        /* Search bar styling */
        .search-container {
            position: fixed;
            top: 30px;
            right: 30px;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 50px;
            padding: 10px 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .search-input {
            border: none;
            background: transparent;
            font-size: 16px;
            padding: 8px 12px;
            width: 300px;
            outline: none;
            color: #232F3E;
        }

        .search-input::placeholder {
            color: #888;
        }

        .search-icon {
            color: #FF9900;
            font-size: 20px;
        }

        .search-results {
            position: fixed;
            top: 90px;
            right: 30px;
            z-index: 999;
            background: white;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            max-width: 400px;
            max-height: 300px;
            overflow-y: auto;
            display: none;
        }

        .result-item {
            padding: 10px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
            transition: background 0.2s;
        }

        .result-item:hover {
            background: #f5f5f5;
        }

        .result-item:last-child {
            border-bottom: none;
        }

        .result-name {
            font-weight: bold;
            color: #232F3E;
        }

        .result-address {
            font-size: 12px;
            color: #666;
        }

        .no-results {
            text-align: center;
            color: #888;
            padding: 20px;
        }
    </style>
    """

    # Search bar HTML
    search_html = """
    <div class="search-container">
        <span class="search-icon">🔍</span>
        <input type="text" class="search-input" id="searchInput" placeholder="Search by state or facility code (e.g., CA or BWI6)">
    </div>
    <div class="search-results" id="searchResults"></div>
    """

    # Inject the custom CSS before the closing </head> tag
    html_content = html_content.replace('</head>', custom_css + '</head>')

    # Inject the search bar after the opening <body> tag
    html_content = html_content.replace('<body>', '<body>' + search_html)

    # Write the modified HTML back to the file
    with open(html_file, 'w') as f:
        f.write(html_content)

    print("Custom styling and search bar applied to HTML")


def inject_search_functionality(html_file, df):
    """Add JavaScript search functionality to the HTML file"""
    with open(html_file, 'r') as f:
        html_content = f.read()

    # Convert dataframe to JavaScript-friendly format
    facilities_data = []
    for _, row in df.iterrows():
        # Extract state from address (assuming format: "address, City, ST")
        address_parts = row['address'].split(',')
        state = address_parts[-1].strip().split()[0] if len(address_parts) > 1 else ''

        facilities_data.append({
            'name': row['name'],
            'address': row['address'],
            'state': state,
            'lat': float(row['latitude']),
            'lon': float(row['longitude'])
        })

    # Convert to JSON string
    import json
    facilities_json = json.dumps(facilities_data)

    # JavaScript code for search functionality
    search_js = f"""
    <script>
        // Facilities data
        const facilities = {facilities_json};

        const searchInput = document.getElementById('searchInput');
        const searchResults = document.getElementById('searchResults');

        // Search function
        function searchFacilities(query) {{
            if (!query || query.length < 2) {{
                searchResults.style.display = 'none';
                return;
            }}

            query = query.toUpperCase();

            // Search by facility code or state
            const results = facilities.filter(facility =>
                facility.name.toUpperCase().includes(query) ||
                facility.state.toUpperCase().includes(query) ||
                facility.address.toUpperCase().includes(query)
            );

            displayResults(results);
        }}

        // Display search results
        function displayResults(results) {{
            if (results.length === 0) {{
                searchResults.innerHTML = '<div class="no-results">No facilities found</div>';
                searchResults.style.display = 'block';
                return;
            }}

            const resultsHTML = results.slice(0, 10).map(facility => `
                <div class="result-item" onclick="centerMap(${{facility.lat}}, ${{facility.lon}}, '${{facility.name}}')">
                    <div class="result-name">${{facility.name}}</div>
                    <div class="result-address">${{facility.address}}</div>
                </div>
            `).join('');

            searchResults.innerHTML = resultsHTML;
            searchResults.style.display = 'block';
        }}

        // Center map on selected facility
        function centerMap(lat, lon, name) {{
            // Get the plotly graph div
            const plotlyDiv = document.getElementsByClassName('plotly-graph-div')[0];

            if (plotlyDiv) {{
                // Update the map center and zoom in using Plotly.relayout
                Plotly.relayout(plotlyDiv, {{
                    'mapbox.center': {{lat: lat, lon: lon}},
                    'mapbox.zoom': 12
                }}).then(function() {{
                    console.log('Map centered on:', name, 'at', lat, lon);
                }}).catch(function(error) {{
                    console.error('Error centering map:', error);
                }});
            }} else {{
                console.error('Plotly div not found');
            }}

            // Hide search results
            searchResults.style.display = 'none';
            searchInput.value = name;
        }}

        // Event listeners
        searchInput.addEventListener('input', (e) => {{
            searchFacilities(e.target.value);
        }});

        // Hide results when clicking outside
        document.addEventListener('click', (e) => {{
            if (!e.target.closest('.search-container') && !e.target.closest('.search-results')) {{
                searchResults.style.display = 'none';
            }}
        }});
    </script>
    """

    # Inject the JavaScript before the closing </body> tag
    html_content = html_content.replace('</body>', search_js + '</body>')

    # Write the modified HTML back to the file
    with open(html_file, 'w') as f:
        f.write(html_content)

    print("Search functionality added to HTML")


def create_us_map():
    """Create an interactive map of US facilities and save as HTML"""
    
    try:
        # Load the CSV file
        df = pd.read_csv('USA facilities.csv')
        print(f"Loaded {len(df)} total facilities")
        
        # Display column names to help with debugging
        print("CSV columns:", df.columns.tolist())
        
        # Common column name variations - adjust these based on your CSV structure
        lat_columns = ['latitude', 'lat', 'Latitude', 'LAT', 'y', 'Y']
        lon_columns = ['longitude', 'lon', 'lng', 'Longitude', 'LON', 'LONGITUDE', 'x', 'X']
        name_columns = ['site_name', 'name', 'facility_name', 'site', 'Site', 'Name', 'facility']
        address_columns = ['address', 'Address', 'full_address', 'location', 'street_address']
        
        # Find the correct column names
        lat_col = next((col for col in lat_columns if col in df.columns), None)
        lon_col = next((col for col in lon_columns if col in df.columns), None)
        name_col = next((col for col in name_columns if col in df.columns), None)
        address_col = next((col for col in address_columns if col in df.columns), None)
        
        if not lat_col or not lon_col:
            print("Error: Could not find latitude/longitude columns")
            print("Available columns:", df.columns.tolist())
            return False
            
        print(f"Using columns - Lat: {lat_col}, Lon: {lon_col}, Name: {name_col}, Address: {address_col}")
        
        # Clean and convert coordinates
        df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
        df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
        
        # Remove rows with invalid coordinates
        df = df.dropna(subset=[lat_col, lon_col])
        print(f"After cleaning coordinates: {len(df)} facilities")
        
        # Filter for United States coordinates
        # Continental US + Alaska + Hawaii bounds
        us_df = df[
            (df[lat_col] >= 18.0) & (df[lat_col] <= 72.0) &  # Includes Alaska and Hawaii
            (df[lon_col] >= -180.0) & (df[lon_col] <= -65.0)
        ].copy()
        
        print(f"US facilities found: {len(us_df)}")
        
        # Optional: Filter by status (uncomment the lines below if you want only specific statuses)
        # FILTER OPTIONS - Uncomment ONE of these if desired:
        
        # Option 1: Only idle sites
        # us_df = us_df[us_df['status'].str.lower() == 'idle']
        # print(f"Idle facilities: {len(us_df)}")
        
        # Option 2: Only active sites  
        # us_df = us_df[us_df['status'].str.lower() == 'active']
        # print(f"Active facilities: {len(us_df)}")
        
        # Option 3: Exclude certain statuses
        # us_df = us_df[~us_df['status'].str.lower().isin(['closed', 'inactive'])]
        # print(f"Open facilities: {len(us_df)}")
        
        # Show status breakdown
        if 'status' in us_df.columns:
            print("\nStatus breakdown:")
            status_counts = us_df['status'].value_counts()
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
            print()
        
        if len(us_df) == 0:
            print("No facilities found in US coordinate range")
            return False
        
        # Prepare hover text
        hover_data = {}
        hover_name = None
        
        if name_col and name_col in us_df.columns:
            hover_name = name_col
            hover_data[name_col] = False  # Don't show in hover data since it's the hover_name
        
        if address_col and address_col in us_df.columns:
            hover_data[address_col] = True
            
        # Always hide coordinates from hover
        hover_data[lat_col] = False
        hover_data[lon_col] = False
        
        # Create the interactive map using the new scatter_map function
        fig = px.scatter_map(
            us_df,
            lat=lat_col,
            lon=lon_col,
            hover_name=hover_name,
            hover_data=hover_data,
            zoom=2.5,
            height=700,
            title="Amazon Warehouse Locations",
            center={"lat": 39.8283, "lon": -98.5795}  # Geographic center of USA
        )

        # Update map style and layout with zoom constraints
        fig.update_layout(
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            title={
                'text': "Amazon Warehouse Locations - USA",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            mapbox={
                'zoom': 2.5,
                'center': {"lat": 39.8283, "lon": -98.5795},
                'style': 'open-street-map'
            }
        )
        
        # Update marker appearance (removed invalid 'line' property)
        fig.update_traces(
            marker=dict(
                size=10,
                color='red',
                opacity=0.7
            )
        )
        
        # Save the map as HTML
        fig.write_html("warehouse_map.html")
        print("Map saved as warehouse_map.html")

        # Apply custom styling
        inject_custom_styling("warehouse_map.html")

        # Add search functionality with the dataframe
        inject_search_functionality("warehouse_map.html", us_df)

        # Also show the map if running interactively
        # fig.show()

        return True
        
    except FileNotFoundError:
        print("Error: USA facilities.csv file not found")
        return False
    except Exception as e:
        print(f"Error creating map: {str(e)}")
        return False

if __name__ == "__main__":
    print("Creating Amazon warehouse map...")
    success = create_us_map()

    if success:
        print("\nWarehouse map creation completed successfully!")
        print("Files created:")
        print("- warehouse_map.html (interactive Amazon warehouse map)")
    else:
        print("\nMap creation failed. Please check your CSV file and try again.")