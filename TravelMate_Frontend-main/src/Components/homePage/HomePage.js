import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import "../../styles.css";
import "./HomePage.css";
import Header from "../header/Header";
import TextBox from "../textBox/TextBox";
const HomePage = () => {
    const navigate = useNavigate();

    const [userData, setUserData] = useState({
        source: "",
        destination: "",
        departureDate: null,
        returnDate: null,
        budget: "",
        description: "",
    });
    // Callback to update userData from TextBox
    const updateUserData = (newUserData) => {
        setUserData(newUserData);
    };


    // Function to navigate with state
    const goToPlaceSelector = () => {
        navigate('/place-selector', {
            state: {
                userData: userData,
            },
        });
    };
    return (
        <>
            <div className="banner-text">
                <Header />
                <TextBox updateUserData={updateUserData} />
                <button onClick={goToPlaceSelector} className="btn btn-primary">Recommend Places</button>
            </div>
        </>
    );
};

export default HomePage;
