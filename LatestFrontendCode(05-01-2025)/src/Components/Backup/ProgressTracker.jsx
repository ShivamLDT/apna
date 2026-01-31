import React from 'react';
import './Backup.css';

export default function ProgressTracker({ currentStep }) {
  const steps = ['Backup Info', 'File Extensions', 'Endpoint List', 'Schedule'];

  const getStatus = (index) => {
    if (index < currentStep) return 'done';
    if (index === currentStep) return 'wip';
    return 'ready';
  };

  return (
    <div className="stepper">
      {steps.map((step, index) => (
        <span key={index} className={getStatus(index)}>
          <div className="item">{step}</div>
        </span>
      ))}
    </div>
  );
}
