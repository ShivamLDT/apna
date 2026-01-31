// AuthContext.jsx
import React, { createContext, useContext, useState } from 'react';
import CryptoJS from "crypto-js";
import axios from "axios";
import config from "./config";
import { useToast } from "./ToastProvider";
import axiosInstance from './axiosinstance';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const { showToast } = useToast();

  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    const encryptedValue = localStorage.getItem('isLoggedIn');
    return encryptedValue && decryptData(encryptedValue) === 'true';
  });

  function encryptData(data) {
    return CryptoJS.AES.encrypt(data, "1234567890").toString();
  }
  function decryptData(encryptedData) {
    return CryptoJS.AES.decrypt(encryptedData, "1234567890").toString(CryptoJS.enc.Utf8);
  }

  const login = (token) => {
    localStorage.setItem("isLoggedIn", encryptData('true'));
    localStorage.setItem("Authorization", encryptData(token));
    setIsLoggedIn(true);
  };

  const showSessionExpiredAndLogout = () => {
    showToast("Session Expired", "error");
    logout();
  };

  const logout = async () => {
    const accessToken = localStorage.getItem('AccessToken');

    try {
      if (accessToken) {
        const response = await axiosInstance.post(
          `${config.API.FLASK_URL}/logout`,
          null,
          {
            headers: {
              'Content-Type': 'application/json',
              'Token': `${accessToken}`,
            },
            validateStatus: () => true,
          }
        );

        if (response.status >= 400) {
          throw new Error('Logout request failed');
        }

        // Show success toast
        showToast("Logged out successfully!", "success");
      }

      // Clear local storage, set isLoggedIn to false, and reload the page
      localStorage.clear();
      setIsLoggedIn(false);
      // window.location.reload();
    } catch (error) {
      console.error('Error during logout:', error);
      // Show error toast
      showToast("Error during logout. Please try again.", "error");

      // Ensure logout even if the API call fails
      localStorage.clear();
      // window.location.reload();
    }
  };

  const checkTokenValidity = async () => {
    const accessToken = localStorage.getItem('AccessToken');

    if (!accessToken) {
      showSessionExpiredAndLogout();
      return;
    }

    try {
      const response = await axiosInstance.post(
        `${config.API.FLASK_URL}/tokencheck`,
        {},
        { headers: { 'Content-Type': 'application/json', 'token': accessToken } }
      );

      // If response status is not OK or session has expired
      if (response.status !== 200 || response.data?.message === 'YOUR SESSION HAS EXPIRED , PLEASE LOGIN AGAIN!!') {
        showSessionExpiredAndLogout();
      }
    } catch (error) {
      console.error("Token check failed", error);
      showSessionExpiredAndLogout();
    }
  };



  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout, checkTokenValidity, encryptData, decryptData }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
