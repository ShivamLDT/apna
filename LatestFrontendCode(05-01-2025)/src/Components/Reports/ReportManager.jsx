import React from 'react';
import ReportSidebar from './ReportSidebar';
import Server from './Server';
import './ReportManager.css';

function ReportManager() {
  return (
    <div>
      <ReportSidebar />
      <Server />
    </div>
  );
}

export default ReportManager;