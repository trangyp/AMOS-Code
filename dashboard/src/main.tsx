/**
 * AMOS React Application Entry Point
 * 
 * Mounts the AMOS Dashboard React application to the DOM.
 * 
 * Architecture: AMOS Brain 14-Layer Cognitive System
 * Creator: Trang Phan
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Mount the application
const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found. Please ensure there is a div with id="root" in the HTML.');
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Log AMOS initialization
console.log('%c🧠 AMOS Brain Initialized', 'font-size: 24px; font-weight: bold; color: #6366f1;');
console.log('%cAbsolute Meta Operating System v3.0.0', 'font-size: 14px; color: #a855f7;');
console.log('%cCreator: Trang Phan', 'font-size: 12px; color: #818cf8;');
console.log('%cArchitecture: 14-Layer Cognitive System', 'font-size: 12px; color: #10b981;');
