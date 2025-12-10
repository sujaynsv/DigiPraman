import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Applications from './components/Applications';
import Organizations from './components/Organizations';
import Users from './components/Users';
import Schemes from './components/Schemes';
import ApplicationDetail from './components/ApplicationDetail';
import { Routes, Route, useLocation } from 'react-router-dom';

import './App.css';

import JitsiMeetComponent from "./components/JitsiMeetComponent";
function App() {
  const location = useLocation();

  // Map path prefix to a sidebar "current" view (for highlighting)
  const path = location.pathname;
  let currentView = 'dashboard';
  if (path.startsWith('/applications')) currentView = 'applications';
  else if (path.startsWith('/organizations')) currentView = 'organizations';
  else if (path.startsWith('/users')) currentView = 'users';
  else if (path.startsWith('/schemes')) currentView = 'schemes';

  return (
    <div className="app">
      <Sidebar currentView={currentView} />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/applications" element={<Applications />} />
          <Route path="/applications/:id" element={<ApplicationDetail />} />
          <Route path="/organizations" element={<Organizations />} />
          <Route path="/users" element={<Users />} />
          <Route path="/schemes" element={<Schemes />} />
          <Route path="/jitsi" element={<JitsiMeetComponent />} />
          <Route path="/jitsi/:id" element={<JitsiMeetComponent />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
