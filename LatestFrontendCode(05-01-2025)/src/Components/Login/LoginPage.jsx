import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import Logo from "../../Image/ApnaCloud.png";
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import config from "../../config";
import { useAuth } from "../../AuthContext";
import axiosInstance from "../../axiosinstance";
import { useToast } from "../../ToastProvider";
import { jwtDecode } from "jwt-decode";

// const LoginLoadingAnimation = () => {
//   return (
//     <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
//       <div className="bg-white rounded-2xl p-8 flex flex-col items-center space-y-6 shadow-2xl">
//         {/* Animated Logo */}
//         <div className="relative">
//           <div className="w-16 h-16 bg-indigo-600 rounded-full animate-pulse"></div>
//           <div className="absolute inset-2 w-12 h-12 bg-white rounded-full flex items-center justify-center">
//             <Loader2 className="w-6 h-6 text-indigo-600 animate-spin" />
//           </div>
//         </div>

//         {/* Loading Text with Animation */}
//         <div className="text-center">
//           <h3 className="text-xl font-semibold text-gray-800 mb-2">Signing you in...</h3>
//           <div className="flex items-center space-x-1">
//           </div>
//         </div>

//         {/* Progress Bar */}
//         <div className="w-64 bg-gray-200 rounded-full h-2">
//           <div className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full animate-pulse"></div>
//         </div>

