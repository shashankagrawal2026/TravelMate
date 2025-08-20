# Import the required modules

import networkx as nx
import nx_arangodb as nxadb

from arango import ArangoClient

import pandas as pd
import numpy as np
import requests
import urllib.parse
import networkx as nx
import matplotlib.pyplot as plt
from random import randint
import re
import os
import io
from dotenv import load_dotenv
import json
from typing import List, Dict, Any, Optional

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_community.graphs import ArangoGraph
from langchain_community.chains.graph_qa.arangodb import ArangoGraphQAChain
from langchain_core.tools import tool

from flask import Flask, request, jsonify
from flask_cors import CORS
# Load environment variables from .env file
load_dotenv()

# ----------------------------------------------------------------WIKIPEDIA API----------------------------------------------------------------------

def get_wikipedia_info(name):
    # Step 1: Construct the API URL
    search_title = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=" + \
        urllib.parse.quote(name) + \
        "&format=json&origin=*"
    search_title_response = requests.get(search_title)
    if search_title_response.status_code != 200:
        raise Exception(
            f"Failed to fetch search results. Received: {search_title_response.status_code} {search_title_response.reason}"
        )
    
    search_title_data = search_title_response.json()
    if len(search_title_data["query"]["search"]) == 0:
        return "No information found on Wikipedia"
    
    title = search_title_data["query"]["search"][0]["title"]

    search_url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&titles=" + \
        urllib.parse.quote(title) + \
        "&explaintext=1&origin=*"
    
    search_response = requests.get(search_url)
    if search_response.status_code != 200:
        raise Exception(
            f"Failed to fetch search results. Received: {search_response.status_code} {search_response.reason}"
        )

    # Parse the JSON response
    search_data = search_response.json()

    data = search_data['query']['pages']
    page_number = list(data.keys())[0]
    extracted_text = data[page_number]['extract']
    return extracted_text

# ----------------------------------------------------------------MAPS API----------------------------------------------------------------------

def get_maps_places(location, search_text="Most Popular places in "):
    api_key = os.getenv("GEMINI_API_KEY")
    # Step 1: Construct the API URL for Google Maps Places API
    search_query = search_text + location
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + \
        urllib.parse.quote(search_query) + \
        f"&radius=20000&key={api_key}"  # Replace with your actual API key
    
    search_response = requests.get(search_url)
    if search_response.status_code != 200:
        raise Exception(
            f"Failed to fetch search results. Received: {search_response.status_code} {search_response.reason}"
        )

    # Parse the JSON response
    search_data = search_response.json()
    return search_data["results"]


# -------------------------------------------------Wiki details of Maps recommended places Function-------------------------------------------------------

def get_wiki_desc_for_places(destination_location, sz = 2):
    places = get_maps_places(destination_location, "Most Popular places in ")
    place_descriptors = []
    
    for i in range(min(sz, len(places))):
        description = get_wikipedia_info(places[i]["name"])

        place_descriptor = {
            "place": places[i]["name"],
            "description": description,
            "destination": destination_location
        }
        place_descriptors.append(place_descriptor)
    
    return place_descriptors

