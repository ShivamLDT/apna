import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import WA from '../../assets/Whatsappr.png'
import GM from '../../assets/gmail.png'
import ET from '../../assets/event.png'
import { useSyncData } from '../../Context/SyncDataContext';
import CryptoJS from "crypto-js";
import axiosInstance from '../../axiosinstance';
import AlertComponent from '../../AlertComponent';

const EVENTS = [
  { key: 'JobsSuccess', label: 'Jobs Successfully' },
  { key: 'restoresuccess', label: 'Job Restore' },
  { key: 'JobsFailed', label: 'Jobs Failed' },
  { key: 'LoginDone', label: 'Login Done' },
  { key: 'JobPlay', label: 'Job Resume/Started(Reschedule)' },
  { key: 'JobPause', label: 'Job Paused(Reschedule)' },
  { key: 'JobRename', label: 'Job Renamed(Reschedule)' },
  { key: 'JobReshedule', label: 'Job Reschedule' },
  { key: 'JobDelete', label: 'Job Deleted' },
  // { key: 'restorefailed', label: 'Restore Failed' }
];

const formatValue = (value) => (value?.trim() ? value : 'Default');

export default function NotificationSettings() {
  const { syncData } = useSyncData();
  const [permissions, setPermissions] = useState(() =>
    Object.fromEntries(EVENTS.map(e => [e.key, { email: 'default', whatsapp: 'default' }]))
  );
  const [emailInput, setEmailInput] = useState('');
  const [whatsappInput, setWhatsappInput] = useState('');
  const [emailPermissionForAll, setEmailPermissionForAll] = useState('default');
  const [whatsappPermissionForAll, setWhatsappPermissionForAll] = useState('default');
  const [emailOptions, setEmailOptions] = useState([]);
  const [whatsappOptions, setWhatsappOptions] = useState([]);
  const [showPopup, setShowPopup] = useState(false);
  const [userName, setUserName] = useState("");
  const [userRole, setUserRole] = useState("");
  const [profilePic, setProfilePic] = useState(null);
  const [firstNameP, setFirstNameP] = useState(null);
  const [lastNameP, setLastFNameP] = useState(null);
  const [emailP, setEmailP] = useState(null);
  const [alert, setAlert] = useState(null);

  const accessToken = localStorage.getItem('AccessToken');
  const adminEmail = syncData?.email;
  const adminMob = syncData?.mobile;

  const handleChange = (eventKey, channel) => (e) => {
    const value = e.target.value;
    if (eventKey === 'ForAll') {
      if (channel === 'email') {
        setEmailPermissionForAll(value);
        setPermissions(prev => {
          const updated = { ...prev };
          for (const key in updated) {
            updated[key].email = value;
          }
          return updated;
        });
      } else {
        setWhatsappPermissionForAll(value);
        setPermissions(prev => {
          const updated = { ...prev };
          for (const key in updated) {
            updated[key].whatsapp = value;
          }
          return updated;
        });
      }
    } else {
      setPermissions(prev => ({
        ...prev,
        [eventKey]: {
          ...prev[eventKey],
          [channel]: value
        }
      }));
    }
  };

  const handleInput = (type, value) => {
    if ((type === 'email' && value === adminEmail) || (type === 'whatsapp' && value === adminMob)) {
      setAlert({
        message: `Admin ${type === 'email' ? 'email' : 'WhatsApp'} cannot be added.`,
        type: 'warning'
      });
      type === 'email' ? setEmailInput('') : setWhatsappInput('');
    } else {
      type === 'email' ? setEmailInput(value) : setWhatsappInput(value);
    }
  };

  const handleSave = async () => {
    const formatted = {
      CC: {
        Email: emailInput.trim(),
        Whatsapp: formatValue(whatsappInput)
      },
      ForAll: {
        Email: formatValue(emailPermissionForAll),
        Whatsapp: formatValue(whatsappPermissionForAll)
      }
    };

    EVENTS.forEach(({ key }) => {
      formatted[key] = {
        Email: formatValue(permissions[key].email),
        Whatsapp: formatValue(permissions[key].whatsapp)
      };
    });

    try {
      const res = await axiosInstance.post(`${config.API.FLASK_URL}/notification`, {
        ...formatted,
        noughty: true
      }, {
        headers: {
          'Content-Type': 'application/json',
          token: accessToken
        }
      });

      if (res.data.allEmails) setEmailOptions(res.data.allEmails);
      if (res.data.detailslist) {
        setWhatsappOptions(res.data.detailslist.map(item => `${item.mobile} (${item.name})`));
      }

      setShowPopup(true);
      handleSaveLogs(formatted);
    } catch (err) {
      console.error('Save error:', err);
    }
  };

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

  useEffect(() => {
    const profileUrl = localStorage.getItem('Admin Profile');
    const user_profile = localStorage.getItem('user_profile');
    const firstName = decryptData(localStorage.getItem("first_name")) || "";
    const lastName = decryptData(localStorage.getItem("last_name")) || "";
    const email = decryptData(localStorage.getItem("email")) || "";
    setFirstNameP(firstName);
    setLastFNameP(lastName);
    setEmailP(email);

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
  }, []);

  const Role = decryptData(localStorage.getItem("role"));


  const handleSaveLogs = async (formattedPermissions) => {
    try {
      const logs = [];

      const logEvent = async (type, eventKey, value) => {
        if (!value || value === 'default' || value.trim() === '') return;

        const isForAll = eventKey === "ForAll";
        const isCC = eventKey === "CC";
        const eventLabel = isCC
          ? "CC event"
          : isForAll
            ? "ForAll"
            : EVENTS.find(e => e.key === eventKey)?.label || eventKey;

        const message = `${type === "email" ? "Email" : "WhatsApp"} permission for ${eventLabel}`;

        const payload = {
          profile: profilePic,
          firstName: firstNameP,
          lastName: lastNameP,
          email: emailP,
          role: Role,
          event: message,
          loginTime: new Date().toISOString(),
          receiver: value
        };

        logs.push(payload);
      };

      // ✅ CC inputs
      const ccEmail = formattedPermissions.CC?.Email?.trim();
      const ccWhatsapp = formattedPermissions.CC?.Whatsapp?.trim();
      if (ccEmail && ccEmail !== 'default') await logEvent("email", "CC", ccEmail);
      if (ccWhatsapp && ccWhatsapp !== 'default') await logEvent("whatsapp", "CC", ccWhatsapp);

      // ✅ ForAll inputs
      const forAllEmail = formattedPermissions.ForAll?.Email?.trim();
      const forAllWhatsapp = formattedPermissions.ForAll?.Whatsapp?.trim();
      if (forAllEmail && forAllEmail !== 'default') await logEvent("email", "ForAll", forAllEmail);
      if (forAllWhatsapp && forAllWhatsapp !== 'default') await logEvent("whatsapp", "ForAll", forAllWhatsapp);

      // ✅ Individual events
      for (const { key } of EVENTS) {
        const email = formattedPermissions[key]?.Email?.trim();
        const whatsapp = formattedPermissions[key]?.Whatsapp?.trim();
        if (email && email !== 'default') await logEvent("email", key, email);
        if (whatsapp && whatsapp !== 'default') await logEvent("whatsapp", key, whatsapp);
      }

      // 🔁 Submit all valid logs (parallel instead of one-by-one)
      await Promise.all(
        logs.map(log =>
          axiosInstance.post(`${config.API.FLASK_URL}/eventlogs`, log, {
            headers: { token: accessToken }
          })
        )
      );

    } catch (error) {
      console.error('Log submission error:', error.response?.data || error.message);
    }
  };


  useEffect(() => {
    fetchInitialPermissions();
  }, []);

  const fetchInitialPermissions = async () => {
    try {
      const res = await axiosInstance.post(`${config.API.FLASK_URL}/notification`, {}, {
        headers: {
          'Content-Type': 'application/json',
          token: accessToken
        }
      });

      const data = res.data;
      if (data.allEmails) setEmailOptions(data.allEmails);
      if (data.detailslist)
        setWhatsappOptions(data.detailslist.map(item => `${item.mobile} (${item.name})`));

      if (data.Notification) {
        const notif = data.Notification;
        if (notif.CC) {
          setEmailInput(notif.CC.Email);
          setWhatsappInput(notif.CC.Whatsapp);
        }
        if (notif.ForAll) {
          setEmailPermissionForAll(notif.ForAll.Email);
          setWhatsappPermissionForAll(notif.ForAll.Whatsapp);
        }
        const updatedPermissions = {};
        EVENTS.forEach(({ key }) => {
          if (notif[key]) {
            updatedPermissions[key] = {
              email: notif[key].Email,
              whatsapp: notif[key].Whatsapp
            };
          }
        });
        setPermissions(updatedPermissions);
      }
    } catch (error) {
      console.error('Initial load error:', error);
    }
  };

  return (
    <div className="h-screen flex flex-col">
      <div className="flex-1 flex flex-col bg-white overflow-hidden" style={{ boxShadow: "1px 1px 12px gray" }}>
        <div className="flex justify-between items-center p-2 border-b">
          <h2 className="text-xl font-semibold text-gray-700">Message & Email</h2>
        </div>

        <div className="grid grid-cols-3 text-center font-semibold text-gray-600 bg-gray-50 border-b">
          <div className="text-red-600 flex justify-center items-center gap-1"><img src={ET} height={25} width={25} className="flex justify-between items-center" /> Event</div>
          <div className="text-red-600 flex justify-center items-center gap-1"><img src={GM} height={25} width={25} className="flex justify-between items-center" /> Email</div>
          <div className="text-green-600 flex justify-center items-center gap-1"><img src={WA} height={25} width={25} className="flex justify-between items-center" /> WhatsApp</div>
        </div>

        <div className="flex-1 overflow-auto">
          <div className="px-2 py-2 space-y-2">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="font-medium">CC</div>
              <input
                type="email"
                placeholder="Add Email"
                className="border rounded px-2 py-2"
                value={emailInput}
                onChange={(e) => handleInput('email', e.target.value)}
              />
              <input
                type="number"
                placeholder="Add Number"
                className="border rounded px-2 py-2"
                value={whatsappInput}
                onChange={(e) => handleInput('whatsapp', e.target.value)}
                maxLength={10}
                pattern="\d{10}"
              />

            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="font-medium">For All</div>
              <select
                className="border rounded px-2 py-2"
                value={emailPermissionForAll}
                onChange={handleChange('ForAll', 'email')}
              >
                <option value="default">Default</option>
                {emailOptions.map((e, i) => <option key={i} value={e}>{e}</option>)}
              </select>
              <select
                className="border rounded px-2 py-2"
                value={whatsappPermissionForAll}
                onChange={handleChange('ForAll', 'whatsapp')}
              >
                <option value="default">Default</option>
                {whatsappOptions.map((e, i) => <option key={i} value={e}>{e}</option>)}
              </select>
            </div>

            {EVENTS.map(({ key, label }) => (
              <div key={key} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="font-medium">{label}</div>
                <select
                  className="border rounded px-2 py-2"
                  value={permissions[key]?.email || 'default'}
                  onChange={handleChange(key, 'email')}
                >
                  <option value="default">Default</option>
                  {emailOptions.map((e, i) => <option key={i} value={e}>{e}</option>)}
                </select>
                <select
                  className="border rounded px-2 py-2"
                  value={permissions[key]?.whatsapp || 'default'}
                  onChange={handleChange(key, 'whatsapp')}
                >
                  <option value="default">Default</option>
                  {whatsappOptions.map((e, i) => <option key={i} value={e}>{e}</option>)}
                </select>
              </div>
            ))}
          </div>
          <div className="text-center pb-1">
            <button
              onClick={handleSave}
              className="bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-500"
            >
              Save Changes
            </button>
          </div>
        </div>
      </div>

      {showPopup && (
        <div className="fixed inset-0 z-60 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded shadow-lg text-center">
            <h4 className="text-lg font-semibold mb-4">Permission Updated Successfully!</h4>
            <button
              onClick={() => setShowPopup(false)}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              OK
            </button>
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
}