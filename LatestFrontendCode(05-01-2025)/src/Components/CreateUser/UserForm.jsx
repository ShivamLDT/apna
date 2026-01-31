import React, { useState, useEffect, useContext } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { Camera, Eye, EyeOff } from 'lucide-react';
import "./UserForm.css";
import config from '../../config';
import { useSyncData } from '../../Context/SyncDataContext';
import CryptoJS from "crypto-js";
import useSaveLogs from '../../Hooks/useSaveLogs';
import { Backupindex } from '../../Context/Backupindex';
import axios from "axios";
import axiosInstance from '../../axiosinstance';
import { sendNotification } from '../../Hooks/useNotification';
import { useToast } from '../../ToastProvider';
import { NotificationContext } from "../../Context/NotificationContext";
export default function UserProfile({ onSave, editingUser = null }) {

  const { syncData } = useSyncData();
  const orgName = syncData?.organization_details?.name;
  const [loading, setLoading] = useState(false);
  const { setNotificationData } = useContext(NotificationContext);
  const { showToast } = useToast();
  const { userName, userRole, profilePic, handleLogsSubmit } = useSaveLogs();

  const [formData, setFormData] = useState({
    name: '',
    lname: '',
    mobileNumber: '',
    email: '',
    designation: '',
    // oldPassword: '',
    // password: '',
    role: "Employee"
  });

  const [showPassword, setShowPassword] = useState(false);
  const [profileImage, setProfileImage] = useState(null);
  const [profileImageBase64, setProfileImageBase64] = useState('');
  const [submitToggle, setSubmitToggle] = useState(false);
  const [userData, setUserData] = useState('0')

  const [privileges, setPrivileges] = useState({
    userRead: false,
    userCreate: false,
    userDelete: false,
    restoreReadWrite: false,
    backupReadWrite: false,
    agentRead: false,
    agentPause: false,
    // agentCreate: false,
    agentUpdate: false,
    agentDelete: false,
    settingRead: false,
    settingDestination: false,
    settingChangePassword: false,
    settingNotification: false,
    destinationLanSetting: false,
    destinationGoogleDriveSetting: false,
    destinationDropboxSetting: false,
    progressPlay: false,
    progressPause: false,
    progressDelete: false,
    reportRead: false,
    reportDelete: false,
    userUpdate: false,
    settingVerification: false,
    destinationAWSSetting: false,
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    if (name === "mobileNumber") {
      const numericValue = value.replace(/\D/g, "");
      if (numericValue.length <= 10) {
        setFormData((prev) => ({
          ...prev,
          [name]: numericValue,
        }));
      }
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };


  const MAX_IMAGE_SIZE = 200 * 1024; // 200 KB

  // ✅ Helper to convert any image to WebP
  const convertToWebP = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement("canvas");
          canvas.width = img.width;
          canvas.height = img.height;
          const ctx = canvas.getContext("2d");
          ctx.drawImage(img, 0, 0);

          // Convert canvas to WebP blob
          canvas.toBlob(
            (blob) => {
              if (!blob) return reject(new Error("WebP conversion failed"));
              const webpReader = new FileReader();
              webpReader.onloadend = () => resolve(webpReader.result);
              webpReader.readAsDataURL(blob);
            },
            "image/webp",
            0.8 // quality (0–1)
          );
        };
        img.onerror = reject;
        img.src = event.target.result;
      };

      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };


  const handleImageChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // 1️⃣ Check file size
    if (file.size > MAX_IMAGE_SIZE) {
      showToast("Image size must be less than 200KB ❌", "error");
      e.target.value = ""; // Reset the file input
      return;
    }

    // 2️⃣ Allow .webp files directly
    if (file.type === "image/webp") {
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileImage(reader.result);
        setProfileImageBase64(reader.result);
      };
      reader.readAsDataURL(file);
      return;
    }

    // 3️⃣ Convert other formats to WebP
    try {
      const webpDataUrl = await convertToWebP(file);
      setProfileImage(webpDataUrl);
      setProfileImageBase64(webpDataUrl);
    } catch (err) {
      console.error("Image conversion error:", err);
      showToast("Failed to convert image to WebP ❌", "error");
    }
  };


  const handlePasswordChange = () => {
    // toast.success(`Password changed successfully ✅`);
    showToast(`Password changed successfully ✅`);
    setFormData(prev => ({ ...prev, newPassword: '' }));
  };

  const handleTogglePrivilege = (key) => {
    setPrivileges((prev) => {
      const updated = { ...prev };

      // Toggle the selected key
      updated[key] = !prev[key];

      // 1️⃣ If user toggles ON create/update/delete → force userRead = true
      if (
        (key === "userCreate" || key === "userUpdate" || key === "userDelete") &&
        updated[key] === true
      ) {
        updated.userRead = true;
      }

      // 2️⃣ If user toggles OFF create/update/delete → check if all are false, then disable userRead (only if userRead was auto-enabled)
      if (
        (key === "userCreate" || key === "userUpdate" || key === "userDelete") &&
        updated[key] === false
      ) {
        const allOff =
          !updated.userCreate && !updated.userUpdate && !updated.userDelete;

        if (allOff) {
          updated.userRead = false; // disable only if all are off
        }
      }

      // 3️⃣ Prevent turning off userRead while any create/update/delete is active
      if (
        key === "userRead" &&
        prev.userRead === true && // currently true
        updated.userRead === false && // trying to disable it
        (prev.userCreate || prev.userUpdate || prev.userDelete)
      ) {
        return prev; // block disabling userRead
      }

      return updated;
    });
  };



  const accessToken = localStorage.getItem("AccessToken");

  // const handleSubmit = async (e) => {
  //   e.preventDefault();
  //   setLoading(true);
  //   const url = submitToggle
  //     ? `${config.API.FLASK_URL}/updateuser`
  //     : `${config.API.FLASK_URL}/adduser`;

  //   const payload = {
  //     companyName: orgName,
  //     ...formData,
  //     profilePhoto: profileImageBase64,
  //     privileges,
  //     role: "Employee",
  //   };

  //   try {
  //     const response = await fetch(url, {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //         token: accessToken,
  //       },
  //       body: JSON.stringify(payload),
  //     });

  //     if (!response.ok) throw new Error();

  //     toast.success(submitToggle ? "User updated successfully ✅" : "User created successfully ✅");

  //     onSave?.();
  //     if (!submitToggle) resetForm();
  //   } catch (err) {
  // toast.error(submitToggle ? "Update failed ❌" : "Creation failed ❌");
  //   } finally {
  //     setLoading(false);
  //   }
  // };


  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const isUpdate = submitToggle;
    const url = isUpdate
      ? `${config.API.FLASK_URL}/updateuser`
      : `${config.API.FLASK_URL}/adduser`;

    const payload = {
      companyName: orgName,
      ...formData,
      profilePhoto: profileImageBase64,
      privileges,
      role: "Employee",
    };

    try {
      const response = await axiosInstance.post(url, payload, {
        headers: {
          'Content-Type': 'application/json',
          token: accessToken,
        },
      });

      // Check success properly
      if (response.status === 200 || response.status === 201) {
        showToast(`${formData?.name} ${formData?.lname} User ${isUpdate ? 'updated' : 'created'} successfully.`);

        const Notification_local_Data = {
          id: Date.now(),
          message: `✅ ${formData?.name} ${formData?.lname} User ${isUpdate ? 'updated' : 'created'} successfully`,
          timestamp: new Date(),
          isRead: false,
        };
        sendNotification(`✅ ${formData?.name} ${formData?.lname} User ${isUpdate ? 'updated' : 'created'} successfully`);
        setNotificationData((prev) => [Notification_local_Data, ...prev]);

        onSave?.();
        await handleLogsSubmit(`${formData?.name} ${formData?.lname} User ${isUpdate ? 'updated' : 'created'}`);
        // if (!isUpdate) resetForm();
      } else {
        throw new Error("Unexpected response status");
      }
    } catch (error) {
      console.error("Error submitting user:", error);

      let errorMessage = isUpdate ? "Update failed ❌" : "Creation failed ❌";
      if (error.response) {
        if (error.response.data?.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data?.message) {
          errorMessage = error.response.data.message;
        } else {
          errorMessage = error.response.statusText || errorMessage;
        }
      } else if (error.request) {
        errorMessage = "Network error - please check your connection";
      }

      showToast(errorMessage, "error");

      const Notification_local_Data = {
        id: Date.now(),
        message: `🚫 ${formData?.name} User ${isUpdate ? 'update' : 'creation'} failed`,
        timestamp: new Date(),
        isRead: false,
      };
      setNotificationData((prev) => [Notification_local_Data, ...prev]);
      sendNotification(`🚫 ${formData?.name} User ${isUpdate ? 'update' : 'creation'} failed`);
    }
    finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (editingUser) {
      setFormData({
        companyName: editingUser.companyName,
        name: editingUser.name,
        lname: editingUser.lname,
        mobileNumber: editingUser.mobileNumber,
        email: editingUser.email,
        designation: editingUser.designation,
        password: '',
        role: editingUser.role || 'Employee',
      });

      setPrivileges(editingUser.privileges || {});
      setProfileImage(editingUser.profilePhoto || null);
      setProfileImageBase64(editingUser.profilePhoto || '');
      setSubmitToggle(true);
    }
  }, [editingUser]);


  return (
    <div className="user-container">
      <form onSubmit={handleSubmit} className="form-content">
        <div className="sidebarr">
          <div className="profile-pic-container hover-gradient">
            <label htmlFor="imageUpload" className="image-upload-label">
              {profileImage ? (
                <img src={profileImage} alt="Profile" className="profile-pic" />
              ) : (
                <div className="placeholder-pic">No Photo</div>
              )}
              <div className="overlay">
                <Camera />
              </div>
            </label>
          </div>
          <input
            id="imageUpload"
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="hidden-file-input"
            style={{ cursor: "pointer", maxWidth: "100%", whiteSpace: "normal", wordBreak: "break-all" }}
          />

          {/* <input
            type="password"
            placeholder="Old Password"
            name="oldPassword"
            value={formData.oldPassword}
            onChange={handleInputChange}
            className="password-input"
          /> */}
          {submitToggle && (
            <div className="password-input-container">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="New Password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="password-input"
                pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{6,12}$"
                title="Password must be 6-12 characters long, include at least one uppercase letter, one lowercase letter, one number, and one special character."
              />
              <span className="password-toggle-icon" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </span>
            </div>
          )}


          {/* <button type="button" className="change-btn" onClick={handlePasswordChange}>
            Change Password
          </button> */}

        </div>

        <div className="main-form">
          <div className="two-col">
            <div className="floating-label-group">
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
              <label className={formData.name ? 'filled' : ''}>First Name</label>
            </div>
            <div className="floating-label-group">
              <input
                type="text"
                name="lname"
                value={formData.lname}
                onChange={handleInputChange}
                required
              />
              <label className={formData.lname ? 'filled' : ''}>Last Name</label>
            </div>
            <div className="floating-label-group">
              <input
                type="Number"
                name="mobileNumber"
                value={formData.mobileNumber}
                onChange={handleInputChange}
                maxLength={10}
                pattern="\d{10}"
                required
              />
              <label className={formData.mobileNumber ? 'filled' : ''}>Contact Number</label>
            </div>
          </div>

          <div className="two-col">
            <div className="floating-label-group">
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                disabled={submitToggle}
              />
              <label className={formData.email ? 'filled' : ''}>Email Address</label>
            </div>

            <div className="floating-label-group">
              <input
                type="text"
                name="designation"
                value={formData.designation}
                onChange={handleInputChange}
                required
              />
              <label className={formData.designation ? 'filled' : ''}>Designation</label>
            </div>
          </div>

          <div className='flex'>
            <div className="privilege-section">
              <h3 className="privilege-heading">User Privileges</h3>
              <hr style={{ marginBottom: "5px" }}></hr>

              <div className="privilege-row">
                <span>Create and schedule Backup</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.backupReadWrite ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('backupReadWrite')}
                >
                  {privileges.backupReadWrite ? 'On ✅' : 'Off ❌'}
                </button>
              </div>

              <div className="privilege-row">
                <span>Restore Executed Backup</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.restoreReadWrite ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('restoreReadWrite')}
                >
                  {privileges.restoreReadWrite ? 'On ✅' : 'Off ❌'}
                </button>
              </div>

              <div className="privilege-row">
                <span>User Profile view</span>
                <button
                  type="button"
                  disabled={privileges.userCreate || privileges.userUpdate || privileges.userDelete}
                  className={`toggle-btn ${privileges.userRead ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('userRead')}
                >
                  {privileges.userRead ? 'On ✅' : 'Off ❌'}
                </button>

              </div>

              <div className="privilege-row">
                <span>Create User Profile</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.userCreate ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('userCreate')}
                >
                  {privileges.userCreate ? 'On ✅' : 'Off ❌'}
                </button>
              </div>

              <div className="privilege-row">
                <span>Update User Profile</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.userUpdate ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('userUpdate')}
                >
                  {privileges.userUpdate ? 'On ✅' : 'Off ❌'}
                </button>
              </div>

              <div className="privilege-row">
                <span>Delete User Profile</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.userDelete ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('userDelete')}
                >
                  {privileges.userDelete ? 'On ✅' : 'Off ❌'}
                </button>
              </div>
            </div>

            <div className="privilege-section">
              <h3 className="privilege-heading">User Privileges</h3>
              <hr style={{ marginBottom: "5px" }}></hr>

              <div className="privilege-row">
                <span>View Scheduled Jobs</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.agentRead ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('agentRead')}
                >
                  {privileges.agentRead ? 'On ✅' : 'Off ❌'}
                </button>
              </div>

              <div className="privilege-row">
                <span>Pause Scheduled Jobs</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.agentPause ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('agentPause')}
                >
                  {privileges.agentPause ? 'On ✅' : 'Off ❌'}
                </button>
              </div>

              <div className="privilege-row">
                <span>Edit Scheduled Jobs</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.agentUpdate ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('agentUpdate')}
                >
                  {privileges.agentUpdate ? 'On ✅' : 'Off ❌'}
                </button>
              </div>

              <div className="privilege-row">
                <span>Delete Scheduled Jobs</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.agentDelete ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('agentDelete')}
                >
                  {privileges.agentDelete ? 'On ✅' : 'Off ❌'}
                </button>
              </div>

              <div className="privilege-row">
                <span>Jobs Progress Pause</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.progressPause ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('progressPause')}
                >
                  {privileges.progressPause ? 'On ✅' : 'Off ❌'}
                </button>
              </div>

              <div className="privilege-row">
                <span>Jobs Progress Play</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.progressPlay ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('progressPlay')}
                >
                  {privileges.progressPlay ? 'On ✅' : 'Off ❌'}
                </button>
              </div>

              <div className="privilege-row">
                <span>Jobs Progress Kill</span>
                <button
                  type="button"
                  className={`toggle-btn ${privileges.progressDelete ? 'on' : 'off'}`}
                  onClick={() => handleTogglePrivilege('progressDelete')}
                >
                  {privileges.progressDelete ? 'On ✅' : 'Off ❌'}
                </button>
              </div>
            </div>
          </div>


          <button type="submit" className="submit-btn" disabled={loading}>
            {loading
              ? (submitToggle ? 'Updating...' : 'Saving...')
              : (submitToggle ? 'Update Profile' : 'Save Profile')}
          </button>

        </div>
      </form>
      {/* <ToastContainer position="top-right" autoClose={3000} /> */}
    </div>
  );
}