# ----------------------------------------------------------------GEMINI API----------------------------------------------------------------------
def call_gemini_api(prompt):
    """
    Call the Gemini API with the given prompt.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No Gemini API key provided. Set the GEMINI_API_KEY environment variable")
    
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    params = {
        "key": api_key
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.8,
            "topK": 40,
            "maxOutputTokens": 8192
        }
    }
    
    response = requests.post(url, headers=headers, params=params, json=data)
    
    if response.status_code != 200:
        raise Exception(f"Failed to call Gemini API. Received: {response.status_code} {response.reason} - {response.text}")
    
    response_json = response.json()
    
    # Extract the text from the response
    if "candidates" in response_json and len(response_json["candidates"]) > 0:
        if "content" in response_json["candidates"][0] and "parts" in response_json["candidates"][0]["content"]:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
    
    return "No response generated."

# ----------------------------------------------------------------Knowledge Extraction with Gemini----------------------------------------------------------------------
def extract_knowledge_from_gemini(destination):
    """
    Extract structured knowledge about a destination using Gemini API.
    Returns a list of dictionaries with relationship triples.
    """
    # First, get descriptive information about the places
    place_descriptors = get_wiki_desc_for_places(destination)
    
    # Now ask Gemini to structure this into a TSV format
    extraction_prompt = f"""Based on the following information about tourist attractions in {destination}, extract a highly detailed knowledge graph in TSV format that captures diverse relationships between attractions, their history, significance, and travel-related insights.
    {place_descriptors}

    Format:
    Create a TSV with the following columns:

    Node_1: The name of the entity (e.g., attraction, person, event, historical figure, location, year).
    Relation: The relationship between Node_1 and Node_2 (e.g., LOCATED_IN, BUILT_IN, KNOWN_FOR, DESIGNED_BY, INFLUENCED_BY, HAS_EVENT, CULTURAL_IMPORTANCE, RECOMMENDED_ACTIVITY).
    Node_2: The entity that Node_1 is related to.
    Node_1_Type: The type of Node_1 (e.g., Attraction, Landmark, Event, Architect, Year, Culture, TravelTip).
    Node_2_Type: The type of Node_2 (e.g., Location, AttractionType, Architect, Year, CulturalAspect, RecommendedActivity).
    Attributes: A JSON string with additional information (e.g., opening hours, ticket price, notable facts, visiting tips).
    Guidelines:

    Extract at least 8 relationships per attraction to create a dense knowledge graph.
    Include core travel-related information such as:
    Best time to visit (e.g., "Eiffel Tower" → BEST_VISITED_IN → "Evening")
    Famous events held there (e.g., "Sydney Opera House" → HOSTS_EVENT → "Vivid Sydney Festival")
    Recommended activities (e.g., "Grand Canyon" → RECOMMENDED_ACTIVITY → "Hiking")
    Nearby attractions (e.g., "Louvre Museum" → NEARBY_ATTRACTION → "Seine River")
    Historical significance (e.g., "Colosseum" → HISTORIC_IMPORTANCE → "Gladiator battles")
    Influences (e.g., "Taj Mahal" → INFLUENCED_BY → "Mughal Architecture")
    Travel insights (e.g., "Machu Picchu" → TRAVEL_TIP → "Get tickets in advance")
    Ensure each attraction is connected to broader travel concepts, such as:
    The country it belongs to
    Related UNESCO heritage status (if applicable)
    Any notable designers, rulers, or figures associated with it
    Instructions for Output:

    Just return the TSV content without markdown formatting or extra text.
    The first line should be the header row."""

    tsv_content = call_gemini_api(extraction_prompt)
    
    # Clean up the response to ensure it's just TSV content
    if "```" in tsv_content:
        # Extract content between triple backticks if present
        tsv_content = tsv_content.split("```")[1].strip()
        if tsv_content.startswith("tsv"):
            tsv_content = tsv_content[3:].strip()
    
    return tsv_content

# ----------------------------------------------------------------Knowledge Pandas Dataframe----------------------------------------------------------------------

def create_travel_knowledge_dataframe(destination_location: str) -> pd.DataFrame:
    """
    Create a DataFrame containing travel knowledge about places in the specified destination
    using the Gemini API.
    """
    print(f"Creating travel knowledge graph for {destination_location}...")
    
    # Get TSV content from Gemini
    tsv_content = extract_knowledge_from_gemini(destination_location)
    
    # Convert TSV string to DataFrame
    df = pd.read_csv(io.StringIO(tsv_content), sep='\t')
    
    # Handle any necessary data cleaning
    if 'Attributes' in df.columns:
        # Ensure Attributes is a valid JSON string
        df['Attributes'] = df['Attributes'].apply(lambda x: '{}' if pd.isna(x) or x == '' else x)
        
        # Verify JSON formatting
        def ensure_json(attr_str):
            try:
                # If it's already a JSON object, convert to string
                if isinstance(attr_str, dict):
                    return json.dumps(attr_str)
                # Try to parse as JSON to validate
                json.loads(attr_str)
                return attr_str
            except:
                # If not valid JSON, return empty object
                return '{}'
        
        df['Attributes'] = df['Attributes'].apply(ensure_json)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['Node_1', 'Relation', 'Node_2'])
    
    return df

def sanitize_key(name):
    """Converts a name into a valid _key for ArangoDB."""
    name = name.lower().strip()  # Ensure consistent casing and remove trailing spaces
    name = re.sub(r'[^a-z0-9_-]', '_', name)  # Replace invalid characters
    return name

# ----------------------------------------------------------------Knowledge Graph from Dataframe----------------------------------------------------------------------

def generate_knowledge_graph(G, destination):
    # Debug statement: Print the number of nodes and edges in the input graph
    print(f"\nInput graph before modification: {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # destination = "Varanasi"  # Change this to any destination you want
    df = create_travel_knowledge_dataframe(destination)
    
    # Display the first few rows of the DataFrame
    print("\nSample of the knowledge graph data:")
    print(df.head(2).to_string())
    
    # Track how many new elements we're adding
    nodes_added = 0
    edges_added = 0
    
    for _, row in df.iterrows():
        # Sanitize keys for ArangoDB
        node1_key = sanitize_key(row['Node_1'])
        node2_key = sanitize_key(row['Node_2'])

        # Check if nodes already exist before adding them
        if not G.has_node(node1_key):
            G.add_node(node1_key, key=node1_key, name=row['Node_1'], type=row['Node_1_Type'])
            nodes_added += 1
        
        if not G.has_node(node2_key):
            G.add_node(node2_key, key=node2_key, name=row['Node_2'], type=row['Node_2_Type'])
            nodes_added += 1

        # Check if edge already exists before adding it
        if not G.has_edge(node1_key, node2_key):
            G.add_edge(node1_key, node2_key, relation=row['Relation'], attributes=row['Attributes'])
            edges_added += 1
    
    print(f"\nAdded {nodes_added} new nodes and {edges_added} new edges")
    print(f"Output graph after modification: {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    return G

# ----------------------------------------------------------------Knowledge Graph Plot----------------------------------------------------------------------

def plot_knowledge_graph(destination):
    G = generate_knowledge_graph(G,destination)
    plt.figure(figsize=(20, 15))

    # Define node positions
    pos = nx.spring_layout(G, seed=42)

    # Draw nodes with labels
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color="lightblue", edge_color="gray")

    # Draw edge labels (relationship types)
    edge_labels = {(u, v): d['relation'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

    plt.title("Knowledge Graph from LLM-Generated Table")
    plt.show()

# --------------------------------------------------------Gateway to Create KG if not Exists------------------------------------------------------
def fetch_or_create_city(city_name, existing_city_names, G):
    """
    Fetches or creates a city in the graph database based on the list of existing city names..
    """
    try:
        if city_name in existing_city_names:
            print("City already exists in the database")
            return G
        else:
            G = generate_knowledge_graph(G, city_name)
            print("City created successfully")
            return G
    except Exception as e:
        raise Exception(f"Error executing graph operation: {str(e)}")

# ----------------------------------------------------------------Add Selected key to places object----------------------------------------------------------------------

def add_selected_key_to_places(places_google_maps, extracted_list):
    """
    Add 'selected' as a key to Google maps generated list of places.
    
    Args:
        places_google_maps (list): List of places from Google Maps
        extracted_list (list): List of selected places
        
    Returns:
        list: Modified places
    """
    modified_places = []
    for place in places_google_maps:
        if place["name"] in extracted_list:
            modified_place = place.copy()
            modified_place["selected"] = True
            modified_places.append(modified_place)
    return modified_places

# ----------------------------------------------------------------Use User Input to filter places----------------------------------------------------------------------

def get_top_k_places(input_data, existing_city_names, G):
    """
    Retrieves the top K places based on the user's input data.

    Args:
        input_data (dict): The user's input data containing destination, budget, interests, etc.
        existing_city_names (list): List of existing city names in the database
        G (nx.Graph): NetworkX graph representing the knowledge graph
    
    Returns:
        list: A list of modified places recommended for the user.
    """
    # Check if the city exists in the database, and the Knowledge Graph has substantial knowledge about it.
    G = fetch_or_create_city(input_data["destination"], existing_city_names, G)

    # Fetch all places based on the city, country, state.
    places_google_maps = get_maps_places(input_data["destination"], "Most Popular places in ")
    sz = len(places_google_maps)
    places_ext = []
    results_retrieved = []

    for i in range(sz):
        place_name = places_google_maps[i]["name"].replace('"', '')
        place_key = sanitize_key(place_name)  # Use sanitized key
        print(place_key)
        places_ext.append(place_name)

        # For nxadb graphs, use this approach
        try:
            # Try to get node data - this will raise an exception if the node doesn't exist
            node_data = G.nodes[place_key]
            print(f"Found node {place_key} in graph")
        except (KeyError, ValueError) as e:
            print(f"Node {place_key} not found in graph: {str(e)}")
            results_retrieved.append(f'Node "{place_name}" was not found in the knowledge graph.')
            continue
        # Query the graph for relationships
        try:
            for path_length in range(1, 4):
                try:
                    for node in nx.single_source_shortest_path_length(G, place_key, cutoff=path_length):
                        if node != place_key:
                            try:
                                path = nx.shortest_path(G, place_key, node)
                                
                                relationships = []
                                for j in range(len(path) - 1):
                                    edge_data = G.get_edge_data(path[j], path[j+1])
                                    if edge_data and 'relation' in edge_data:
                                        relationships.append(edge_data['relation'])
                                
                                start_node_type = G.nodes.get(place_key, {}).get('type', 'unknown type')
                                end_node_name = G.nodes.get(node, {}).get('name', 'unknown')
                                end_node_type = G.nodes.get(node, {}).get('type', 'unknown type')

                                sentence = (f'Node "{place_name}, a {start_node_type}" is connected to '
                                            f'Node "{end_node_name}, a {end_node_type}" by the '
                                            f'relationships: "{", ".join(relationships)}".')
                                print(sentence)
                                results_retrieved.append(sentence)
                            except nx.NetworkXNoPath:
                                continue
                except nx.NodeNotFound:
                    continue
        except Exception as e:
            print(f"Error processing place '{place_name}': {str(e)}")
            results_retrieved.append(f'Error processing relationships for "{place_name}": {str(e)}')

    if not results_retrieved:
        results_retrieved.append("No relationship data could be retrieved from the knowledge graph for the given places.")

    retriever = f"""You are given a list of places and related details extracted from a Knowledge Graph. Your task is to recommend specific places based on the user's destination, budget, and interests. 
                    Filter the relevant places from the data and return a JSON list containing only the exact names of the places, ensuring that the recommendations align with the user's preferences.

                    USER Data:
                    Total list of places: {places_ext}
                    Source information: {input_data["source"]}
                    Destination: {input_data["destination"]}
                    Departure Date: {input_data["departureDate"]}
                    Return Date: {input_data["returnDate"]}
                    Budget: {input_data["budget"]}
                    Description of the user's interests: {input_data["description"]}

                    Knowledge Graph Data:
                    {results_retrieved}
                    """

    try:
        json_list_of_places = call_gemini_api("You are a travel expert and your task is to recommend specific places based on the user's destination, budget, and interests." + retriever)

        # Handle potential format issues with the API response
        try:
            extracted_list_string = json_list_of_places.strip()
            
            if "```" in json_list_of_places:
                extracted_list_string = json_list_of_places.split("```")[1].strip()
                if extracted_list_string.startswith("json"):
                    extracted_list_string = extracted_list_string[4:].strip()
            else:
                json_pattern = r'\[\s*"[^"]*"(?:\s*,\s*"[^"]*")*\s*\]'
                match = re.search(json_pattern, json_list_of_places)
                if match:
                    extracted_list_string = match.group(0)
            
            extracted_list = json.loads(extracted_list_string)
        except (json.JSONDecodeError, IndexError) as e:
            print(f"Error parsing API response: {str(e)}")
            extracted_list = places_ext  # Fallback to all places if parsing fails

        modified_places = add_selected_key_to_places(places_google_maps, extracted_list)
        return modified_places, G
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return places_ext, G  # Return all places if API call fails


# ------------------------------------------------------ Event Planner ------------------------------------------------------ 

def event_planner(selected_places, user_input):
    """
    Plans a series of events for a group of tourists based on selected places and user input.

    Args:
        selected_places (str): A string containing the list of places selected by the user.
        user_input (str): Additional user input to customize the event plan.
    
    Returns:
        list: A list of event plan dictionaries containing details such as place ID, name, 
              details, timing, famous activities, total duration, recommended transport, 
              and additional notes.

    The function generates a prompt combining the user input and selected places, then uses 
    an AI text generation function to create a detailed event plan. The response is parsed 
    into a list of event plans and returned.
    """

    demo = '''[
                {
                  "place_id": 0,
                  "name": "Burj Khalifa",
                  "details": "The Burj Khalifa is the tallest building in the world and a major attraction. Start your day early to avoid long queues for the observation deck.",
                  "timing": "9:00 AM to 10:30 AM"
                  "Famous Activity": "Photoshoots",
                  "total_duration": "1-2 hours",
                  "recommended_transport": "Taxi",
                  "additional_notes": "Grab a pair of glasses and a camera. Dress nicely and bring water."
                },
                ...
                {
                  "place_id": 4,
                  "name": "Downtown Dubai Park",
                  "details": "Visit another park or green space to enjoy the peaceful environment.",
                  "timing": "1:00 PM to 4:45 PM",
                  "Famous Activity": "Swimming",
                  "total_duration": "4-5 hours",
                  "recommended_transport": "Walking",
                  "additional_notes": "Grab a snack or lunch at Dubai Mall or nearby cafes. Dress comfortably and bring water, especially for outdoor activities."
                } 
              ]'''
    prompt = (user_input + "Plan a series of events that will provide a memorable experience for the group. The group is interested in exploring the places listed below.\n Selected Places:" + selected_places + "\nReturn a smart plan in the form of a 'JSON list of the same structure' containing the events and activities that the group should participate in. Ensure that the plan includes the total number of places to visit, the locations, details, timings, famous activities, total duration, recommended transport, and additional notes." + demo)
              
    response = call_gemini_api("You are an event planner and your task is to plan a series of events for a group of tourists.", prompt)
    resp = response.split("```")[1].strip()
    event_list = json.loads(resp)
    return event_list

# ## MAIN CODE

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
PLACES_FILE  = "existing_places.json"

# Function to load places from JSON
def load_places():
    with open(PLACES_FILE, "r") as file:
        return json.load(file)

# Function to add a new place and save
def add_place(name):
    places = load_places()
    if({"name": name} not in places):
        places.append({"name": name})

    with open(PLACES_FILE, "w") as file:
        json.dump(places, file, indent=4)

# Endpoint to get all places
@app.route("/api/places", methods=["GET"])
def get_places():
    with open(PLACES_FILE, "r") as file:
        places = json.load(file)
    city_names = [place["name"] for place in places]  # Extract city names
    return jsonify(city_names)

@app.route('/api/top-places', methods=['POST'])
def top_places():

    db = ArangoClient(hosts="https://72f3bc481376.arangodb.cloud:8529").db(username="root", password="jznyCFlCYCwMCH5q2wV8", verify=True)
    G = nxadb.Graph(name="TravelMate", db=db)
    # existing_city_names = ["Varanasi", "Bombay", "Kolkata"]
    places = load_places()
    existing_city_names = [place["name"] for place in places]
    print(existing_city_names)
    """
    REST API endpoint to get top places based on user data
    """
    # Get user data from request
    user_data = request.json
    destination_name = user_data['destination']

    if not user_data:
        return jsonify({"error": "No user data provided"}), 400
    
    # Get top places based on user data
    places, updated_G = get_top_k_places(user_data, existing_city_names, G)
    add_place(destination_name)
    G = updated_G
    
    # Return the places
    return jsonify({"places": places})

@app.route("/api/event-planner", methods=["POST"])
def api_event_planner():
    """Handle event planner requests"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    selected_places = data.get("selectedPlaces", "")
    user_input = data.get("userInput", "")
    
    if not selected_places or not user_input:
        return jsonify({"error": "Missing required parameters: selectedPlaces or userInput"}), 400
    
    try:
        print(selected_places)
        print(user_input)
        result = event_planner(selected_places, user_input)
        print(result)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = 5000
    print(f"Starting Flask server on port {port}")
    app.run(debug=True, port=port, host='0.0.0.0')

