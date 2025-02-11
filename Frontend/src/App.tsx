import React from 'react';
import { Toaster } from 'react-hot-toast';
import RegisterForm from './components/RegisterForm';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <RegisterForm />
      <Toaster position="top-right" />
    </div>
  );
}

export default App;