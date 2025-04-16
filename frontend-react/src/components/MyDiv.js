// src/App.js
import React from 'react';
import "./MyDiv.css";

function MyDiv({text}) {
    return(
        <div>
          <h1 style={ {color: text.color} }>{text.content}</h1>
        </div>
    );
}

export default MyDiv;
