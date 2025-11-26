import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Applications from './components/Applications';
import Organizations from './components/Organizations';
import Users from './components/Users';
import Schemes from './components/Schemes';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'applications':
        return <Applications />;
      case 'organizations':
        return <Organizations />;
      case 'users':
        return <Users />;
      case 'schemes':
        return <Schemes />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Sidebar currentView={currentView} setCurrentView={setCurrentView} />
      <main className="main-content">{renderView()}</main>
    </div>
  );
}

export default App;
