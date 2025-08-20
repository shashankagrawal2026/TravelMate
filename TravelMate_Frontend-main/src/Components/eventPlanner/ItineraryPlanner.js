import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import EventCards from "../eventCards/EventCards";
import './ItineraryPlanner.css';

const ItineraryPlanner = () => {
  const location = useLocation();
  const { selectedPlacesIds, places, userData } = location.state || {};
  const [fetchedPlan, setFetchedPlan] = useState([]); // State for fetched plan
  const [isLoading, setIsLoading] = useState(true); // Loading state

  // Get the selected place objects
  const selectedPlaces = (places || []).filter((place) =>
    selectedPlacesIds?.includes(place.place_id)
  );

  useEffect(() => {
    if (!selectedPlaces || !userData) {
      setIsLoading(false); // No data to fetch, stop loading
      return;
    }

    // Build the statement from selected places
    let statement = selectedPlaces
      .map((place) => {
        let details = `NAME: '${place.name}' is located in ${place.address}, and has a rating of ${place.rating}. It was chosen by the user`;
        if (place.types && place.types.length > 0) {
          const reasons = place.types.join(", ");
          details += ` because of the following reasons: ${reasons}`;
        }
        return details;
      })
      .join("\n");

    const userInput = `You are an event planner and your task is to plan a series of events for a group of tourists visiting the region of ${userData.destination} between ${userData.departureDate} to ${userData.returnDate}. They have a budget of ${userData.budget}, so plan accordingly.`;

    const fetchEventPlan = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/event-planner", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            selectedPlaces: statement,
            userInput: userInput,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setFetchedPlan(data || []); // Update state with fetched data
      } catch (error) {
        console.error("Error fetching event plan:", error);
      } finally {
        setIsLoading(false); // Stop loading state
      }
    };

    fetchEventPlan(); // Fetch event plan when component mounts
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array to run only once when mounted

  return (
    <div className="event-planner-container">
      <header className="custom-header-event navbar navbar-expand-lg navbar-light sticky-top">
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

      <div className="event-planner-content">
        {isLoading ? (
          // <div className="loading-container text-center my-5">
          //   <img
          //     src="/images/loading.gif"
          //     alt="Loading..."
          //     className="loading-animation"
          //     style={{ width: "100px", height: "100px" }}
          //   />
          //   <p className="mt-3">Creating your personalized itinerary...</p>
          // </div>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',  // Full viewport height
            width: '100%',    // Full width
        }}>
            <img src="images/loading-animation.svg" alt="Loading..." style={{ height: 500, opacity: 0.8 }} />
        </div>
             
        ) : (
          <div className="itinerary-container">
            <h2 className="text-center mb-4" style={{ color: 'whitesmoke', fontWeight: "bold" }}>Your Travel Itinerary</h2>
            <div className="itinerary-timeline">
              {fetchedPlan.map((event, index) => (
                <div key={index} className="itinerary-item">
                  <div className="event-card-wrapper">
                    <div className="event-card">
                      <EventCards 
                        locations={[event]} 
                        indexPrint={index}
                        selectedPlaces={selectedPlaces} 
                      />
                    </div>
                  </div>

                  {index < fetchedPlan.length - 1 && (
                    <div className="arrow-container">
                      <div className="animated-arrow">
                        <svg width="40" height="100" xmlns="http://www.w3.org/2000/svg">
                          <defs>
                            <linearGradient id={`arrowGradient-${index}`} x1="0%" y1="0%" x2="0%" y2="100%">
                              <stop offset="0%" stopColor="#4e54c8" stopOpacity="0.8">
                                <animate attributeName="stopOpacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite" />
                              </stop>
                              <stop offset="100%" stopColor="#8f94fb" stopOpacity="0.9">
                                <animate attributeName="stopOpacity" values="0.9;1;0.9" dur="2s" repeatCount="indefinite" />
                              </stop>
                            </linearGradient>
                          </defs>
                          <path
                            d="M20,5 L20,75 M8,65 L20,85 L32,65"
                            stroke={`url(#arrowGradient-${index})`}
                            strokeWidth="5"
                            fill="none"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ItineraryPlanner;