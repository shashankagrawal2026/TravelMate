# TravelMate - AI-Powered Travel Recommendation System

<div align="center">
  <img src="TravelMate_Frontend-main/public/images/logo_main.png" alt="TravelMate Logo" width="200"/>
  
  **Your Personal Travel Guide**
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
  [![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg)](https://reactjs.org)
  [![Flask](https://img.shields.io/badge/Flask-Latest-000000.svg)](https://flask.palletsprojects.com)
  [![Neo4j.](https://img.shields.io/badge/Neo4j.-Graph_Database-red.svg)](https://Neo4j..com)
</div>

## 🌟 Overview

TravelMate is an intelligent travel recommendation system that combines the power of **Knowledge Graphs**, **AI/ML algorithms**, and **real-time APIs** to provide personalized travel recommendations. The system leverages Neo4j. for graph database operations, Google Maps API for location data, Wikipedia API for enriched content, and Gemini AI for intelligent event planning.

### 🚀 Key Features

- **🎯 Smart Destination Discovery**: AI-powered place recommendations based on user preferences
- **📊 Knowledge Graph Integration**: Rich contextual information using Neo4j. graph database
- **🗺️ Real-time Location Data**: Integration with Google Maps API for accurate place information
- **📖 Wikipedia Integration**: Detailed descriptions and historical context for recommended places
- **🤖 AI Event Planning**: Gemini AI-powered itinerary generation
- **📱 Modern Web Interface**: Responsive React.js frontend with intuitive user experience
- **🔄 Real-time Processing**: Flask backend with CORS support for seamless API communication

## 🏗️ Architecture

```
TravelMate/
├── TravelMate_Backend-main/          # Flask API Server
│   ├── main.py                       # Main application entry point
│   ├── Solution.ipynb                # Jupyter notebook for development/testing
│   ├── requirements.txt              # Python dependencies
│   ├── existing_places.json          # Pre-loaded destination data
│   └── README.md                     # Backend documentation
└── TravelMate_Frontend-main/         # React Web Application
    ├── public/                       # Static assets and images
    ├── src/                          # React source code
    │   ├── Components/               # Reusable React components
    │   │   ├── homePage/            # Landing page component
    │   │   ├── placeSelector/       # Place selection interface
    │   │   ├── eventPlanner/        # Itinerary planning component
    │   │   ├── header/              # Navigation header
    │   │   └── modal/               # Modal dialogs
    │   ├── App.js                   # Main React app component
    │   └── index.js                 # Application entry point
    ├── package.json                 # Node.js dependencies
    └── README.md                    # Frontend documentation
```

## 🛠️ Technology Stack

### Backend

- **Python 3.8+** - Core programming language
- **Flask** - Web framework for REST APIs
- **Neo4j.** - Graph database for knowledge storage
- **NetworkX** - Graph analysis and manipulation
- **Pandas & NumPy** - Data processing and analysis
- **LangChain** - LLM integration framework
- **Google Maps API** - Location and place data
- **Wikipedia API** - Enriched content retrieval
- **Gemini AI** - Intelligent event planning

### Frontend

- **React 18.3.1** - User interface framework
- **React Router** - Client-side routing
- **Bootstrap 5.3** - UI component library
- **Material-UI** - Modern React components
- **SCSS** - Enhanced CSS preprocessing

### APIs & Services

- **Google Maps Places API** - Location data
- **Wikipedia API** - Content enrichment
- **Gemini AI API** - AI-powered recommendations
- **Neo4j. Cloud** - Managed graph database

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher**
- **Node.js 16.0 or higher**
- **npm or yarn package manager**
- **Git** (for cloning the repository)

### Required API Keys

1. **Google Maps API Key** - For place data and geocoding
2. **Gemini AI API Key** - For AI-powered recommendations
3. **Neo4j. Cloud Account** - For graph database access

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd TravelMate
```

### Step 2: Backend Setup

#### 2.1 Navigate to Backend Directory

```bash
cd TravelMate_Backend-main
```

#### 2.2 Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2.4 Environment Configuration

Create a `.env` file in the backend directory:

```env
# Google Maps API Configuration
GEMINI_API_KEY=your_google_maps_api_key_here

# Gemini AI Configuration
GEMINI_AI_API_KEY=your_gemini_ai_api_key_here

# Neo4j. Configuration (Update with your credentials)
ARANGO_HOST=https://72f3bc481376.Neo4j..cloud:8529
ARANGO_USERNAME=root
ARANGO_PASSWORD=your_Neo4j._password
ARANGO_DATABASE=TravelMate
```

#### 2.5 Update Neo4j. Configuration

In `main.py`, update the Neo4j. connection details:

```python
# Line 556 in main.py - Update with your Neo4j. credentials
db = ArangoClient(hosts="your_Neo4j._host").db(
    username="your_username",
    password="your_password",
    verify=True
)
```

#### 2.6 Initialize Database

Ensure `existing_places.json` contains initial city data:

```json
[{ "name": "Varanasi" }, { "name": "Delhi" }, { "name": "Bombay" }]
```

### Step 3: Frontend Setup

#### 3.1 Navigate to Frontend Directory

```bash
cd ../TravelMate_Frontend-main
```

#### 3.2 Install Node.js Dependencies

```bash
npm install
```

## 🎮 Running the Application

### Method 1: Development Mode

#### Start Backend Server

```bash
cd TravelMate_Backend-main
python main.py
```

Backend will be available at: `http://localhost:5000`

#### Start Frontend Development Server

```bash
cd TravelMate_Frontend-main
npm start
```

Frontend will be available at: `http://localhost:3000`

### Method 2: Using Jupyter Notebook (Alternative)

For backend development and testing:

```bash
cd TravelMate_Backend-main
jupyter notebook Solution.ipynb
```

## 🔧 API Endpoints

### Backend REST API

| Endpoint             | Method | Description                            | Parameters                                   |
| -------------------- | ------ | -------------------------------------- | -------------------------------------------- |
| `/api/places`        | GET    | Get all available cities               | None                                         |
| `/api/top-places`    | POST   | Get recommended places for destination | `{destination, source, budget, description}` |
| `/api/event-planner` | POST   | Generate AI-powered itinerary          | `{selectedPlaces, userInput}`                |

### Example API Usage

#### Get Top Places

```javascript
POST /api/top-places
Content-Type: application/json

{
  "destination": "Delhi",
  "source": "Mumbai",
  "budget": "50000",
  "description": "Looking for historical and cultural experiences"
}
```

#### Generate Itinerary

```javascript
POST /api/event-planner
Content-Type: application/json

{
  "selectedPlaces": "Red Fort, India Gate, Lotus Temple",
  "userInput": "3-day trip for family with kids, prefer morning activities"
}
```

## 📱 User Workflow

### 1. Home Page

- Users enter travel preferences:
  - Source and destination cities
  - Travel dates
  - Budget constraints
  - Trip description and preferences

### 2. Place Selection

- System displays AI-recommended places based on:
  - Knowledge graph analysis
  - User preferences
  - Popular destinations from Google Maps
  - Wikipedia-enriched descriptions

### 3. Itinerary Planning

- Users select preferred places
- AI generates detailed itinerary including:
  - Optimal visit order
  - Time allocations
  - Transportation recommendations
  - Activity suggestions

## 🧠 Knowledge Graph Features

### Graph Database Operations

- **Node Types**: Cities, Places, Activities, Historical Events
- **Relationships**: Located_in, Related_to, Recommended_for
- **3-Hop Analysis**: Discovers related entities within knowledge graph
- **Dynamic Updates**: Automatically adds new cities and places

### AI-Powered Enrichment

- **Contextual Information**: Historical significance, cultural aspects
- **Relationship Discovery**: Connected attractions and activities
- **Preference Matching**: Aligns recommendations with user interests

## 🎨 Frontend Features

### Responsive Design

- **Mobile-first approach** with Bootstrap 5
- **Modern UI components** using Material-UI
- **Custom SCSS styling** for brand consistency

### Component Structure

- **HomePage**: Landing page with user input forms
- **PlaceSelector**: Interactive place selection interface
- **ItineraryPlanner**: AI-generated itinerary display
- **Modal**: Detailed place information dialogs

## 🔍 Troubleshooting

### Common Issues

#### Backend Issues

1. **Neo4j. Connection Error**

   ```
   Solution: Verify Neo4j. credentials and network connectivity
   ```

2. **API Key Issues**

   ```
   Solution: Ensure all API keys are properly set in .env file
   ```

3. **Package Installation Errors**
   ```bash
   # Try upgrading pip
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

#### Frontend Issues

1. **Node.js Version Compatibility**

   ```bash
   # Check Node.js version
   node --version
   # Should be 16.0 or higher
   ```

2. **CORS Issues**
   ```
   Solution: Ensure Flask-CORS is properly configured in backend
   ```

### Debug Mode

Enable debug mode for detailed error logging:

```python
# In main.py
app.run(debug=True, port=5000, host='0.0.0.0')
```

## 🚀 Deployment

### Backend Deployment

- **Production WSGI Server**: Use Gunicorn for production deployment
- **Environment Variables**: Secure API keys using environment configuration
- **Database**: Ensure Neo4j. is properly configured for production

### Frontend Deployment

```bash
npm run build
# Deploy the build/ directory to your web server
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Neo4j.** for graph database capabilities
- **Google Maps API** for location data
- **Wikipedia** for enriched content
- **Gemini AI** for intelligent recommendations
- **React & Flask Communities** for excellent documentation

## 📞 Support

For support and questions:

- Create an issue in the repository
- Check existing documentation
- Review API documentation for troubleshooting

---

<div align="center">
  <strong>Built with ❤️ for travelers by travelers</strong>
</div>
