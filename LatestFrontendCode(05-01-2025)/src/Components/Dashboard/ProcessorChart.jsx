// components/dashboard/ProcessorChart.jsx
import React from "react";
import { Doughnut } from "react-chartjs-2";
import "chart.js/auto";

const ProcessorChart = ({ data, processorData }) => {
    const centerTextPlugin = {
        id: "centerText",
        beforeDraw: function (chart) {
            const opts = chart.config.options.plugins.centerText;
            if (!opts?.display) return;

            const { ctx, width, height } = chart;
            const { usage } = opts.processorData || {};
            const centerX = width / 2;
            const centerY = height / 2;

            ctx.save();
            ctx.font = "16px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillStyle = "#1F2937";
            ctx.fillText("Usage", centerX, centerY - 30);

            ctx.font = "14px Arial";
            ctx.fillText(`${usage || 0}%`, centerX, centerY - 10);

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
                        return `${context.label}: ${context.parsed}`;
                    },
                },
            },
            centerText: {
                display: true,
                processorData, // 🔥 Pass latest processor values here
            },
        },
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-center text-lg font-semibold mb-4 text-gray-800">
                Server Processor Usage
            </h3>
            <div className="h-64 relative">
                <Doughnut data={data} options={options} plugins={[centerTextPlugin]} />
            </div>

            {/* Processor details below the chart */}
            <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div className="text-center">
                    <div className="text-base font-bold text-blue-500">
                        {processorData?.physical || "0.0"}
                    </div>
                    <div className="text-blue-600">Physical</div>
                </div>
                <div className="text-center">
                    <div className="text-base font-bold text-green-500">
                        {processorData?.count || "0.0"}
                    </div>
                    <div className="text-green-600">Core</div>
                </div>
            </div>
        </div>
    );
};

export default ProcessorChart;
