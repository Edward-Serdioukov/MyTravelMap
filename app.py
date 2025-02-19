import json
from flask import Flask, render_template, request, send_file
import folium
from folium.plugins import Fullscreen
import urllib.parse
from collections import defaultdict
import re

app = Flask(__name__)


with open('places_visited.json', 'r') as f:
    places_visited = json.load(f)
    
with open('countries_map.json', 'r') as f:
    COUNTRY_MAP = json.load(f)
    

button_html = """
<div style="position: fixed; 
            bottom: 10px; left: 10px; 
            z-index: 9999; 
            background-color: white; 
            padding: 10px; 
            border-radius: 5px; 
            box-shadow: 0 0 5px rgba(0,0,0,0.5);">
    <button onclick="document.getElementById('info').style.display='block';">?</button>
   
   <div id="info" style="display:none; position:absolute; top:-320px; left:0; background-color:white; padding:10px; border-radius:5px; box-shadow: 0 0 5px rgba(0,0,0,0.5); height:300px; width:200px; overflow:auto;">
        <p><b>Help</b></p>
        <p>To see the photo, you need to click on the marker. A popup window with small photos will open. 
        If you click on any photo in the popup, a new window with large photos will open.</p>
        <button onclick="document.getElementById('info').style.display='none';">Close</button>
        <a href="/book" target="_blank">&#127758;</a>
        <a href="/book-dates" target="_blank">&#128197;</a> 
    </div>
</div>
""" 

def get_html_for_popup(place):
    """
    The function takes a dictionary with place information and returns a string
    with HTML code for popup window.
    """
    html = ""
    if place["img_orient"] == "2":
        # If the orientation is set to 2, the popup window will have a fixed
        # height of 410px and a filmstrip with images will be displayed.
        # The filmstrip is a horizontal list of images.
        if len(place["images"]) > 1:
            html = """
                    <div  class="filmstrip" id="image-popup" style='width:300px; height:410px; overflow-y: scroll;'>
                """
        else:
            # If there is only one image, the popup window will have a fixed
            # height of 210px and a single image will be displayed.
            html = """
                    <div  class="filmstrip" id="image-popup" style='width:300px; height:210px; overflow-y: scroll;'>
                """
    else:
        # If the orientation is not set to 2, the popup window will have a fixed
        # height of 410px and a single image will be displayed.
        html = """
                <div  class="filmstrip" id="image-popup" style='width:300px; height:410px; overflow-y: scroll;'>
                """

    html += f"<b>{place['name']}</b><br>"

    # Create query parameters for the link
    query_params = {
        "images": ",".join(place["images"]),
        "title": place["name"]
    }

    # Encode the query parameters
    query_string = urllib.parse.urlencode(query_params)

    # Create the URL with the query parameters
    url = f'/gallery?{query_string}'

    # Create the link
    html += f'<a href="{url}" target="_blank">'

    for img in place["images"]:
        if place["img_orient"] == "2":
            # Display the images in a filmstrip
            html += f"<img src='{img}' alt='Images' style='width:100%;'>"
        else:
            # Display a single image
            html += f"<img src='{img}' alt='Images' style='width:100%;'/>"

    html += "</a></div>"

    return html

def replace_html(html_file):

    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    """
    html = html.replace(
        'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css',
        'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css'
    )
    html = html.replace(
        'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js',
        'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js'
    )
    """
    
    html = html.replace(
        'https://cdn.jsdelivr.net/npm/leaflet-textpath@1.2.3/leaflet.textpath.min.js',
        'js/leaflet.textpath.min.js'
    )
    html = html.replace(
        'https://cdn.jsdelivr.net/gh/marslan390/BeautifyMarker/leaflet-beautify-marker-icon.min.css',
        'css/leaflet-beautify-marker-icon.min.css'
    )
    html = html.replace(
        'https://cdn.jsdelivr.net/gh/marslan390/BeautifyMarker/leaflet-beautify-marker-icon.min.js',
        'js/leaflet-beautify-marker-icon.min.js'
    )
    html = html.replace(
        'https://cdn.jsdelivr.net/npm/leaflet.fullscreen@3.0.0/Control.FullScreen.min.js',
        'js/Control.FullScreen.min.js'
    )
    html = html.replace(
        'https://cdn.jsdelivr.net/npm',
        'https://unpkg.com'
    )
    html = html.replace(
        'https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css',
        'css/leaflet.awesome.rotate.min.css'
    )


    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js', mimetype='application/javascript')

@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')


