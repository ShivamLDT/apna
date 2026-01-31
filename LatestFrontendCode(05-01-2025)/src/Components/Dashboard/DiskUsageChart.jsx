// components/dashboard/DiskUsageChart.jsx
import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const DiskUsageChart = ({ data }) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm">
      <h3 className="text-center text-lg font-semibold mb-4">Server Disk Usage</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            {/* <CartesianGrid strokeDasharray="3 3" /> */}
            <XAxis dataKey="name" />
            <YAxis unit=" GB" />
            <Tooltip />
            <Legend />
            <Bar dataKey="total" fill="#0195fe" name="Total" />
            <Bar dataKey="used" fill="#ef4444" name="Used" />
            <Bar dataKey="free" fill="#01e196" name="Free" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default DiskUsageChart;