# TravelMate-Frontend

# Knowledge Graph Travel Recommendation System
This project implements a travel recommendation system that leverages a knowledge graph to provide users with enriched information about popular places.

## Features
City and Place Lookup:

- Verifies user-specified destination city existence within the knowledge graph.
- Retrieves popular places from the Google Maps API for the chosen city.

## Knowledge Graph Enrichment:

- For each retrieved place, the system queries the knowledge graph to discover related entities within 3 hops.
- This provides richer context about points of interest, such as historical significance, nearby attractions, or cultural aspects.

## Sentence Generation (Placeholder):

- The system currently builds basic sentences describing the first relationship found in the knowledge graph for each place.
- Future updates will incorporate more complex sentence generation based on retrieved relationships and properties.

## Future Development
- User Preference Integration:
- Implement functionality to capture user preferences (e.g., historical interests, outdoor activities, culinary experiences).

## GPT Recommendation Generation:

- Use a pre-trained language model (GPT) to create a descriptive JSON list of recommended places based on user preferences and enriched information.

# Selection Handling:

Integrate a feature to allow users to specify their interests from the list of enriched places.
Update the recommended places list based on user selections.
Error Handling and Scalability:

Implement comprehensive error handling for API calls and knowledge graph queries.
Optimize Cypher queries and result processing for improved performance with larger knowledge graphs.
Dependencies
This project relies on the following external libraries:

Google Maps API
Knowledge Graph Client (specific library dependent on your chosen knowledge graph implementation)

# In the project directory, you can run:
### `npm i`

### `npm start`

Runs the app in the development mode.
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.