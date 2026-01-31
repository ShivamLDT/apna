import React from 'react';
import './Sidebar.css';

const Sidebar = () => {
  const items = ["Overview", "Executed Jobs", "Successfull Jobs", "Failed Jobs", "Backup Logs", "Portal User Logs", "License Information", "Paired Endpoints", "Endpoint Overview"];

  return (
    <div className="sidebar">
      <h2 className="logo">Report</h2>
      <ul className="menu">
        {items.map((item) => (
          <li key={item} className={item === "Overview" ? "active" : ""}>{item}</li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;
