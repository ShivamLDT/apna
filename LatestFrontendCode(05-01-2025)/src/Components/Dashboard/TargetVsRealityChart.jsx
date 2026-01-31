// components/dashboard/TargetVsRealityChart.jsx
import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const targetData = [
  { month: "Jan", reality: 18, target: 20 },
  { month: "Feb", reality: 19, target: 22 },
  { month: "Mar", reality: 25, target: 24 },
  { month: "Apr", reality: 22, target: 26 },
  { month: "May", reality: 24, target: 28 },
  { month: "Jun", reality: 20, target: 25 },
  { month: "Jul", reality: 28, target: 30 },
];

const TargetVsRealityChart = () => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm">
      <h3 className="text-center text-lg font-semibold mb-4">Target vs Reality</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={targetData}>
            {/* <CartesianGrid strokeDasharray="3 3" /> */}
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="reality" fill="#10b981" name="Reality Sales" />
            <Bar dataKey="target" fill="#fbbf24" name="Target Sales" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex justify-between mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-sm">Reality Sales - 8,823</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <span className="text-sm">Target Sales - 12,122</span>
        </div>
      </div>
    </div>
  );
};

export default TargetVsRealityChart;