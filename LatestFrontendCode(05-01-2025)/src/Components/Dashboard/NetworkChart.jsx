import React from 'react';
import GaugeComponent from 'react-gauge-component';

const NetworkChart = ({ networkData }) => {
  const mbitsToDisplayValue = (value) => {
    if (value >= 1000) {
      const gbValue = value / 1000;
      if (Number.isInteger(gbValue)) {
        return gbValue.toFixed(2) + ' GB';
      } else {  
        return gbValue.toFixed(2) + ' GB';
      }
    } else {
      return value.toFixed(2) + ' MB';
    }
  };

  return (
    <div className="bg-white p-6 mb-2 rounded-xl shadow-sm w-full" >
      {/* <h3 className="text-center text-lg font-semibold mb-4 text-gray-800">Network Usage Dashboard</h3> */}
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Network Received Gauge */}
        <div className="flex flex-col items-center">
          <h3 className="text-lg font-semibold text-blue-600">Data Received</h3>
          <div className="w-full max-w-xs">
            <GaugeComponent
              arc={{
                nbSubArcs: 150,
                colorArray: ['#5BE12C', '#F5CD19', '#EA4228'],
                width: 0.3,
                padding: 0.003
              }}
              labels={{
                valueLabel: {
                  style: { fontSize: 40 },
                  formatTextValue: mbitsToDisplayValue
                },
                tickLabels: {
                  type: "outer",
                  ticks: [
                    { value: 100 },
                    { value: 250 },
                    { value: 500 },
                    { value: 1000 },
                    { value: 2500 },
                    { value: 5000 },
                    { value: 7500 },
                    { value: 1000 },
                    { value: 1500 },
                    { value: 2000 }
                  ],
                  defaultTickValueConfig: {
                    formatTextValue: mbitsToDisplayValue
                  }
                }
              }}
              value={networkData.received}
              maxValue={2000}
            />
          </div>
        </div>

        {/* Network Sent Gauge */}
        <div className="flex flex-col items-center">
          <h3 className="text-lg font-semibold text-green-600">Data Sent</h3>
          <div className="w-full max-w-xs">
            <GaugeComponent
              arc={{
                nbSubArcs: 150,
                colorArray: ['#5BE12C', '#F5CD19', '#EA4228'],
                width: 0.3,
                padding: 0.003
              }}
              labels={{
                valueLabel: {
                  style: { fontSize: 40 },
                  formatTextValue: mbitsToDisplayValue
                },
                tickLabels: {
                  type: "outer",
                  ticks: [
                    { value: 100 },
                    { value: 250 },
                    { value: 500 },
                    { value: 1000 },
                    { value: 2500 },
                    { value: 5000 },
                    { value: 7500 },
                    { value: 1000 },
                    { value: 1500 },
                    { value: 2000 }
                  ],
                  defaultTickValueConfig: {
                    formatTextValue: mbitsToDisplayValue
                  }
                }
              }}
              value={networkData.sent}
              maxValue={2000}
            />
          </div>
        </div>
      </div>

      {/* Network Stats Summary */}
      {/* <div className="bg-gray-50 rounded-lg mt-6 p-4">
        <h4 className="text-center font-semibold text-gray-800 mb-2">Network Statistics</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-blue-100 p-3 rounded">
            <span className="font-medium text-blue-800">Data Received:</span>
            <br />
            <span className="text-blue-600">{networkData.received.toFixed(2)} MB</span>
          </div>
          <div className="bg-green-100 p-3 rounded">
            <span className="font-medium text-green-800">Data Sent:</span>
            <br />
            <span className="text-green-600">{networkData.sent.toFixed(2)} MB</span>
          </div>
          <div className="bg-purple-100 p-3 rounded">
            <span className="font-medium text-purple-800">Total Usage:</span>   
            <br />
            <span className="text-purple-600">{networkData.totalUsage.toFixed(2)} MB</span>
          </div>
        </div>
      </div> */}
    </div>
  );
};

export default NetworkChart;