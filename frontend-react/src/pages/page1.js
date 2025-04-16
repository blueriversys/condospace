
import React from 'react';
import { createRoot } from 'react-dom/client';
import ComponentPage1 from '../components/ComponentPage1';

const domNode = document.getElementById('page1');
const root = createRoot(domNode);

root.render(<ComponentPage1 />);
