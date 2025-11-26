import { FaHome, FaBuilding, FaUsers, FaClipboardList, FaFileAlt } from 'react-icons/fa';
import './Sidebar.css';

function Sidebar({ currentView, setCurrentView }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <FaHome /> },
    { id: 'applications', label: 'Applications', icon: <FaFileAlt /> },
    { id: 'organizations', label: 'Organizations', icon: <FaBuilding /> },
    { id: 'users', label: 'Beneficiaries', icon: <FaUsers /> },
    { id: 'schemes', label: 'Schemes', icon: <FaClipboardList /> },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>📊 DigiPraman</h2>
      </div>
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${currentView === item.id ? 'active' : ''}`}
            onClick={() => setCurrentView(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
