// src/App.js
import React from 'react';
import "./MyText.css";


function MyText() {
    return(
        <div>
            <h1>This is the composite component MyText</h1>
            <div>
              <label>Enter your name:</label>
              <input type="text"></input>
            </div>
        </div>
    );
}

export default MyText;
