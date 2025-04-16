// src/App.js
import React from 'react';
import "./ComponentPage1.css";
import MyDiv from './MyDiv.js';
import MyText from './MyText.js';


function ComponentPage1() {
    return (
      <>
          <MyDiv text={{color: 'orange', content: 'This is the content of Page1'}}/>
          <MyText />
          <MyText />
      </>
    );
};

export default ComponentPage1;