//         {/* Loading Steps */}
//         <div className="text-sm text-gray-500 text-center">
//           <div className="flex items-center justify-center space-x-2">
//             <div className="flex items-center space-x-2">
//               <div className="w-2 h-2 bg-green-500 rounded-full"></div>
//               <span>Verifying credentials</span>
//             </div>
//           </div>
//           <div className="flex items-center justify-center space-x-2 mt-1">
//             <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></div>
//             <span>Loading your dashboard</span>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [loginEmail, setLoginEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { showToast } = useToast();
  const navigate = useNavigate();
  const { login, encryptData } = useAuth();

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoginError("");
    setIsLoading(true);

    try {
      const response = await axiosInstance.post(`${config.API.Server_URL}/login`, {
        email: loginEmail,
        password: password,
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 200) {
        const data = response.data;
        
        if ((data.status) && (data.data.role === "Admin")) {
          // Ensure all values passed to encryptData are strings
          localStorage.setItem('adminn', encryptData(String(data.data.email || '')));
          localStorage.setItem("admin_email", encryptData(String(data.data.email || '')));
          localStorage.setItem('AccessToken', (data.data.access || '')); // AccessToken can remain unencrypted if it's a short-lived token
          localStorage.setItem('RefreshToken', (data.data.refresh || '')); // AccessToken can remain unencrypted if it's a short-lived token
          localStorage.setItem('first_name', encryptData(String(data.data.first_name || '')));
          localStorage.setItem('last_name', encryptData(String(data.data.last_name || '')));
          localStorage.setItem('designation', encryptData(String(data.data.designation || '')));
          localStorage.setItem('role', encryptData(String(data.data.role || '')));
          localStorage.setItem('Admin Profile', String(data?.data?.image_url || '')); // URLs typically don't need encryption, but ensure string
          localStorage.setItem('Phone No.', encryptData(String(data.data.mobile || '')));
          localStorage.setItem('email', encryptData(String(data.data.email || '')));
          localStorage.setItem('status', encryptData(String(data.data.status || '')));
          localStorage.setItem('last_login', encryptData(String(data.data.last_login || '')));
          localStorage.setItem('last_sync', encryptData(String(data.data.timestamp || '')));

          const orgDetails = data.data.organization_details || {};
          localStorage.setItem('org_address', encryptData(String(orgDetails.address || '')));
          localStorage.setItem('org_admin_users', encryptData(String(orgDetails.admin_users || '')));
          localStorage.setItem('org_domain', encryptData(String(orgDetails.domain || '')));
          localStorage.setItem('org_employee_users', encryptData(String(orgDetails.employee_users || '')));
          localStorage.setItem('org_expiry', encryptData(String(orgDetails.expiry || '')));
          localStorage.setItem('org_favicon_url', encryptData(String(orgDetails.favicon_url || '')));
          localStorage.setItem('org_gst_no', encryptData(String(orgDetails.gst_no || '')));
          localStorage.setItem('org_id', encryptData(String(orgDetails.id || '')));
          localStorage.setItem('org_limit_of_days', encryptData(String(orgDetails.limit_of_days || '')));
          localStorage.setItem('org_limit_of_agents', encryptData(String(orgDetails.limit_of_agents || '')));
          localStorage.setItem('org_limit_of_users', encryptData(String(orgDetails.limit_of_users || '')));
          localStorage.setItem('org_logo_url', encryptData(String(orgDetails.logo_url || '')));
          localStorage.setItem('org_mobile', encryptData(String(orgDetails.mobile || '')));
          localStorage.setItem('org_name', encryptData(String(orgDetails.name || '')));
          localStorage.setItem('org_pan_no', encryptData(String(orgDetails.pan_no || '')));
          localStorage.setItem('org_station', encryptData(String(orgDetails.station || '')));
          localStorage.setItem('org_status', encryptData(String(orgDetails.status || '')));
          localStorage.setItem('org_timestamp', encryptData(String(orgDetails.timestamp || '')));
          localStorage.setItem('org_umi', encryptData(String(orgDetails.umi || '')));
          localStorage.setItem('timestamp', encryptData(String(orgDetails.utimestamp || '')));

          const selectedCard = response.data.selected_card || [];
          localStorage.setItem('selected_card', JSON.stringify(selectedCard));
          const switches = response.data.switches || {};
          localStorage.setItem('switches', JSON.stringify(switches));
          const storageStates = response.data.storageStates || {};
          if (storageStates.Nas === false) {
            delete storageStates.Nas;
          }
          localStorage.setItem('storageStates', encryptData(JSON.stringify(storageStates)));
          const Permissions = data.Permissions || {};
          localStorage.setItem('permission', encryptData(JSON.stringify(Permissions))); // Permissions object needs stringify before encryption

          login(data.data.access); // Call login from AuthContext
          navigate('/');
          showToast("Login Successfull", "success");
        } else if (data.role === "Employee" || data.role === 'employee' || data.role === 'EMPLOYEE') {
          // Ensure all values passed to encryptData are strings
          localStorage.setItem('user_profile', String(data.profilePhoto || ''));
          localStorage.setItem('org_name', encryptData(String(data.companyName || '')));
          localStorage.setItem('user_designation', encryptData(String(data.designation || '')));
          localStorage.setItem('user_email', encryptData(String(data.email || '')));
          localStorage.setItem('user_Phone No.', encryptData(String(data.mobileNumber || '')));
          localStorage.setItem('first_name', encryptData(String(data.name || '')));
          localStorage.setItem('last_name', encryptData(String(data.lname || '')));
          // localStorage.setItem('user_privileges', encryptData(JSON.stringify(data.privileges)));
          localStorage.setItem('user_privileges', encryptData(JSON.stringify(jwtDecode(data.prev))));
          localStorage.setItem('user_role', encryptData(String(data.role || '')));
          localStorage.setItem('last_login', encryptData(String(data.last_login || '')));
          localStorage.setItem('limit_of_users', encryptData(String(data.limit_of_users || '')));
          localStorage.setItem('admin_email', encryptData(String(data.admin_email || '')));
          localStorage.setItem('admin_name', encryptData(String(data.admin_name || '')));
          localStorage.setItem('admin_img', String(data.admin_img_url || ''));
          localStorage.setItem('AccessToken', (data.access || ''));
          localStorage.setItem('RefreshToken', (data.refresh || ''));

          const selectedCard = response.data.selected_card || [];
          localStorage.setItem('selected_card', JSON.stringify(selectedCard));
          const switches = response.data.switches || {};
          localStorage.setItem('switches', JSON.stringify(switches));
          const storageStates = response.data.storageStates || {};
          if (storageStates.Nas === false) {
            delete storageStates.Nas;
          }
          localStorage.setItem('storageStates', encryptData(JSON.stringify(storageStates)));

          login(data.access); // Call login from AuthContext
          navigate('/');
          showToast("Login Successfull", "success");
        } else {
          throw new Error(data.message || 'Failed to authenticate');
        }
      } else {
        throw new Error('Failed to authenticate');
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error?.response?.status === 403) {
        setLoginError("You are out of organization!")
        showToast("You are out of organization!", "error")
      } else if (error?.response?.status === 401) {
        setLoginError("YOUR LICENSE HAS EXPIRED, PLEASE UPGRADE YOUR LICENSE!")
        showToast("YOUR LICENSE HAS EXPIRED, PLEASE UPGRADE YOUR LICENSE!", "error")
      } else {
        setLoginError("Invalid user ID and Password!");
        showToast("Invalid user ID and Password!", "error")
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Loading Animation Overlay */}
      {isLoading}

      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="w-full max-w-md p-8 bg-white rounded-xl shadow-md">
          <div className="flex flex-col items-center mb-6">
            <div className="rounded-md">
              <img src={Logo} width={100} alt="ApnaCloud Logo" />
            </div>
          </div>

          <div className="text-gray-700 text-lg font-semibold mb-4 flex justify-between items-center">
            <span>Sign in</span>
            <a href={`${config.API.SIGNUP_URL}`} className="text-sm text-indigo-600 hover:underline">
              Create an account
            </a>
          </div>

          {loginError && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm">
              {loginError}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleLoginSubmit}>
            <input
              type="email"
              placeholder="Enter your email"
              value={loginEmail}
              onChange={(e) => setLoginEmail(e.target.value)}
              required
              disabled={isLoading}
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
                className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <span
                  className={`password-toggle ${isLoading ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
                  onClick={() => !isLoading && setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </span>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <Link
                to="/forgot-password"
                className={`text-sm text-indigo-600 hover:underline ${isLoading ? 'pointer-events-none opacity-50' : ''}`}
              >
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <span>Sign in</span>
              )}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}

export default LoginPage;