import React, { useState, useImperativeHandle, useEffect, forwardRef } from 'react';
import {
    Database,
    Cloud,
    HardDrive,
    Settings,
    Save,
    Check,
    AlertCircle,
    RefreshCcw
} from 'lucide-react';
import RepoIcon from '../Reports/Jobs/RepoIcon';
import axios from 'axios';
import config from '../../config';
import { ToastContainer, toast, Bounce } from 'react-toastify';
import { useToast } from '../../ToastProvider';
import CryptoJS from "crypto-js";
import axiosInstance from '../../axiosinstance';
import AlertComponent from '../../AlertComponent';

function decryptData(encryptedData) {
    const decryptedData = CryptoJS.AES.decrypt(
        encryptedData,
        "1234567890"
    ).toString(CryptoJS.enc.Utf8);
    return decryptedData;
}

function encryptData(data) {
    const encryptedData = CryptoJS.AES.encrypt(data, "1234567890").toString();
    return encryptedData;
}

const DestinationStorage = forwardRef((props, ref) => {
    const accessToken = localStorage.getItem("AccessToken");
    const [isSaving, setIsSaving] = useState(false);
    const [alert, setAlert] = useState(null);
    const { showToast } = useToast();
    const [toggleLoading, setToggleLoading] = useState({});
    const skipRepoCheck = ["LocalStorage", "UNC"];
    const repoMap = {
        AwsS3: "AWS",
        Azure: "AZURE",
        OneDrive: "ONEDRIVE",
        GoogleDrive: "GDRIVE",
        UNC: null,
        LocalStorage: null
    };

    const [storageSettings, setStorageSettings] = useState({
        s3bucket: true,
        azure: true,
        onedrive: true,
        localStorage: true,
        googleDrive: true,
        nasLan: true
    });

    const [storageStates, setStorageStates] = useState({
        LocalStorage: false,
        GoogleDrive: false,
        AwsS3: false,
        Azure: false,
        UNC: false,
        OneDrive: false
    });

    const storageStatesLabels = {
        LocalStorage: "On-Premise",
        GoogleDrive: "Google Drive",
        AwsS3: "S3 Bucket",
        Azure: "Azure",
        UNC: "NAS/UNC",
        OneDrive: "OneDrive"
    };

    // Load saved states from localStorage
    useEffect(() => {
        const savedStates = decryptData(localStorage.getItem("storageStates"));
        if (savedStates) {
            const excludedKeys = ["ApnaCloud", "Dropbox", "mock", "time"];
            const parsedStates = JSON.parse(savedStates);

            const filteredStates = Object.fromEntries(
                Object.entries(parsedStates).filter(
                    ([key]) => !excludedKeys.includes(key)
                )
            );

            setStorageStates({
                ...filteredStates,
                LocalStorage: filteredStates.LocalStorage !== undefined ? filteredStates.LocalStorage : true
            });
        }
    }, []);

    // Check repo configurations after storageStates are loaded
    useEffect(() => {
        // Only run if storageStates have been initialized
        const hasInitialized = Object.values(storageStates).some(val => val === true);
        if (!hasInitialized) return;

        const checkAllRepos = async () => {
            try {
                const reposToCheck = Object.keys(storageStates)
                    .filter(key => !skipRepoCheck.includes(key))
                    .map(key => repoMap[key]);

                const payload = {
                    action: "list_repo_check",
                    rep: reposToCheck
                };

                const response = await axiosInstance.post(
                    `${config.API.FLASK_URL}/dststorage`,
                    payload,
                    {
                        headers: {
                            "Content-Type": "application/json",
                            "token": accessToken,
                        }
                    }
                );

                const repoArray = response.data?.repo_list || [];

                const flatRepoResults = repoArray.reduce((acc, item) => {
                    const key = Object.keys(item)[0];
                    acc[key] = item[key];
                    return acc;
                }, {});

                const updatedStates = { ...storageStates };
                let invalidList = [];

                Object.keys(storageStates).forEach(type => {
                    if (!skipRepoCheck.includes(type)) {
                        const rep = repoMap[type];
                        const isValid = flatRepoResults[rep];

                        if (isValid === false && storageStates[type] === true) {
                            updatedStates[type] = false;
                            invalidList.push(storageStatesLabels[type]);
                        }
                    }
                });

                // Only update if there were changes
                const hasChanges = Object.keys(updatedStates).some(
                    key => updatedStates[key] !== storageStates[key]
                );

                if (hasChanges) {
                    setStorageStates(updatedStates);

                    // Save the updated states to localStorage
                    const excludedKeys = ["ApnaCloud", "Dropbox", "mock", "time"];
                    const filteredStates = Object.fromEntries(
                        Object.entries(updatedStates).filter(
                            ([key]) => !excludedKeys.includes(key)
                        )
                    );
                    localStorage.setItem("storageStates", encryptData(JSON.stringify(filteredStates)));
                }

                if (invalidList.length > 0) {
                    setAlert({
                        type: "error",
                        message: `${invalidList.join(", ")} not configured. Toggled off automatically.`
                    });
                }

            } catch (err) {
                console.error("Repo check on load failed:", err);
            }
        };

        checkAllRepos();
    }, [storageStates.LocalStorage]); // Only trigger when initial load is complete

    const [showSaveConfirm, setShowSaveConfirm] = useState(false);

    const handleToggle = async (type) => {
        const turningOn = !storageStates[type];
        setToggleLoading(prev => ({ ...prev, [type]: true }));

        if (turningOn && !skipRepoCheck.includes(type)) {
            try {
                const payload = {
                    action: "repo_check",
                    rep: repoMap[type]
                };

                const response = await axiosInstance.post(
                    `${config.API.FLASK_URL}/dststorage`,
                    payload,
                    {
                        headers: {
                            "Content-Type": "application/json",
                            "token": accessToken
                        }
                    }
                );

                if (response.data.valid === false) {
                    setToggleLoading(prev => ({ ...prev, [type]: false }));
                    setAlert({
                        message: `${storageStatesLabels[type]} is not configured`,
                        type: 'error'
                    });
                    return;
                }

            } catch (err) {
                setToggleLoading(prev => ({ ...prev, [type]: false }));
                setAlert({
                    message: "Unable to verify repository configuration",
                    type: 'error'
                });
                return;
            }
        }

        setStorageStates(prev => ({
            ...prev,
            [type]: !prev[type]
        }));

        setToggleLoading(prev => ({ ...prev, [type]: false }));
    };

    const saveChanges = async (e) => {
        e.preventDefault();

        if (isSaving) return;

        setIsSaving(true);

        const excludedKeys = ["ApnaCloud", "Dropbox", "mock", "time"];

        const filteredStates = Object.fromEntries(
            Object.entries(storageStates).filter(
                ([key]) => !excludedKeys.includes(key)
            )
        );

        localStorage.setItem("storageStates", encryptData(JSON.stringify(filteredStates)));

        const payload = {
            ...storageStates,
            'mock': true
        }

        try {
            const response = await axiosInstance.post(`${config.API.FLASK_URL}/dststorage`, payload, {
                headers: {
                    'Content-Type': 'application/json',
                    'token': `${accessToken}`,
                },
            });

            if (response.status === 200) {
                const { message } = response.data;
                showToast('Storage Set Successfully');
            }
            if (response.status === 400) {
                const errorData = await response.json();
                if (errorData.message === 'invalid token') {
                    localStorage.clear();
                    window.location.reload();
                }
            } else {
                console.error('Unexpected response status:', response.status);
            }
        } catch (error) {
            console.error('Error during form submission:', error.response ? error.response.data : error.message);
        }
        setIsSaving(false);
    };

    useImperativeHandle(ref, () => ({
        saveChanges
    }));

    const CustomToggle = ({ checked, onChange, disabled = false, loading }) => (
        <button
            onClick={onChange}
            disabled={disabled || loading}
            className={`
            relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ease-in-out
            ${checked ? 'bg-blue-500' : 'bg-gray-300'}
            ${loading ? ' cursor-wait' : 'cursor-pointer'}
        `}
        >
            {loading ? (
                <div className="flex justify-center items-center w-full">
                    <RefreshCcw size={20} color='#3b82f6' className='animate-spin' />
                </div>
            ) : (
                <span
                    className={`
                    inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200
                    ${checked ? 'translate-x-6' : 'translate-x-1'}
                `}
                />
            )}
        </button>
    );

    return (
        <div className="space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div>
                    <h2 className="text-lg font-bold text-gray-800">Destination Storage Type</h2>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-2">
                    <div className="space-y-2">
                        {Object.keys(storageStates).map((option, index) => (
                            <div
                                key={option}
                                className={`
                                    flex items-center justify-between p-2 rounded-lg border-2 transition-all duration-200
                                    ${storageStates[option]
                                        ? 'border-blue-200 bg-blue-50'
                                        : 'border-gray-200 bg-gray-50'
                                    }
                                    hover:border-blue-300 hover:shadow-sm
                                `}
                            >
                                <div className="flex items-center gap-2">
                                    <div className={`p-2 rounded-lg w-24`}>
                                        <RepoIcon repo={option.toUpperCase()} />
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-gray-800">{storageStatesLabels[option]}</h4>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    <CustomToggle
                                        checked={storageStates[option]}
                                        onChange={() => handleToggle(option)}
                                        loading={toggleLoading[option]}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-gray-50 px-2 py-2 border-t border-gray-200">
                    <div className="flex justify-center">
                        <button
                            onClick={saveChanges}
                            disabled={isSaving}
                            className={`
                                px-8 py-3 rounded-lg font-semibold transition-all duration-200 flex items-center gap-2
                                ${isSaving
                                    ? "bg-gray-400 cursor-not-allowed"
                                    : "bg-blue-500 hover:bg-blue-600 text-white hover:shadow-lg transform hover:scale-105"
                                }
                            `}
                        >
                            {isSaving ? (
                                <>
                                    <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                        <path className="opacity-75" fill="currentColor"
                                            d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 100 16v-4l-3 3 3 3v-4a8 8 0 01-8-8z" />
                                    </svg>
                                    Saving...
                                </>
                            ) : showSaveConfirm ? (
                                <>
                                    <Check className="w-5 h-5" />
                                    Changes Saved
                                </>
                            ) : (
                                <>
                                    <Save className="w-5 h-5" />
                                    Save Changes
                                </>
                            )}
                        </button>
                    </div>
                </div>
                {alert && (
                    <AlertComponent
                        message={alert.message}
                        type={alert.type}
                        onClose={() => setAlert(null)}
                    />
                )}
            </div>
        </div>
    );
});

export default DestinationStorage;