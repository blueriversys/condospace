
import React from 'react';
import { createRoot } from 'react-dom/client';
import ComponentPage2 from '../components/ComponentPage2';

const domNode = document.getElementById('page2');
const root = createRoot(domNode);

root.render(<ComponentPage2 />);
