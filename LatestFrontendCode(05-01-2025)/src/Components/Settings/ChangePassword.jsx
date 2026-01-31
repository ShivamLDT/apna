import React, { useState } from 'react';
import { Eye, EyeOff, Check, X } from 'lucide-react';
import config from '../../config';
import CryptoJS from "crypto-js";
import useSaveLogs from '../../Hooks/useSaveLogs';
import axios from 'axios';
import axiosInstance from '../../axiosinstance';
import { sendNotification } from '../../Hooks/useNotification';
import AlertComponent from '../../AlertComponent';

export default function ChangePassword() {
    const accessToken = localStorage.getItem("AccessToken");
    const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();
    const [alert, setAlert] = useState(null);

    const [passwords, setPasswords] = useState({
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
    });

    const [showPassword, setShowPassword] = useState({
        oldPassword: false,
        newPassword: false,
        confirmPassword: false
    });

    const [errors, setErrors] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    const passwordRequirements = [
        { id: 'length', text: 'At least 6 and max 12 characters', test: (pwd) => pwd.length >= 6 && pwd.length <= 12 },
        { id: 'uppercase', text: 'One uppercase letter', test: (pwd) => /[A-Z]/.test(pwd) },
        { id: 'lowercase', text: 'One lowercase letter', test: (pwd) => /[a-z]/.test(pwd) },
        { id: 'number', text: 'One number', test: (pwd) => /\d/.test(pwd) },
        { id: 'special', text: 'One special character', test: (pwd) => /[!@#$%^&*(),.?":{}|<>]/.test(pwd) }
    ];

    const togglePasswordVisibility = (field) => {
        setShowPassword(prev => ({
            ...prev,
            [field]: !prev[field]
        }));
    };

    const handleInputChange = (field, value) => {
        setPasswords(prev => ({
            ...prev,
            [field]: value
        }));

        // Clear errors when user starts typing
        if (errors[field]) {
            setErrors(prev => ({
                ...prev,
                [field]: ''
            }));
        }
    };

    const validateForm = () => {
        const newErrors = {};

        if (!passwords.oldPassword) {
            newErrors.oldPassword = 'Current password is required';
        }

        if (!passwords.newPassword) {
            newErrors.newPassword = 'New password is required';
        } else if (passwords.newPassword.length < 6 || passwords.newPassword.length > 12) {
            newErrors.newPassword = 'Password must be between 6 and 12 characters';
        }
        if (!passwords.confirmPassword) {
            newErrors.confirmPassword = 'Please confirm your password';
        } else if (passwords.newPassword !== passwords.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) return;

        setIsSubmitting(true);

        try {
            const response = await axiosInstance.post(`${config.API.FLASK_URL}/change-password`, {
                oldPassword: passwords.oldPassword,
                password: passwords.newPassword,
                confirmPassword: passwords.confirmPassword
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    token: accessToken,
                },
            });

            const data = response.data;

            // Success - axios only reaches here for 2xx status codes
            setPasswords({
                oldPassword: '',
                newPassword: '',
                confirmPassword: ''
            });

            const downloadEvent = "✅ Password changed successfully";
            handleLogsSubmit(downloadEvent);
            sendNotification(downloadEvent);
            setAlert({
                message: data.message || 'Password changed successfully!',
                type: 'success'
            });

        } catch (error) {
            console.error('Change password error:', error);

            // Handle specific HTTP error responses
            if (error.response) {
                const data = error.response.data;

                if (error.response.status === 400) {
                    setErrors(prev => ({
                        ...prev,
                        newPassword: data.message || 'Password does not meet requirements (e.g. upper, lower, number, special char).'
                    }));
                    handleLogsSubmit(`Change Password: ${data.message}` || 'Password does not meet requirements (e.g. upper, lower, number, special char).');
                    sendNotification(`❌ Change Password: ${data.message}` || '❌ Password does not meet requirements (e.g. upper, lower, number, special char).');
                    return;
                }

                if (error.response.status === 401) {
                    setErrors(prev => ({
                        ...prev,
                        oldPassword: data.message || 'Current password is incorrect.'
                    }));
                    handleLogsSubmit(`Change Password: ${data.message}` || 'Current password is incorrect.')
                    sendNotification(`❌ Change Password: ${data.message}` || '❌ Current password is incorrect.')
                    return;
                }

                // Other HTTP errors
                handleLogsSubmit(`Change Password: ${data.message}` || 'Something went wrong.')
                sendNotification(`❌ Change Password: ${data.message}` || '❌ Something went wrong.')
                setAlert({
                    message: data.message || data?.error || 'Something went wrong.',
                    type: 'error'
                });
            } else {
                // Network or other errors
                handleLogsSubmit(`Change Password: ${error.message}` || 'An unexpected error occurred.')
                sendNotification(`❌ Change Password: ${error.message}` || '❌ An unexpected error occurred.')
                setAlert({
                    message: error.message || 'An unexpected error occurred.',
                    type: 'error'
                });
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
            <div className="w-full max-w-md">
                {/* Header */}
                <div className="text-center">
                    <h1 className="text-xl font-bold text-gray-900">Change Password</h1>
                </div>

                {/* Form Container */}
                <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                    <div className="p-4">
                        <div className="space-y-4">
                            {/* Old Password */}
                            <div className="space-y-2">
                                <div className="relative">
                                    <input
                                        id="oldPassword"
                                        type={showPassword.oldPassword ? 'text' : 'password'}
                                        value={passwords.oldPassword}
                                        onChange={(e) => handleInputChange('oldPassword', e.target.value)}
                                        className={`w-full px-4 py-3 pr-12 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent peer ${errors.oldPassword ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
                                            }`}
                                        placeholder=" "
                                    />
                                    <label
                                        htmlFor="oldPassword"
                                        className={`absolute left-3 px-1 transition-all duration-200 pointer-events-none bg-white ${passwords.oldPassword || showPassword.oldPassword
                                            ? '-top-2 text-xs text-blue-600 font-medium'
                                            : 'top-1/2 transform -translate-y-1/2 text-gray-500'
                                            } peer-focus:-top-2 peer-focus:text-xs peer-focus:text-blue-600 peer-focus:font-medium`}
                                    >
                                        Current Password
                                    </label>
                                    <button
                                        type="button"
                                        onClick={() => togglePasswordVisibility('oldPassword')}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                                    >
                                        {showPassword.oldPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                                {errors.oldPassword && (
                                    <p className="text-red-500 text-sm flex items-center gap-1">
                                        <X className="w-4 h-4" />
                                        {errors.oldPassword}
                                    </p>
                                )}
                            </div>

                            {/* New Password */}
                            <div className="space-y-2">
                                <div className="relative">
                                    <input
                                        id="newPassword"
                                        type={showPassword.newPassword ? 'text' : 'password'}
                                        value={passwords.newPassword}
                                        onChange={(e) => handleInputChange('newPassword', e.target.value)}
                                        className={`w-full px-4 py-3 pr-12 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent peer ${errors.newPassword ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
                                            }`}
                                        placeholder=" "
                                    />
                                    <label
                                        htmlFor="newPassword"
                                        className={`absolute left-3 px-1 transition-all duration-200 pointer-events-none bg-white ${passwords.newPassword || showPassword.newPassword
                                            ? '-top-2 text-xs text-blue-600 font-medium'
                                            : 'top-1/2 transform -translate-y-1/2 text-gray-500'
                                            } peer-focus:-top-2 peer-focus:text-xs peer-focus:text-blue-600 peer-focus:font-medium`}
                                    >
                                        New Password
                                    </label>
                                    <button
                                        type="button"
                                        onClick={() => togglePasswordVisibility('newPassword')}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                                    >
                                        {showPassword.newPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                                {errors.newPassword && (
                                    <p className="text-red-500 text-sm flex items-center gap-1">
                                        <X className="w-4 h-4" />
                                        {errors.newPassword}
                                    </p>
                                )}

                                {/* Password Requirements */}
                                {passwords.newPassword && (
                                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                                        <p className="text-sm font-medium text-gray-700 mb-2">Password Requirements:</p>
                                        <div className="space-y-1">
                                            {passwordRequirements.map((req) => {
                                                const isValid = req.test(passwords.newPassword);
                                                return (
                                                    <div key={req.id} className="flex items-center gap-2 text-sm">
                                                        {isValid ? (
                                                            <Check className="w-4 h-4 text-green-500" />
                                                        ) : (
                                                            <X className="w-4 h-4 text-red-400" />
                                                        )}
                                                        <span className={isValid ? 'text-green-600' : 'text-gray-600'}>
                                                            {req.text}
                                                        </span>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Confirm Password */}
                            <div className="space-y-2">
                                <div className="relative">
                                    <input
                                        id="confirmPassword"
                                        type={showPassword.confirmPassword ? 'text' : 'password'}
                                        value={passwords.confirmPassword}
                                        onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                                        className={`w-full px-4 py-3 pr-12 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent peer ${errors.confirmPassword ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
                                            }`}
                                        placeholder=" "
                                    />
                                    <label
                                        htmlFor="confirmPassword"
                                        className={`absolute left-3 px-1 transition-all duration-200 pointer-events-none bg-white ${passwords.confirmPassword || showPassword.confirmPassword
                                            ? '-top-2 text-xs text-blue-600 font-medium'
                                            : 'top-1/2 transform -translate-y-1/2 text-gray-500'
                                            } peer-focus:-top-2 peer-focus:text-xs peer-focus:text-blue-600 peer-focus:font-medium`}
                                    >
                                        Confirm Password
                                    </label>
                                    <button
                                        type="button"
                                        onClick={() => togglePasswordVisibility('confirmPassword')}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                                    >
                                        {showPassword.confirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                                {errors.confirmPassword && (
                                    <p className="text-red-500 text-sm flex items-center gap-1">
                                        <X className="w-4 h-4" />
                                        {errors.confirmPassword}
                                    </p>
                                )}
                                {passwords.confirmPassword && passwords.newPassword === passwords.confirmPassword && (
                                    <p className="text-green-500 text-sm flex items-center gap-1">
                                        <Check className="w-4 h-4" />
                                        Passwords match
                                    </p>
                                )}
                            </div>

                            {/* Submit Button */}
                            <button
                                onClick={handleSubmit}
                                disabled={isSubmitting}
                                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold text-lg shadow-lg hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                            >
                                {isSubmitting ? (
                                    <div className="flex items-center justify-center gap-2">
                                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                        Updating Password...
                                    </div>
                                ) : (
                                    'Save Changes'
                                )}
                            </button>
                        </div>
                    </div>
                </div>
                <span className='block text-xs text-red-500 mt-2'>Note: Admin user password can only be changed through <a href="http://license.apnabackup.com" target='_blank' className='underline text-blue-500'>license.apnabackup.com</a></span>
            </div>
            {alert && (
                <AlertComponent
                    message={alert.message}
                    type={alert.type}
                    onClose={() => setAlert(null)}
                />
            )}
        </div>
    );
}