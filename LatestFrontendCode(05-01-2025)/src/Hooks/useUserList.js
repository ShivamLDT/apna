import { useState, useEffect } from "react";
import config from "../config";
import axios from "axios";
import axiosInstance from "../axiosinstance";

const useUserList = (refreshTrigger = 0) => {
  const [userData, setUserData] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const accessToken = localStorage.getItem("AccessToken");

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axiosInstance.post(
        `${config.API.FLASK_URL}/adduser`,
        {
          action: "fetchAll",
          role: "Employee",
        },
        {
          headers: {
            "Content-Type": "application/json",
            token: accessToken,
          },
        }
      );

      const data = response.data;
      setUserData(data);
      setFilteredUsers(data);
    } catch (err) {
      setError(err.response?.data?.message || err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };


  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  useEffect(() => {
    if (!searchTerm) {
      setFilteredUsers(userData);
    } else {
      const filtered = userData.filter((user) =>
        [user.name, user.lname, user.email, user.designation, user.mobileNumber]
          .filter(Boolean)
          .some((field) =>
            field.toLowerCase().includes(searchTerm.toLowerCase())
          )
      );
      setFilteredUsers(filtered);
    }
  }, [searchTerm, userData]);

  useEffect(() => {
    fetchUsers();
  }, [refreshTrigger]);

  return {
    userData,
    filteredUsers,
    loading,
    error,
    searchTerm,
    handleSearchChange,
    refetch: fetchUsers,
  };
};

export default useUserList;
