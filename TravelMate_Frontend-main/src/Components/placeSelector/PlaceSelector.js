import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Card from "../card/Card";
import "../../styles.css";
import "./PlaceSelector.css";
import Modal from "../modal/Modal";

let API_KEY = process.env.REACT_APP_MAPS_API_KEY;
const PlaceSelector = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { userData } = location.state || {};
    const [selectedPlacesIds, setSelectedPlacesIds] = useState([]);
    const [places, setPlaces] = useState([]); 
    const [isLoading, setIsLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalContent, setModalContent] = useState(null);
    console.log("places selected", selectedPlacesIds)
    // Function to fetch places from REST API
    useEffect(() => {
        const fetchPlaces = async (userData) => {
            try {
                const response = await fetch('http://localhost:5000/api/top-places', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(userData),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();
                const fetchedPlaces = data.places || [];
                setPlaces(fetchedPlaces);
                console.log("Places fetched:", fetchedPlaces);
                // Set the selected places based on the 'selected' property of places
                const initialSelectedPlacesIds = fetchedPlaces
                    .filter(place => place.selected == 1)
                    .map(place => place.place_id);
                setSelectedPlacesIds(initialSelectedPlacesIds);

                console.log("Places fetched:", fetchedPlaces);
                setIsLoading(false);
            }
            catch (error) {
                console.error("Error fetching places:", error);
                setIsLoading(false);
            }
        };
        
        fetchPlaces(userData);
    }, [userData]);

    // Handle selecting/deselecting places
    const handleSelectPlace = (id) => {
        // Update places array to toggle the selected property
        setPlaces(prevPlaces =>
            prevPlaces.map(place =>
                place.place_id == id 
                    ? { ...place, selected: place.selected == 1 ? 0 : 1 } 
                    : place
            )
        );
    
        // Update selectedPlacesIds array
        setSelectedPlacesIds(prev =>
            prev.includes(id) 
                ? prev.filter(placeId => placeId != id) 
                : [...prev, id]
        );
    };
    
    const handleItineraryPlannerClick = () => {
        if (selectedPlacesIds.length === 0) {
            alert("Choose at least 1 place to visit!");
            return;
        }
        
        navigate("/event-planner", { 
            state: { 
                selectedPlacesIds: selectedPlacesIds, 
                places: places, 
                userData: userData 
            } 
        });
        console.log("Selected places:", selectedPlacesIds);
    };

    const openModal = (place) => {
        setModalContent(place);
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setModalContent(null);
    };

    return (
        <div className="stylecontainer" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <header className="custom-header-places navbar navbar-expand-lg navbar-light">
                <div className="container-fluid">
                    <div className="navbar-brand logo">
                        <img
                            src="/images/logo_main.png"
                            alt="TravelMate"
                            className="logo-img"
                        />
                    </div>
                    <div className="title">
                        <p>Your Personal Travel Guide</p>
                    </div>

                    <div className="d-flex align-items-center">
                        <button className="btn btn-outline-primary me-2">Register</button>
                        <button className="btn btn-primary me-2">Login</button>
                        <div className="form-check form-switch me-3">
                            <input
                                className="form-check-input"
                                type="checkbox"
                                id="darkModeSwitch"
                            />
                        </div>
                    </div>
                </div>
            </header>

            <main className="places-list">
                {isLoading ? (
                    <img src="images/loading-animation.svg" alt="Loading..." style={{height:500, opacity:0.8}}/>
                ) : (
                    <div className="card-container">
                        {places.length === 0 ? (
                            <p>No places found.</p>
                        ) : (
                            places.map((place) => {
                                let photoReference = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRq7tDgp_TYwdGlzX5KjF8KTQzJh8zQp6ow2g&s";
                                try {
                                    if (place.photos) {
                                        photoReference = place.photos[0]['photo_reference'];
                                    }
                                } catch (error) {
                                    console.error("Error parsing photo data:", error);
                                }
                                return (
                                <Card
                                    key={place.place_id}
                                    title={place.name}
                                    description={place.formatted_address}
                                    rating={place.rating}
                                    onDetails={() => openModal(place)}
                                    image={place.photos ? `https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=${photoReference}&key=${API_KEY}` : "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRq7tDgp_TYwdGlzX5KjF8KTQzJh8zQp6ow2g&s"}
                                    isSelected={place.selected == 1}
                                    onSelect={() => handleSelectPlace(place.place_id)}
                                />
                            )})
                        )}
                    </div>
                )}

                <Modal isOpen={isModalOpen} onClose={closeModal}>
                    {modalContent && (
                        <div>
                            <h2><b>{modalContent.name}</b></h2>
                            <p><b>Address:</b> {modalContent.formatted_address}</p>
                            <div className="rating">
                                <p>Rated {modalContent.rating}/5</p>
                                <img src="https://cdn-icons-png.flaticon.com/512/276/276020.png" style={{height:"20px", width: "20px", marginRight:"10px"}}/>
                                <p> by {modalContent.user_ratings_total} people.</p>
                            </div>
                            <p>Known For: {modalContent.types.map(element => element).join(", ")}</p>

                            <iframe
                                width="450"
                                height="300"
                                frameBorder="0"
                                referrerPolicy="no-referrer-when-downgrade"
                                src={`https://www.google.com/maps/embed/v1/place?key=${process.env.REACT_APP_MAPS_API_KEY}&q=${encodeURIComponent(modalContent.formatted_address)}`}
                                allowFullScreen>
                            </iframe>
                        </div>
                    )}
                </Modal>

                <div className="event-planner-section">
                    <button
                        className={`event-planner-btn ${selectedPlacesIds.length < 1 ? "disabled" : ""}`}
                        onClick={handleItineraryPlannerClick}
                        disabled={selectedPlacesIds.length < 1}
                    >
                        Itinerary Planner
                    </button>
                </div>
            </main>
        </div>
    );
};

export default PlaceSelector;