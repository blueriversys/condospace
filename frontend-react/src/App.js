// src/App.js
import React from 'react';
import "./App.css";
import MyDiv from '../src/components/MyDiv.js';
import MyText from '../src/components/MyText.js';

function App() {
    return (
      <>
          <MyDiv text={{color: 'blue', content: 'This is the content of Index/Home'}}/>
          <MyText />
          <MyText />
      </>
    );
};

export default App;
