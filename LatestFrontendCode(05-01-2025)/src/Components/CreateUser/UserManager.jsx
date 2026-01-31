import React, { useState, useEffect, useContext } from 'react';
import UserForm from "./UserForm";
import './UserForm.css';
import UserListView from './UserListView';
import UserCardView from './UserCardView';
import { IdCard, List } from 'lucide-react';
import config from '../../config';
import { ToastContainer, toast, Bounce } from 'react-toastify';
import { useToast } from '../../ToastProvider';
import CryptoJS from "crypto-js";
import useSaveLogs from '../../Hooks/useSaveLogs';
import { Backupindex } from '../../Context/Backupindex';
import axios from 'axios';
import axiosInstance from '../../axiosinstance';
import { sendNotification } from '../../Hooks/useNotification';
import { NotificationContext } from "../../Context/NotificationContext";
function decryptData(encryptedData) {
  if (!encryptedData) return "";
  try {
    const bytes = CryptoJS.AES.decrypt(encryptedData, "1234567890");
    const decrypted = bytes.toString(CryptoJS.enc.Utf8);
    return decrypted || "";
  } catch (error) {
    console.error("Decryption error:", error);
    return "";
  }
}

export default function UserManagementContainer() {
  // const [users, setUsers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [viewType, setViewType] = useState('list');
  const [editingUser, setEditingUser] = useState(null);
  const accessToken = localStorage.getItem("AccessToken");
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();
  const { setNotificationData } = useContext(NotificationContext)
  const role = decryptData(localStorage.getItem("user_role"));
  const [privileges, setPrivileges] = useState({});
  const [showDeletePopup, setShowDeletePopup] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const handleAddUser = (newUser) => {
    // setUsers(prev => [...prev, newUser]);
    setShowForm(false);
    setEditingUser(null);
    setRefreshTrigger(prev => prev + 1);
  };

  const { showToast } = useToast();


  const handleEdit = (user) => {
    setEditingUser(user);
    setShowForm(true);
  };

  useEffect(() => {
    const stored = decryptData(localStorage.getItem("user_privileges"));
    if (stored) {
      try {
        setPrivileges(JSON.parse(stored));
      } catch (err) {
        console.error("Failed to parse user_privileges", err);
      }
    }
  }, []);

  const hasActionPermissions = () => {
    if (role !== "Employee") {
      return true;
    }
    return privileges.userUpdate || privileges.userDelete || privileges.userRead;
  };

  const canCreate = () => {
    if (role !== "Employee") return true;
    return privileges.userCreate;
  };

  const handleDelete = (user) => {
    setSelectedUser(user);
    setShowDeletePopup(true);
  };


  const confirmDelete = async () => {
    const user = selectedUser;
    setShowDeletePopup(false);

    try {
      const response = await axiosInstance.post(`${config.API.FLASK_URL}/deleteuser`, user, {
        headers: {
          "Content-Type": "application/json",
          token: accessToken,
        },
      });

      const event = `${user.name} ${user.lname} User Deleted`;
      handleLogsSubmit(event);

      const Notification_local_Data = {
        id: Date.now(),
        message: `🚫 ${user.name} ${user.lname} User Deleted`,
        timestamp: new Date(),
        isRead: false,
      };
      setNotificationData((prev) => [...prev, Notification_local_Data]);
      sendNotification(`🚫 ${user.name} ${user.lname} User Deleted`);

      showToast(`User ${user.name} ${user.lname} deleted successfully.`);
      setRefreshTrigger(prev => prev + 1);

    } catch (error) {
      console.error("Error deleting user:", error);
      showToast(`Failed to delete user ${user.name} ${user.lname}`, "error");
    }
  };

  const cancelDelete = () => {
    setShowDeletePopup(false);
    setSelectedUser(null);
  };

  const toggleViewType = () => {
    setViewType(prev => (prev === 'list' ? 'card' : 'list'));
  };

  const handleBackToList = () => {
    setShowForm(false);
    setEditingUser(null);
  };

  return (
    <div className="user-management-container">
      {/* <ToastContainer
        position="top-center"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick={false}
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
        transition={Bounce}
      /> */}
      <div className="top-bar">
        <h2>{showForm ? (editingUser ? 'Edit User' : 'Add New User') : (viewType === 'list' ? 'User List' : 'User Card')}</h2>
        <div className="top-bar-actions">
          {showForm ? (

            <button className="back-btn" onClick={handleBackToList}>
              Back to View
            </button>
          ) : (

            <>
              <button className="toggle-view-btn" onClick={toggleViewType}>
                {viewType === 'list' ? <IdCard /> : <List />}
              </button>
              {canCreate() &&
                <button className="new-user-btn" onClick={() => setShowForm(true)}>
                  + New User
                </button>
              }
            </>
          )}
        </div>
      </div>
      {showDeletePopup && selectedUser && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
          <div className="bg-white rounded-xl shadow-lg p-6 w-80 text-center">
            <h2 className="text-lg font-semibold text-gray-800 mb-2">Confirm Deletion</h2>
            <p className="text-gray-600 mb-5">
              Are you sure you want to delete <br />
              <span className="font-semibold text-gray-900">{selectedUser.name} {selectedUser.lname}</span>?
            </p>
            <div className="flex justify-center space-x-3">
              <button
                onClick={confirmDelete}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition duration-200"
              >
                Yes, Delete
              </button>
              <button
                onClick={cancelDelete}
                className="bg-gray-300 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-400 transition duration-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}


      {!showForm ? (
        viewType === 'list' ? (
          <UserListView onEdit={handleEdit} onDelete={handleDelete} refreshTrigger={refreshTrigger} />
        ) : (
          <UserCardView onEdit={handleEdit} onDelete={handleDelete} refreshTrigger={refreshTrigger} />
        )
      ) : (
        <UserForm onSave={handleAddUser} editingUser={editingUser} onCancel={handleBackToList} />
      )}
    </div>
  );
}