@app.route('/')
def index():
    """
    Generates a map with markers for visited places and returns an HTML page with the map.

    This function creates a folium map centered at approximate coordinates of Europe, 
    adds markers for each place visited, enables fullscreen mode, and saves the map as an HTML file.
    """
    # Set starting coordinates at approximate center of Europe
    start_coords = (46.0, 17.0)
    
    # Create a folium map with a starting zoom level
    folium_map = folium.Map(location=start_coords, zoom_start=4)
    
    # Add custom CSS to the map
    folium_map.get_root().header.add_child(folium.CssLink('css/style.css'))
    
 
    # Add markers to the map for each visited place
    for place in places_visited:
        html = get_html_for_popup(place)
        folium.Marker(
            location=place["coords"],
            popup=html,
            tooltip=place["name"]
        ).add_to(folium_map)


    # Add a fullscreen button to the map
    fullscreen = Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    )
    fullscreen.add_to(folium_map)
    
    # Add custom button to the map
    folium_map.get_root().html.add_child(folium.Element(button_html))

   
    # Save the map to an HTML file
    folium_map.save('static/map.html')
    replace_html('static/map.html')
    
    # Render the HTML page with the map
    return render_template('index.html', title="My Travel Map", map_url='map.html')

@app.route('/map2')
def map2():
    start_coords = (46.0, 17.0)  
    folium_map = folium.Map(location=start_coords, zoom_start=4)
    marker_cluster = folium.plugins.MarkerCluster().add_to(folium_map)

    folium_map.get_root().header.add_child(folium.CssLink('css/style.css'))
 

    for place in places_visited:
        html = get_html_for_popup(place)
        folium.Marker(
            location=place["coords"],
            popup=html,
            tooltip=place["name"],
            lazy=True
        ).add_to(marker_cluster)

    fullscreen = Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    )
    fullscreen.add_to(folium_map)

    ###folium_map.save('static/map2.html')
    return render_template('index.html', title="My trips. Map 2", map_url='map2.html')

def process_data(data):
    timeline = {}
    for item in data:
        name = item['name']
        years = extract_year(name)  # This now returns a list of years
        place = extract_place(name)  # Extract place from the name
        country = COUNTRY_MAP.get(place, "Unknown")

        if years:  # Only proceed if there are years in the list
            for year in years:
                if year:  # Ensure year is valid
                    if year not in timeline:
                        timeline[year] = {}
                    if country not in timeline[year]:
                        timeline[year][country] = {}
                    if place not in timeline[year][country]:
                        timeline[year][country][place] = []

                    timeline[year][country][place].append({
                        "coords": item['coords'],
                        "images": item['images'],
                        "img_orient": item['img_orient'],
                        "original_name": name  # Store the original name
                    })
    return timeline


def extract_year(name):
    years = set()
    parts = re.split(r'[,\s]+', name)

    for part in parts:
        part = part.strip()
        if part.isdigit() and len(part) == 4:  # Check if it's a single year
            years.add(part)
        elif "-" in part:  # Check for a range of years
            range_years = part.split("-")
            if len(range_years) == 2 and range_years[0].isdigit() and len(range_years[0]) == 4 and range_years[1].isdigit() and len(range_years[1]) == 4:
                # Add all years in the range
                """
                start_year = int(range_years[0])
                end_year = int(range_years[1])
                for year in range(start_year, end_year + 1):
                    years.add(str(year))
                """
                years.add(str(range_years[0]))
                years.add(str(range_years[1]))

    # Return a list of years, or None if no years found
    return list(years) if years else None  


def extract_place(name):
    parts = name.split(' ')
    if len(parts) > 0:
        for part in parts:
            if any(char.isdigit() for char in part):
                return ' '.join(parts[:parts.index(part)])
        #return parts[0].strip()
    return name.strip()  # If no comma, return the whole name

def get_timeline():
    timeline_data = process_data(places_visited)
    # Сортируем ключи (года)
    sorted_keys = sorted(timeline_data.keys(), key=int)
    sorted_timeline = {}
    for year in sorted_keys:
        # Сортируем места внутри года
        sorted_places = sorted(timeline_data[year].keys())
        sorted_timeline[year] = {}
        for place in sorted_places:
            sorted_timeline[year][place] = timeline_data[year][place]
    return sorted_timeline

@app.route('/book')
def book():

    # 2. Создадим структуру для группировки:
    #    countries = {
    #        "Czech Republic": {
    #            "Marianske Lazne": [...],
    #            "Prague": [...],
    #            ...
    #        },
    #        "Germany": {
    #            "Nurnberg": [...],
    #            ...
    #        }
    #    }
    countries = defaultdict(lambda: defaultdict(list))

    for place in places_visited:
        # Предположим, что город — это первое слово в "name".
        # Например, "Barselona 2016-2023" -> "Barselona"
        # Или "Marianske Lazne 2024" -> "Marianske"
        # Но на практике, возможно, придётся распарсить чуть иначе.
        city_candidate = extract_place(place["name"]) #place["name"].split()[0]

        # Ищем, какая страна соответствует этому городу
        country = COUNTRY_MAP.get(city_candidate, "Unknown")

        # Добавляем в итоговую структуру
        countries[country][city_candidate].append(place)

    # 3. Передаём в шаблон
    return render_template('photobook.html', countries=countries)

@app.route('/book-dates')
def book_dates():
    timeline_data = get_timeline()
    return render_template('photobook-dates.html', timeline_data=timeline_data, is_img='true')

@app.route('/gallery')
def gallery():
    images = request.args.get('images').split(',')
    title = request.args.get('title', 'Gallery')
    return render_template('gallery.html', images=images, title=title)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
   