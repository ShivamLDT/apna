// components/dashboard/SuccessFailedChart.jsx
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const SuccessFailedChart = ({ data, jobCounts }) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm">
      <h3 className="text-center text-lg font-semibold mb-4">Success Failed Jobs</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="node" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="success"
              stroke="#10b981"
              strokeWidth={2}
              name="success"
            />
            <Line
              type="monotone"
              dataKey="failed"
              stroke="#cf0000ff"
              strokeWidth={2}
              name="failed"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="flex justify-between mt-4 text-sm">
        <div className="text-center">
          <p className="font-semibold text-blue-600">{jobCounts.success}</p>
          <p className="text-gray-500">Success Jobs</p>
        </div>
        <div className="text-center">
          <p className="font-semibold text-green-600">{jobCounts.failed}</p>
          <p className="text-gray-500">Failed Jobs</p>
        </div>
      </div>
    </div>
  );
};

export default SuccessFailedChart;