import React, { useEffect, useState } from 'react';
import {
    LayoutDashboard,
    Database,
    CloudDownload,
    UsersRound,
    Laptop,
    Cable,
    BarChart3,
    ChartNoAxesCombined,
    Download,
    Settings,
    Crown,
    X, Upload
} from "lucide-react";

import axios from 'axios';
import config from '../../config';
import axiosInstance from '../../axiosinstance';
import { sendNotification } from '../../Hooks/useNotification';
import useSaveLogs from '../../Hooks/useSaveLogs';
import AlertComponent from '../../AlertComponent';

const SupportPage = () => {
    const [query, setQuery] = useState('');
    const [selectedTags, setSelectedTags] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [imagePreviewUrl, setImagePreviewUrl] = useState("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedCardTitle, setSelectedCardTitle] = useState("");
    const [messageError, setMessageError] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [confirmModal, setConfirmModal] = useState(false);
    const [tagInput, setTagInput] = useState('');
    const [matchedTags, setMatchedTags] = useState([]);
    const [selectedFileRaw, setSelectedFileRaw] = useState(null);
    const accessToken = localStorage.getItem("AccessToken");
    const { handleLogsSubmit } = useSaveLogs();
    const [alert, setAlert] = useState(null);

    const tagsData = {
        Home: ["Sidebar", "Menu", "Header", "Dashboard", "Card",],
        Backup: ["Storage Type", " file extension", "Scheduler"],
        Restore: ["Selected Endpoint", "DateTime issue", "Storage Type"],
        Users: ["Add user", "Profiles", "Actions"],
        Endpoints: ["Endpoint", "Connections", "Servers", "view job"],
        Progress: ["jobfailed", " Progress Report", "Completion"],
        Report: ["server dashboard", "License", "Excuted jobs"],
        Pairing: ["pairing issue", "Endpoint issue"],
        Settings: ["Destination", "Change password", "Personal information"],
        Licence: ["activationDate", "Agents", "License Expiry"],
        Installation: ["Setup Guide", "Requirements"],

    }

    const toggleTag = (tagId) => {
        setSelectedTags(prev =>
            prev.includes(tagId)
                ? prev.filter(id => id !== tagId)
                : [...prev, tagId]
        );
    };

    const handleTagInputChange = (e) => {
        setTagInput(e.target.value);
    };

    const handleTagInputKeyPress = (e) => {
        if (e.key === 'Enter' && tagInput.trim()) {
            if (!selectedTags.includes(tagInput.trim())) {
                setSelectedTags([...selectedTags, tagInput.trim()]);
            }
            setTagInput('');
            e.preventDefault();
        }
    };
    useEffect(() => {
        updateTagsFromMessage(query);
    }, [query]);

    const updateTagsFromMessage = (text) => {
        if (!text) return;

        const words = text.toLowerCase().split(/\s+/); // Text ke words split karo
        const availableTags = tagsData[selectedCardTitle] || []; // Available tags lo

        const newMatchedTags = availableTags.filter((tag) => {
            const tagWords = tag.toLowerCase().split(/\s+/); // Tag ke words split karo
            const firstWord = tagWords[0]; // Pehla word
            const lastWord = tagWords[tagWords.length - 1]; // Akhri word

            // Agar input ka koi word first ya last word se match kare toh tag select ho
            return words.some((word) => word === firstWord || word === lastWord);
        });

        setMatchedTags(newMatchedTags); // Matched tags update karna
        setSelectedTags((prevTags) => [...new Set([...prevTags, ...newMatchedTags])]); // Unique tags add karna
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedFileRaw(file);

            const fileType = file.type;

            if (fileType.startsWith('image/')) {
                const reader = new FileReader();
                reader.onloadend = () => {
                    setSelectedFile(reader.result);
                    setImagePreviewUrl(reader.result);
                };
                reader.readAsDataURL(file);

            } else if (fileType === 'application/pdf') {
                const reader = new FileReader();
                reader.onloadend = () => {
                    setSelectedFile(reader.result);
                    setImagePreviewUrl('');
                };
                reader.readAsDataURL(file);

            } else if (fileType === 'application/zip' ||
                fileType === 'application/x-zip-compressed' ||
                file.name.endsWith('.zip')) {
                const reader = new FileReader();
                reader.onloadend = () => {
                    setSelectedFile(reader.result);
                    setImagePreviewUrl('');
                }
            } else {
                console.warn('Unsupported file type:', fileType);
            }
        }
    };


    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!query.trim()) {
            setMessageError(true);
            return;
        }

        const formData = new FormData();
        formData.append("SubjectQuery", selectedCardTitle);
        formData.append("Message", query);
        formData.append("Station", 'Apna Backup');
        formData.append("Tags", selectedTags);

        if (selectedFile) {
            formData.append("Image", selectedFile);
        }

        const newFormData = {};
        formData.forEach((value, key) => {
            newFormData[key] = value;
        });

        if (!selectedFile) {
            delete newFormData.Image;
        }

        setIsSubmitting(true);

        try {
            const response = await axiosInstance.post(`${config.API.FLASK_URL}/support`, newFormData, {
                headers: {
                    'Content-Type': 'application/json',
                    'token': `${accessToken}`,
                },

            });

            if (response.status === 200) {
                const { message } = response.data;
                setIsModalOpen(false);
                setQuery('');
                setSelectedTags([]);
                setTagInput('');
                setMatchedTags([]);
                setImagePreviewUrl('');
                setSelectedFile(null);
                setSelectedFileRaw(null);
                setConfirmModal(true);
                sendNotification("✅ Support Query Submitted Successfully!.")
                handleLogsSubmit("Support Query Submitted Successfully!.")
            } else {
                throw new Error('Failed to submit support query');
            }
        } catch (error) {
            sendNotification("❌ Failed to submit support query");
            handleLogsSubmit("Failed to submit support query");
            setAlert({
                message: "Failed to submit support query. Please try again later.",
                type: 'error'
            });
            console.error('Error during form submission:', error.message);
        } finally {
            setIsSubmitting(false);
        }
    };

    const closeModal = () => {
        setIsModalOpen(false);
    }

    const openModal = (title) => {
        setSelectedCardTitle(title);
        setQuery('');
        setSelectedTags([]);
        setImagePreviewUrl('');
        setSelectedFile(null);
        setSelectedFileRaw(null);
        setMessageError(false);
        setTagInput('');
        setMatchedTags([]);
        setIsModalOpen(true);
    };


    const supportCategories = [
        { id: 'home', icon: LayoutDashboard, title: 'Home', color: 'bg-blue-500' },
        { id: 'backup', icon: Database, title: 'Backup', color: 'bg-green-500' },
        { id: 'restore', icon: CloudDownload, title: 'Restore', color: 'bg-purple-500' },
        { id: 'users', icon: UsersRound, title: 'Users', color: 'bg-yellow-500' },
        { id: 'endpoints', icon: Laptop, title: 'Endpoints', color: 'bg-gray-500' },
        { id: 'progress', icon: ChartNoAxesCombined, title: 'Progress', color: 'bg-indigo-500' },
        { id: 'report', icon: BarChart3, title: 'Report', color: 'bg-gray-700' },
        { id: 'pairing', icon: Cable, title: 'Pairing', color: 'bg-yellow-900' },
        { id: 'settings', icon: Settings, title: 'Settings', color: 'bg-red-500' },
        { id: 'licence', icon: Crown, title: 'Licence', color: 'bg-yellow-500' },
        { id: 'installation', icon: Download, title: 'Installation', color: 'bg-pink-500' },
    ];

    return (
        <div className="bg-gradient-to-br from-blue-50 via-white to-gray-100 px-4 sm:px-6 lg:px-8">
            <div className="max-w-5xl mx-auto text-center">
                <h2 className="text-xl sm:text-2xl font-extrabold text-gray-800">
                    Hi, how can we help?
                </h2>
                <p className="text-gray-600 mb-8">
                    We’re here for you every step of the way.
                </p>

                {/* Search Bar */}
                {/* <div className="relative max-w-3xl mx-auto mb-4">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Search className="w-5 h-5 text-gray-400" />
                    </div>
                    <input
                        type="text"
                        placeholder="Search for help articles, features, or topics..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent text-base"
                    />
                </div> */}
            </div>

            {/* Category Grid */}
            <div className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5 px-2">
                {supportCategories.map((category) => (
                    <div
                        key={category.id}
                        className="group bg-white border border-gray-100 p-4 rounded-2xl shadow hover:shadow-md hover:scale-105 transform transition duration-300 cursor-pointer relative overflow-hidden" // Added 'relative' and 'overflow-hidden'
                    >
                        <div className="flex items-center justify-center mb-4">
                            <div
                                className={`w-9 h-9 ${category.color} rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-200`}
                            >
                                <category.icon className="w-5 h-5 text-white" />
                            </div>
                        </div>
                        <h4 className="text-center text-gray-800 font-medium text-sm tracking-wide">
                            {category.title}
                        </h4>
                        <div className="supportform-content-subject-hover absolute inset-x-0 bottom-0 bg-blue-500 text-white py-2 transform translate-y-full opacity-0 transition-all duration-300 ease-in-out"> {/* Added absolute positioning, initial hidden state, and transition */}
                            <button onClick={() => openModal(category.title)} className="w-full h-full">Tell us</button>
                        </div>
                    </div>
                ))}
            </div>

            {isModalOpen && (
                <div className="modal-overlayPop">
                    <div className="w-full max-w-3xl max-h-full overflow-y-auto">
                        {/* Modal Container */}
                        <div className="bg-white shadow-2xl overflow-hidden relative animate-in fade-in-0 scale-in-95 duration-200">
                            {/* Close Button */}
                            <button
                                className="absolute top-0 right-0 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full p-2 transition-all duration-200 z-10"
                                onClick={closeModal}
                            >
                                <X size={18} />
                            </button>

                            {/* Header */}
                            <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 text-white">
                                <div className="flex items-center justify-center">
                                    <div>
                                        <h1 className="text-lg font-bold text-center">Your Query About {selectedCardTitle}</h1>
                                    </div>
                                </div>
                            </div>

                            {/* Form Content */}
                            <div className="p-2">
                                {/* Query Input */}
                                <div>
                                    <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700">
                                        <span>Describe your issue</span>
                                    </label>
                                    <textarea
                                        value={query}
                                        onChange={(e) => setQuery(e.target.value)}
                                        placeholder="Please describe your issue in detail. The more information you provide, the better we can help you..."
                                        className="w-full h-24 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-200 resize-none text-gray-700 placeholder-gray-400 text-sm leading-relaxed"
                                        rows="5"
                                    />
                                    {messageError && (
                                        <p className="text-red-500 text-sm flex items-center space-x-1">
                                            <span>⚠️</span>
                                            <span>Please describe your issue before submitting</span>
                                        </p>
                                    )}
                                </div>

                                {/* File Upload */}
                                <div className="space-y-3">
                                    <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700">
                                        <span>Attach screenshot or document (optional)</span>
                                    </label>
                                    <div className="relative">
                                        <input
                                            type="file"
                                            onChange={handleFileChange}
                                            className="hidden"
                                            id="file-upload"
                                            accept="image/*,application/pdf,zip,application/zip,application/x-zip,application/x-zip-compressed"
                                        />
                                        <label
                                            htmlFor="file-upload"
                                            className="flex items-center justify-between w-full px-2 py-2 border-2 border-dashed border-gray-300 rounded-xl hover:border-blue-400 hover:bg-blue-50 transition-all duration-200 cursor-pointer group"
                                        >
                                            <div className="flex items-center space-x-3">
                                                <div className="w-10 h-10 bg-gray-100 group-hover:bg-blue-100 rounded-lg flex items-center justify-center transition-colors duration-200">
                                                    <Upload size={20} className="text-gray-500 group-hover:text-blue-600" />
                                                </div>
                                                <div>
                                                    <p className="text-sm font-medium text-gray-700 group-hover:text-blue-700">
                                                        {selectedFileRaw ? selectedFileRaw.name : 'Click to upload file'}
                                                    </p>
                                                    <p className="text-xs text-gray-500">
                                                        Images ,PDF and ZIP files
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-blue-600 group-hover:text-blue-700 transition-colors duration-200">
                                                <span className="text-sm font-medium">Browse</span>
                                            </div>
                                        </label>
                                    </div>
                                    {selectedFileRaw && (
                                        <div className="mt-2 flex items-center justify-between bg-gray-50 border rounded-md p-2">
                                            <p className="text-sm text-gray-700 truncate max-w-xs">{selectedFileRaw.name}</p>
                                            <button
                                                onClick={() => {
                                                    setSelectedFile(null);
                                                    setSelectedFileRaw(null);
                                                    setImagePreviewUrl('');
                                                }}
                                                className="text-red-500 hover:text-red-700"
                                                title="Remove file"
                                            >
                                                <X size={18} />
                                            </button>
                                        </div>
                                    )}

                                    {/* Image Preview */}
                                    {imagePreviewUrl && (
                                        <div className="mt-3">
                                            <img
                                                src={imagePreviewUrl}
                                                alt="Preview"
                                                className="max-w-full h-24 rounded-lg border border-gray-200 shadow-sm object-cover"
                                            />
                                        </div>
                                    )}
                                </div>

                                {/* Tags */}
                                <div className="space-y-2">
                                    <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700">
                                        <span>Select or add relevant tags</span>
                                    </label>

                                    <input
                                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-200 text-gray-700 placeholder-gray-400 text-sm"
                                        type="text"
                                        placeholder="Type a custom tag and press Enter"
                                        value={tagInput}
                                        onChange={handleTagInputChange}
                                        onKeyPress={handleTagInputKeyPress}
                                    />

                                    <div className="flex flex-wrap gap-2">
                                        {[...new Set([
                                            ...(tagsData[selectedCardTitle] || []),
                                            ...selectedTags.filter(tag => !(tagsData[selectedCardTitle] || []).includes(tag))
                                        ])].map((tag) => {
                                            const isSelected = selectedTags.includes(tag);
                                            return (
                                                <button
                                                    key={tag}
                                                    type="button"
                                                    onClick={() => toggleTag(tag)}
                                                    className={`px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 transform hover:scale-105 border
                                            ${isSelected
                                                            ? 'bg-blue-500 text-white border-blue-500 shadow-lg shadow-blue-200'
                                                            : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 hover:border-gray-300'}
                                        `}
                                                >
                                                    {tag}
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>

                                {/* Submit Button */}
                                <div className="flex items-center justify-center pt-4 border-t border-gray-100">
                                    <button
                                        type="button"
                                        onClick={handleSubmit}
                                        disabled={isSubmitting}
                                        className="text-center bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-2 px-2 rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-200 flex items-center justify-center space-x-2"
                                    >
                                        {isSubmitting ? (
                                            <>
                                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                                <span>Submitting...</span>
                                            </>
                                        ) : (
                                            <>
                                                <span>Submit Support Query</span>
                                                <span>→</span>
                                            </>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Confirmation Modal (confirmModal) */}
            {confirmModal && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md animate-in fade-in-0 scale-in-95 duration-200">
                        {/* Success Icon */}
                        <div className="flex justify-center mb-6">
                            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                </div>
                            </div>
                        </div>

                        {/* Content */}
                        <div className="text-center space-y-4">
                            <h2 className="text-2xl font-bold text-gray-900">Query Submitted Successfully!</h2>
                            <p className="text-gray-600 leading-relaxed">
                                Thank you for reaching out to us. Our support team has received your query and will get back to you as soon as possible.
                            </p>

                            {/* Info Box */}
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left">
                                <div className="flex items-start space-x-3">
                                    <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center mt-0.5">
                                        <span className="text-white text-xs font-bold">i</span>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-blue-900">What happens next?</p>
                                        <p className="text-sm text-blue-700 mt-1">
                                            You'll receive an email confirmation shortly, and our team will respond within 24 hours.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Action Button */}
                        <div className="mt-8">
                            <button
                                onClick={() => {
                                    setConfirmModal(false);
                                    setSelectedTags([]);
                                    setTagInput('');
                                    setMatchedTags([]);
                                    setSelectedFileRaw(null);
                                    setMessageError(false);
                                }}
                                className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-green-600 hover:to-green-700 transition-all duration-200 shadow-lg hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-green-200"
                            >
                                Got it, thanks!
                            </button>
                        </div>
                    </div>
                </div>
            )}
            {alert && (
                <AlertComponent
                    message={alert.message}
                    type={alert.type}
                    onClose={() => setAlert(null)}
                />
            )}
        </div>
    );
};

export default SupportPage;