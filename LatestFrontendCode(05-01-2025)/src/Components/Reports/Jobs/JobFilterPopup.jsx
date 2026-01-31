import React, { useState, useEffect } from 'react';

export default function JobFilterPopup({
    visible,
    filters,
    setFilters,
    onApply,
    onClose,
    nameOptions = [],
    showEndpoint = true,
    showDestination = true,
    showStatus = true,
    showEvent = false
}) {
    if (!visible) return null;

    const [localFilters, setLocalFilters] = useState(filters);

    useEffect(() => {
        setLocalFilters(filters);
    }, [filters, visible]);

    const maxDate = new Date().toISOString().split("T")[0];

    const handleClearAll = () => {
        setLocalFilters({ name: '', repo: '', fromDate: '', toDate: '', status: '', event: '' });
        setFilters("");
        onClose();
    };
    
    const handleFromDateChange = (e) => {
        const fromDate = e.target.value;
        setLocalFilters(prev => ({
            ...prev,
            fromDate,
            toDate: prev.toDate && prev.toDate < fromDate ? '' : prev.toDate
        }));
    };

    const handleToDateChange = (e) => {
        const toDate = e.target.value;
        setLocalFilters(prev => ({ ...prev, toDate }));
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
            <div className="bg-white rounded-lg shadow-lg p-6 w-96">
                <h2 className="text-lg font-bold mb-4">Filter Jobs</h2>

                {/* Endpoint Name */}
                {showEndpoint && (
                    <div className="mb-3">
                        <label className="block text-sm font-medium text-gray-700">Endpoint Name</label>
                        <select
                            value={localFilters.name}
                            onChange={e => setLocalFilters(prev => ({ ...prev, name: e.target.value }))}
                            className="mt-1 p-2 w-full border border-gray-300 rounded"
                        >
                            <option value="">All</option>
                            {nameOptions.map(name => (
                                <option key={name} value={name}>{name}</option>
                            ))}
                        </select>
                    </div>
                )}

                {/* Event Filter */}
                {showEvent && (
                    <div className="mb-3">
                        <label className="block text-sm font-medium text-gray-700">Event</label>
                        <input
                            type="text"
                            value={localFilters.event || ""}
                            onChange={e => setLocalFilters(prev => ({ ...prev, event: e.target.value }))}
                            className="mt-1 p-2 w-full border border-gray-300 rounded"
                            placeholder="Search event..."
                        />
                    </div>
                )}

                {/* Destination */}
                {showDestination && (
                    <div className="mb-3">
                        <label className="block text-sm font-medium text-gray-700">Destination</label>
                        <select
                            value={localFilters.repo}
                            onChange={e => setLocalFilters(prev => ({ ...prev, repo: e.target.value }))}
                            className="mt-1 p-2 w-full border border-gray-300 rounded"
                        >
                            <option value="">All</option>
                            <option value="LAN">On-Premise</option>
                            <option value="GDRIVE">Google Drive</option>
                            <option value="UNC">NAS</option>
                            <option value="AZURE">Azure</option>
                            <option value="AWSS3">AWS S3</option>
                            <option value="ONEDRIVE">OneDrive</option>
                        </select>
                    </div>
                )}

                {/* Status */}
                {showStatus && (
                    <div className="mb-3">
                        <label className="block text-sm font-medium text-gray-700">Status</label>
                        <select
                            value={localFilters.status}
                            onChange={e => setLocalFilters(prev => ({ ...prev, status: e.target.value }))}
                            className="mt-1 p-2 w-full border border-gray-300 rounded"
                        >
                            <option value="">All</option>
                            <option value="success">Executed</option>
                            <option value="failed">Not Executed</option>
                        </select>
                    </div>
                )}

                {/* From Date */}
                <div className="mb-3">
                    <label className="block text-sm font-medium text-gray-700">From Date</label>
                    <input
                        type="date"
                        value={localFilters.fromDate}
                        max={maxDate}
                        onChange={handleFromDateChange}
                        className="mt-1 p-2 w-full border border-gray-300 rounded"
                    />
                </div>

                {/* To Date */}
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700">To Date</label>
                    <input
                        type="date"
                        value={localFilters.toDate}
                        min={localFilters.fromDate || undefined}
                        max={maxDate}
                        onChange={handleToDateChange}
                        className="mt-1 p-2 w-full border border-gray-300 rounded"
                    />
                </div>

                {/* Buttons */}
                <div className="flex justify-between items-center">
                    <button
                        onClick={handleClearAll}
                        className="px-4 py-2 bg-yellow-400 text-gray-900 rounded hover:bg-yellow-500"
                    >
                        Clear All
                    </button>
                    <div className="flex gap-2">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={() => {
                                setFilters(localFilters);
                                onApply();
                            }}
                            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                            Apply
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
}
