import React, { useEffect, useState } from 'react';
import { Rnd } from 'react-rnd';
import { Doughnut, Bar } from 'react-chartjs-2';
import 'chart.js/auto';
import './ServerInfoPopup.css';
import { PieChart, Pie, Cell, Tooltip } from 'recharts';
import { RefreshCw, Monitor } from 'lucide-react';


const RADIAN = Math.PI / 180;

const needle = (value, total, cx, cy, iR, oR, color) => {
    const ang = 180.0 * (1 - value / total);
    const length = (iR + 2 * oR) / 3;
    const sin = Math.sin(-RADIAN * ang);
    const cos = Math.cos(-RADIAN * ang);
    const r = 5;
    const x0 = cx + 5;
    const y0 = cy + 5;
    const xba = x0 + r * sin;
    const yba = y0 - r * cos;
    const xbb = x0 - r * sin;
    const ybb = y0 + r * cos;
    const xp = x0 + length * cos;
    const yp = y0 + length * sin;

    return [
        <circle cx={x0} cy={y0} r={r} fill={color} stroke="none" />,
        <path d={`M${xba} ${yba}L${xbb} ${ybb} L${xp} ${yp} L${xba} ${yba}`} stroke="#none" fill={color} />,
    ];
};

const ServerInfoPopup = ({ loading, serverData, onClose }) => {
    if (loading) {
        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                <div className="bg-white rounded-lg max-w-md w-full mx-4">
                    <div className="p-6">
                        <div className="flex items-center justify-center py-8">
                            <RefreshCw className="w-6 h-6 text-blue-600 animate-spin" />
                            <span className="ml-2 text-gray-600">Loading server data...</span>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
    if (!serverData) return null;


    const { system, os, memory, disk, network, processor, ip_addresses, mac_addresses } = serverData;

    const processorChart = {
        labels: ['Usage', 'Idle'],
        datasets: [{
            data: [processor.usage, 100 - processor.usage],
            backgroundColor: ['#ff6b81', '#3498db'],
            borderWidth: 1,
        }]
    };

    const memoryChart = {
        labels: ['Used', 'Available'],
        datasets: [{
            data: [parseFloat(memory.used.replace(' GB', '')), parseFloat(memory.available.replace(' GB', ''))],
            backgroundColor: ['#ff6b81', '#3498db'],
            borderWidth: 1,
        }]
    };

    const diskBarChart = {
        labels: disk.map(d => d.mountpoint),
        datasets: [
            {
                label: 'Used Space',
                data: disk.map(d => parseFloat(d.used) || 0),
                backgroundColor: '#ff6b81',
            },
            {
                label: 'Free Space',
                data: disk.map(d => parseFloat(d.free) || 0),
                backgroundColor: '#3498db',
            },
            {
                label: 'Total Space',
                data: disk.map(d => parseFloat(d.total) || 0),
                backgroundColor: '#f1c40f',
            }
        ]
    };

    function formatDataSize(size) {
        const units = ['MB', 'GB', 'TB', 'PB'];
        let unitIndex = 0;

        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }

        return size.toFixed(2) + ' ' + units[unitIndex];
    }

    const networkTotal = parseFloat(network.received) + parseFloat(network.sent);
    const networkReceived = parseFloat(network.received);
    const networkSent = parseFloat(network.sent);

    const formattedTotal = formatDataSize(networkTotal);
    const formattedReceived = formatDataSize(networkReceived);
    const formattedSent = formatDataSize(networkSent);

    const networkData = [
        { name: `Received (${formattedReceived})`, value: networkReceived, color: '#36A2EB' },
        { name: `Sent (${formattedSent})`, value: networkSent, color: '#FF6384' },
    ];

    return (
        <div className="server-popup-overlay">
            <Rnd
                default={{
                    x: window.innerWidth / 2 - 300,
                    y: window.innerHeight / 2 - 250,
                    width: 400,
                    height: 500,
                }}
                minWidth={400}
                minHeight={300}
                bounds="window"
                dragHandleClassName="server-popup-drag-handle"
            >
                <div className="server-popup resizable-popup">
                    <div className="server-popup-drag-handle">
                        <button className="close-btnnn" onClick={onClose}>X</button>
                        <h2 className="Server-header">Server: {serverData?.system?.name}</h2>
                    </div>

                    <div className="ServerInfo-section">
                        <div className="Server-box device-info">
                            <h3><Monitor/> Device Specification</h3>
                            <p><strong>Device Name:</strong> {system?.name}</p>
                            <p><strong>Installed RAM:</strong> {memory.total} ({memory.available} usable)</p>
                            <p><strong>Server Version:</strong> {serverData?.server_version}</p>
                            <p><strong>IP:</strong> {ip_addresses}</p>
                            <p><strong>MAC:</strong> {mac_addresses}</p>
                            <p><strong>Activation Date:</strong> {serverData?.server_activation_date}</p>

                            <h3><i class='bx bxl-windows'></i> Windows Specification</h3>
                            <p><strong>Edition:</strong> {os.name}</p>
                            <p><strong>Architecture:</strong> {os.architecture}</p>
                            <p><strong>Version:</strong> {os.version}</p>
                            <p><strong>Type:</strong> {os.type}</p>
                            <p><strong>Manufacturer:</strong> {system?.manufacturer}</p>
                            <p><strong>Model:</strong> {system?.model}</p>
                        </div>

                        <div className="Server-box Server-chart-box Server-ntwk-bar">
                            <h3>Network Info</h3>
                            <PieChart width={300} height={300}>
                                <Pie
                                    dataKey="value"
                                    startAngle={180}
                                    endAngle={0}
                                    data={networkData}
                                    cx={95}
                                    cy={130}
                                    innerRadius={60}
                                    outerRadius={100}
                                    fill="#8884d8"
                                    stroke="none"
                                >
                                    {networkData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                {needle(networkReceived, networkTotal, 95, 130, 50, 100, '#d0d000')}
                            </PieChart>
                            <span className='Server-nterk-infocc'>
                                <label>Received</label>
                                <p>{formattedReceived}</p>
                            </span>
                            <span className='Server-nterk-infocc1'>
                                <label>Data Sent</label>
                                <p>{formattedSent}</p>
                            </span>
                        </div>

                        <div className="Server-box Server-chart-box Server-procs-bar">
                            <h3>Processor Usage</h3>
                            <Doughnut data={processorChart} />
                            <span className='Server-procs-infocc'>
                                <label>Usage</label>
                                <p>{processor.usage}%</p>
                            </span>
                            <span className='Server-procs-infocc11'>
                                <label>Count</label>
                                <p>{processor.count}</p>
                            </span>
                            <span className='Server-procs-infocc12'>
                                <label>Cores</label>
                                <p>{processor.physical}</p>
                            </span>
                        </div>

                        <div className="Server-box Server-chart-box Server-disk-bar">
                            <h3>Disk Storage</h3>
                            <Bar data={diskBarChart} />
                        </div>

                        <div className="Server-box Server-chart-box Server-mem-bar">
                            <h3>Memory Info</h3>
                            <Doughnut data={memoryChart} />
                            <span className='Server-memo-infocc'>
                                <label>Total</label>
                                <p>{memory.total}</p>
                            </span>
                            <span className='Server-memo-infocc11'>
                                <label>Available</label>
                                <p>{memory.available}</p>
                            </span>
                            <span className='Server-memo-infocc12'>
                                <label>Used</label>
                                <p>{memory.used}</p>
                            </span>
                        </div>
                    </div>
                </div>
            </Rnd>
        </div>
    );
};

export default ServerInfoPopup;
