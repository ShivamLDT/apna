// components/dashboard/MemoryChart.jsx
import React from "react";
import { Doughnut } from "react-chartjs-2";
import "chart.js/auto";

const MemoryChart = ({ data, memoryData }) => {
    const centerTextPlugin = {
        id: "centerText",
        beforeDraw: function (chart) {
            const opts = chart.config.options.plugins.centerText;
            if (!opts?.display) return;

            const { ctx, width, height } = chart;
            const { percentage, total } = opts.memoryData || {};
            const centerX = width / 2;
            const centerY = height / 2;

            ctx.save();
            ctx.font = "16px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillStyle = "#1F2937";
            ctx.fillText("Total Memory", centerX, centerY - 30);

            ctx.font = "14px Arial";
            ctx.fillText(`${percentage || 0}% Used`, centerX, centerY - 10);

            ctx.restore();
        },
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "65%",
        plugins: {
            legend: {
                position: "bottom",
                labels: {
                    padding: 20,
                    usePointStyle: true,
                    font: { size: 14 },
                },
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        return `${context.label}: ${context.parsed.toFixed(2)} GB`;
                    },
                },
            },
            centerText: {
                display: true,
                memoryData, // 🔥 Pass latest memory values here
            },
        },
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-center text-lg font-semibold mb-4 text-gray-800">
                Server Memory Usage
            </h3>
            <div className="h-64 relative">
                <Doughnut data={data} options={options} plugins={[centerTextPlugin]} />
            </div>

            {/* Memory details below the chart */}
            <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
                <div className="text-center">
                    <div className="text-base font-bold text-blue-500">
                        {memoryData?.used || "0.0"}
                    </div>
                    <div className="text-blue-600">Used</div>
                </div>
                <div className="text-center">
                    <div className="text-base font-bold text-green-500">
                        {memoryData?.available || "0.0"}
                    </div>
                    <div className="text-green-600">Available</div>
                </div>
                <div className="text-center">
                    <div className="text-base font-bold text-gray-500">
                        {memoryData?.total || "0.0"}
                    </div>
                    <div className="text-gray-600">Total</div>
                </div>
            </div>
        </div>
    );
};

export default MemoryChart;
