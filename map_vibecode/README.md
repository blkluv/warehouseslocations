# California Warehouses Map

A clean, full-page interactive map application displaying California warehouse locations.

## Features

- Full-page interactive map centered on California
- 238+ warehouse locations with detailed information
- Color-coded markers (Green = Active, Red = Inactive)
- Marker clustering for performance
- Responsive design

## Live Demo

[Add your deployed URL here after deployment]

## Technologies Used

- Flask - Web framework
- Folium - Interactive maps
- Pandas - Data processing

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python3 app.py
```

3. Open http://localhost:5001 in your browser

## Deployment

This app is configured for easy deployment to Render, Heroku, or similar platforms.

The app uses Gunicorn as the production server and reads the PORT environment variable.
