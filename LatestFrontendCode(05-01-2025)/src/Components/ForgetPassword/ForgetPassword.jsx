// Components/ForgotPassword/ForgotPassword.jsx
import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Mail, Shield, Lock, ArrowLeft, CheckCircle, X, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import config from '../../config';
import axiosInstance from '../../axiosinstance';
import AlertComponent from '../../AlertComponent';

const ForgotPassword = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [timer, setTimer] = useState(0);
    const [isOtpButtonEnabled, setIsOtpButtonEnabled] = useState(false);
    const [emailError, setEmailError] = useState('');
    const [otpError, setOtpError] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [alert, setAlert] = useState(null);

    // Get access token from localStorage
    const accessToken = localStorage.getItem('AccessToken');

    useEffect(() => {
        let interval;

        if (step === 2) {
            if (timer > 0) {
                interval = setInterval(() => {
                    setTimer(prevTimer => prevTimer - 1);
                }, 1000);
            } else if (timer === 0 && step === 2) {
                setStep(1);
                setOtpError('');
            }
        }

        return () => clearInterval(interval);
    }, [step, timer]);

    useEffect(() => {
        setIsOtpButtonEnabled(otp.trim() !== '');
    }, [otp]);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const passwordRequirements = [
        { id: 'length', text: 'At least 6 characters', test: (pwd) => pwd.length >= 6 && pwd.length <= 12 },
        { id: 'uppercase', text: 'One uppercase letter', test: (pwd) => /[A-Z]/.test(pwd) },
        { id: 'lowercase', text: 'One lowercase letter', test: (pwd) => /[a-z]/.test(pwd) },
        { id: 'number', text: 'One number', test: (pwd) => /\d/.test(pwd) },
        { id: 'special', text: 'One special character', test: (pwd) => /[!@#$%^&*(),.?":{}|<>]/.test(pwd) }
    ];

    const handleEmailSubmit = async () => {
        setIsLoading(true);
        setEmailError(''); // Clear previous errors

        try {
            const response = await axiosInstance.post(`${config.API.FLASK_URL}/requestotp`, { email }, {
                headers: {
                    'Content-Type': 'application/json',
                    token: accessToken,
                }
            });

            // Check if the response is successful
            if (response.status === 200 || response.status === 201) {
                setStep(2);
                setTimer(120);
                setEmailError('');
            } else {
                setEmailError('Invalid email address!');
            }
        } catch (error) {
            console.error('Error sending OTP:', error);

            // Handle different types of errors
            if (error.response) {
                // Server responded with error status
                const status = error.response.status;
                const errorMessage = error.response.data?.message || error.response.data?.error;

                if (status === 400) {
                    setEmailError(errorMessage || 'Invalid email address!');
                } else if (status === 404) {
                    setEmailError('Email not found!');
                } else if (status === 500) {
                    setEmailError('Server error. Please try again later.');
                } else {
                    setEmailError(errorMessage || 'Invalid email address!');
                }
            } else if (error.request) {
                // Network error
                setEmailError('Network error. Please check your connection.');
            } else {
                // Other error
                setEmailError('An unexpected error occurred.');
            }
        }
        setIsLoading(false);
    };

    const handleOtpSubmit = async () => {
        setIsLoading(true);
        setOtpError(''); // Clear previous errors

        try {
            const response = await axiosInstance.post(`${config.API.FLASK_URL}/otp-verify`, { email, otp }, {
                headers: {
                    'Content-Type': 'application/json',
                    token: accessToken
                }
            });

            if (response.status === 200 || response.status === 201) {
                setStep(3);
                setOtpError('');
            } else {
                setOtpError('Invalid OTP, please try again.');
            }
        } catch (error) {
            console.error('Error verifying OTP:', error);

            if (error.response) {
                const status = error.response.status;
                const errorMessage = error.response.data?.message || error.response.data?.error;

                if (status === 400) {
                    setOtpError(errorMessage || 'Invalid OTP, please try again.');
                } else if (status === 401) {
                    setOtpError('OTP expired or invalid.');
                } else {
                    setOtpError(errorMessage || 'Invalid OTP, please try again.');
                }
            } else if (error.request) {
                setOtpError('Network error. Please check your connection.');
            } else {
                setOtpError('An unexpected error occurred.');
            }
        }
        setIsLoading(false);
    };

    const handlePasswordSubmit = async () => {
        const passwordRegex = /(?=.*[A-Z])/.test(password) &&
            /(?=.{6,12}$)/.test(password) &&
            /[ -\/:-@\[-\`{-~]/.test(password) &&
            /(?=.*[0-9])/.test(password);

        if (!passwordRegex) {
            setPasswordError('Password must have combination of UpperCase, lowerCase, special characters and numbers and must have between [6-12] characters');
            return;
        }

        if (password !== confirmPassword) {
            setPasswordError('Passwords do not match!');
            return;
        }

        setIsLoading(true);
        setPasswordError(''); // Clear previous errors

        try {
            const response = await axiosInstance.post(`${config.API.FLASK_URL}/reset-password`, {
                email,
                password,
                confirmPassword
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    token: accessToken
                }
            });

            if (response.status === 200 || response.status === 201) {
                setAlert({
                    message: "Password reset successful!.",
                    type: 'success'
                });
                navigate('/login');
            } else {
                setPasswordError('Failed to reset password. Please try again.');
            }
        } catch (error) {
            console.error('Error resetting password:', error);

            if (error.response) {
                const status = error.response.status;
                const errorMessage = error.response.data?.message || error.response.data?.error;

                if (status === 400) {
                    setPasswordError(errorMessage || 'Password must have UpperCase, lowerCase, special characters and numbers');
                } else {
                    setPasswordError(errorMessage || 'Failed to reset password. Please try again.');
                }
            } else if (error.request) {
                setPasswordError('Network error. Please check your connection.');
            } else {
                setPasswordError('An unexpected error occurred.');
            }
        }
        setIsLoading(false);
    };

    const goBack = () => {
        if (step > 1) {
            setStep(step - 1);
            if (step === 2) {
                setTimer(0);
            }
        }
    };

    const resendOtp = async () => {
        setIsLoading(true);
        setOtpError(''); // Clear previous errors

        try {
            const response = await axiosInstance.post(`${config.API.FLASK_URL}/requestotp`, { email }, {
                headers: {
                    'Content-Type': 'application/json',
                    token: accessToken,
                }
            });

            if (response.status === 200 || response.status === 201) {
                setTimer(120);
                setOtpError('');
            } else {
                setOtpError('Failed to resend OTP. Please try again.');
            }
        } catch (error) {
            console.error('Error resending OTP:', error);
            setOtpError('Failed to resend OTP. Please try again.');
        }
        setIsLoading(false);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="bg-white rounded-2xl shadow-xl p-8">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4">
                            {step === 1 && <Mail className="w-8 h-8 text-indigo-600" />}
                            {step === 2 && <Shield className="w-8 h-8 text-indigo-600" />}
                            {step === 3 && <Lock className="w-8 h-8 text-indigo-600" />}
                        </div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">
                            {step === 1 && 'Forgot Password'}
                            {step === 2 && 'Verify OTP'}
                            {step === 3 && 'Set New Password'}
                        </h1>
                        <p className="text-gray-600 text-sm">
                            {step === 1 && 'Enter your email address to receive OTP'}
                            {step === 2 && 'Enter the 6-digit code sent to your email'}
                            {step === 3 && 'Create a new secure password'}
                        </p>
                    </div>

                    {/* Progress Indicator */}
                    <div className="flex items-center justify-center mb-8">
                        <div className="flex items-center space-x-4">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${step >= 1 ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
                                }`}>
                                {step > 1 ? <CheckCircle className="w-4 h-4" /> : '1'}
                            </div>
                            <div className={`w-8 h-1 ${step >= 2 ? 'bg-indigo-600' : 'bg-gray-200'}`}></div>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${step >= 2 ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
                                }`}>
                                {step > 2 ? <CheckCircle className="w-4 h-4" /> : '2'}
                            </div>
                            <div className={`w-8 h-1 ${step >= 3 ? 'bg-indigo-600' : 'bg-gray-200'}`}></div>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${step >= 3 ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
                                }`}>
                                3
                            </div>
                        </div>
                    </div>

                    {/* Step 1: Email */}
                    {step === 1 && (
                        <div className="space-y-6">
                            <span className='block text-xs text-red-500'>Note: Admin user password can only be changed through <a href="http://license.apnabackup.com" target='_blank' className='underline text-blue-500'>license.apnabackup.com</a></span>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Email Address
                                </label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                                    placeholder="Enter your email address"
                                />
                                {emailError && (
                                    <p className="text-red-500 text-sm mt-2">{emailError}</p>
                                )}
                            </div>
                            <button
                                onClick={handleEmailSubmit}
                                disabled={!email || isLoading}
                                className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                            >
                                {isLoading ? (
                                    <div className="flex items-center justify-center">
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                        Sending OTP...
                                    </div>
                                ) : (
                                    'Send OTP'
                                )}
                            </button>
                        </div>
                    )}

                    {/* Step 2: OTP */}
                    {step === 2 && (
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Enter OTP
                                </label>
                                <input
                                    type="text"
                                    value={otp}
                                    onChange={(e) => setOtp(e.target.value)}
                                    maxLength="6"
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors text-center text-lg tracking-widest"
                                    placeholder="000000"
                                />
                                {otpError && (
                                    <p className="text-red-500 text-sm mt-2">{otpError}</p>
                                )}
                            </div>

                            {/* Timer */}
                            <div className="text-center">
                                {timer > 0 ? (
                                    <p className="text-gray-600 text-sm">
                                        Code expires in <span className="font-medium text-indigo-600">{formatTime(timer)}</span>
                                    </p>
                                ) : (
                                    <button
                                        onClick={resendOtp}
                                        disabled={isLoading}
                                        className="text-indigo-600 text-sm font-medium hover:text-indigo-700 disabled:opacity-50"
                                    >
                                        {isLoading ? 'Resending...' : 'Resend OTP'}
                                    </button>
                                )}
                            </div>

                            <div className="flex space-x-4">
                                <button
                                    onClick={goBack}
                                    className="flex-1 flex items-center justify-center bg-gray-100 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                                >
                                    <ArrowLeft className="w-4 h-4 mr-2" />
                                    Back
                                </button>
                                <button
                                    onClick={handleOtpSubmit}
                                    disabled={!isOtpButtonEnabled || isLoading}
                                    className="flex-1 bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    {isLoading ? (
                                        <div className="flex items-center justify-center">
                                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                            Verifying...
                                        </div>
                                    ) : (
                                        'Verify OTP'
                                    )}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 3: New Password */}
                    {step === 3 && (
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    New Password
                                </label>
                                <div className="relative">
                                    <input
                                        type={showPassword ? 'text' : 'password'}
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                                        placeholder="Enter new password"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                    >
                                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                                {password && (
                                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                                        <p className="text-sm font-medium text-gray-700 mb-2">Password Requirements:</p>
                                        <div className="space-y-1">
                                            {passwordRequirements.map((req) => {
                                                const isValid = req.test(password);
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

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Confirm Password
                                </label>
                                <div className="relative">
                                    <input
                                        type={showConfirmPassword ? 'text' : 'password'}
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                                        placeholder="Confirm new password"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                    >
                                        {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                                {passwordError && (
                                    <p className="text-red-500 text-sm mt-2">{passwordError}</p>
                                )}
                            </div>

                            {/* Password Requirements */}


                            <div className="flex space-x-4">
                                <button
                                    onClick={goBack}
                                    className="flex-1 flex items-center justify-center bg-gray-100 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                                >
                                    <ArrowLeft className="w-4 h-4 mr-2" />
                                    Back
                                </button>
                                <button
                                    onClick={handlePasswordSubmit}
                                    disabled={!password || !confirmPassword || isLoading}
                                    className="flex-1 bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    {isLoading ? (
                                        <div className="flex items-center justify-center">
                                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                            Updating...
                                        </div>
                                    ) : (
                                        'Reset Password'
                                    )}
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="text-center mt-6">
                    <p className="text-sm text-gray-600">
                        Remember your password?{' '}
                        <button
                            onClick={() => navigate('/login')}
                            className="text-indigo-600 font-medium hover:text-indigo-700"
                        >
                            Sign In
                        </button>
                    </p>
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
    );
};

export default ForgotPassword;