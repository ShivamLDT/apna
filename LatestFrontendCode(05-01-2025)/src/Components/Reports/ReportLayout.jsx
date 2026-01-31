import React from 'react';
import ReportSidebar from './ReportSidebar'; // Adjust the path as necessary
import './ReportManager.css'; // Assuming you have shared styles

function ReportLayout({ children }) {
  return (
    <div className="app">
      <ReportSidebar />
      <div className="report-content"> {/* Add a div for content */}
        {children}
      </div>
    </div>
  );
}

export default ReportLayout;