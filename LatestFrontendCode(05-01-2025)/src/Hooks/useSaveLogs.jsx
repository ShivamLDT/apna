// useSaveLogs.js
import { useState, useEffect, useCallback } from "react";
import CryptoJS from "crypto-js";
import config from "../config";
import axios from "axios";
import axiosInstance from "../axiosinstance";

export default function useSaveLogs() {
  const [userName, setUserName] = useState("");
  const [userRole, setUserRole] = useState("");
  const [profilePic, setProfilePic] = useState(null);
  const [firstNameP, setFirstNameP] = useState(null);
  const [lastNameP, setLastNameP] = useState(null);
  const [emailP, setEmailP] = useState(null);
  const accessToken = localStorage.getItem("AccessToken");

  // Utility function
  const decryptData = useCallback((encryptedData) => {
    if (!encryptedData) return "";
    try {
      const bytes = CryptoJS.AES.decrypt(encryptedData, "1234567890");
      const decrypted = bytes.toString(CryptoJS.enc.Utf8);
      return decrypted || "";
    } catch (error) {
      console.error("Decryption error:", error);
      return "";
    }
  }, []);

  // Effect to fetch user profile info
  useEffect(() => {
    const profileUrl = localStorage.getItem("Admin Profile");
    const user_profile = localStorage.getItem("user_profile");

    const firstName = decryptData(localStorage.getItem("first_name")) || "";
    const lastName = decryptData(localStorage.getItem("last_name")) || "";
    const email = decryptData(localStorage.getItem("email")) || "";
    const usermail = decryptData(localStorage.getItem("user_email"));
    const finalEmail = email || usermail || "";

    setFirstNameP(firstName);
    setLastNameP(lastName);
    setEmailP(finalEmail);

    const adminRole = decryptData(localStorage.getItem("role"));
    const employeeRole = decryptData(localStorage.getItem("user_role"));
    const finalRole = adminRole || employeeRole || "";

    if (user_profile) {
      const expBase64 = /^data:image\/(png|jpg|jpeg|gif|bmp|webp|svg\+xml);base64,[A-Za-z0-9+/]+={0,2}$/;
      if (expBase64.test(user_profile)) {
        setProfilePic(user_profile);
      }
    }

    if (profileUrl) {
      const prefixBase64 = `data:image/png;base64,${profileUrl}`;
      const expBase64 = /^data:image\/(png|jpg|jpeg|gif|bmp|webp|svg\+xml);base64,[A-Za-z0-9+/]+={0,2}$/;
      if (expBase64.test(prefixBase64)) {
        setProfilePic(profileUrl);
      }
    }

    setUserName(`${firstName} ${lastName}`.trim());
    setUserRole(finalRole);
  }, [decryptData]);

  // Submit logs
  const handleLogsSubmit = useCallback(
    async (eventName) => {
      try {
        const response = await axiosInstance.post(
          `${config.API.FLASK_URL}/eventlogs`,
          {
            profile: profilePic,
            firstName: firstNameP,
            lastName: lastNameP,
            email: emailP,
            role: userRole,
            event: eventName,
            loginTime: new Date().toISOString(),
          },
          {
            headers: {
              "Content-Type": "application/json",
              token: accessToken,
            },
          }
        );

        // axios automatically throws if status >= 400, so no need for manual status check
        const data = response.data;
        // alert("Successfully Saved Logs"); // if you want to show success
      } catch (error) {
        console.error(
          "Log submission error:",
          error.response?.data?.message || error.message
        );
      }
    },
    [accessToken, profilePic, firstNameP, lastNameP, emailP, userRole]
  );


  return {
    userName,
    userRole,
    profilePic,
    firstNameP,
    lastNameP,
    emailP,
    handleLogsSubmit,
  };
}
