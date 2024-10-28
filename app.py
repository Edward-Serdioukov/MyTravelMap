import json
from flask import Flask, render_template, request, send_file
import folium
from folium.plugins import Fullscreen, MarkerCluster
import urllib.parse

app = Flask(__name__)


with open('places_visited.json', 'r') as f:
    places_visited = json.load(f)
    

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
    
    # Render the HTML page with the map
    return render_template('index.html', title="My trips. Map 1", map_url='map.html')

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
   