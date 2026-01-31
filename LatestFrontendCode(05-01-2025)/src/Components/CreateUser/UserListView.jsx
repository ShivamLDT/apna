import { useState, useEffect } from "react";
import UserList from "../Reports/UserList";
import { Mail, Phone, Clock, Briefcase, Trash2, SquarePen, Eye, X, Check, AlertCircle } from 'lucide-react';
import useUserList from "../../Hooks/useUserList";
import CryptoJS from "crypto-js";
import LoadingComponent from "../../LoadingComponent";

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

const UserListView = ({ onEdit, onDelete, refreshTrigger = 0 }) => {
  const {
    filteredUsers,
    searchTerm,
    handleSearchChange,
    loading,
    error,
  } = useUserList(refreshTrigger);

  const role = decryptData(localStorage.getItem("user_role"));

  const [privileges, setPrivileges] = useState({});

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

  const canEdit = () => {
    if (role !== "Employee") return true;
    return privileges.userUpdate;
  };

  const canDelete = () => {
    if (role !== "Employee") return true;
    return privileges.userDelete;
  };

  const canView = () => {
    if (role !== "Employee") return true;
    return privileges.userRead;
  };

  const showActionsColumn = hasActionPermissions() && (canEdit() || canDelete());

  // if (loading) {
  //   return (
  //     <>
  //       <div className="flex items-center justify-center h-full">
  //         <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
  //           <div className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
  //             style={{ animation: 'oceanSlide 3s infinite' }} />
  //           <style>{`
  //       @keyframes oceanSlide {
  //         0% { transform: translateX(-150%); }
  //         66% { transform: translateX(0%); }
  //         100% { transform: translateX(150%); }
  //       }
  //     `}</style>
  //         </div>
  //       </div>
  //     </>
  //   );
  // }

  if (loading) {
    return <LoadingComponent />;
  }


  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center p-8">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Error loading users</h3>
          <p className="text-gray-500 dark:text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  // If user doesn't have read permission, show access denied message
  if (role === "Employee" && !canView()) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center p-8">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Access Denied</h3>
          <p className="text-gray-500 dark:text-gray-400">You don't have permission to view the user list.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full relative overflow-x-auto shadow-md sm:rounded-lg">
      <div className="flex items-center justify-between flex-column flex-wrap md:flex-row space-y-4 md:space-y-0 pb-4 bg-white dark:bg-gray-900">
        <label htmlFor="table-search" className="sr-only">Search</label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <svg className="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
              <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z" />
            </svg>
          </div>
          <input
            type="text"
            id="table-search-users"
            className="block w-80 pl-10 pr-3 py-2 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 transition-colors duration-200"
            placeholder="Search for users"
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </div>
      </div>

      <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
        <thead className="text-xs text-gray-700 bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
          <tr>
            <th scope="col" className="px-2 py-2">
              User
            </th>
            <th scope="col" className="px-2 py-2">
              Designation
            </th>
            <th scope="col" className="px-2 py-2">
              Mobile
            </th>
            <th scope="col" className="px-2 py-2">
              Created At
            </th>
            <th scope="col" className="px-2 py-2">
              Modified At
            </th>
            {showActionsColumn && (
              <th scope="col" className="px-2 py-2">
                Actions
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {filteredUsers.length > 0 ? (
            filteredUsers.map((user, index) => (
              <tr key={user.id || index} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors duration-200">
                <th scope="row" className="flex items-center gap-5 px-2 py-2 text-gray-900 whitespace-nowrap dark:text-white">
                  {user.profilePhoto && user.profilePhoto.startsWith('data:image') ? (
                    <img
                      className="w-10 h-10 rounded-full object-cover"
                      src={user.profilePhoto}
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full flex items-center justify-center bg-blue-600 text-white font-bold text-lg uppercase">
                      {user.name && user.name.charAt(0)}{user.lname && user.lname.charAt(0)}
                    </div>
                  )}
                  <div className="ps-3">
                    <div className="text-base font-semibold">{user.name} {user.lname}</div>
                    <div className="font-normal text-gray-500">{user.email}</div>
                  </div>
                </th>
                <td className="px-2 py-2">
                  {user.designation}
                </td>
                <td className="px-2 py-2">
                  {user.mobileNumber}
                </td>
                <td className="px-2 py-2">
                  {new Date(user.createdTime).toLocaleString()}
                </td>
                <td className="px-2 py-2">
                  {new Date(user.modifyTime).toLocaleString()}
                </td>
                {showActionsColumn && (
                  <td>
                    <div className="flex flex-wrap gap-1">
                      {canEdit() && (
                        <button
                          onClick={() => onEdit(user)}
                          className="p-1.5 text-green-600 hover:text-green-900 transition-colors"
                          title="Edit"
                        >
                          <SquarePen size={16} />
                        </button>
                      )}

                      {canDelete() && (
                        <button
                          onClick={() => onDelete(user)}
                          className="p-1.5 text-red-600 hover:text-red-900 transition-colors"
                          title="Delete"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  </td>
                )}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={showActionsColumn ? "6" : "5"} className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                {searchTerm ? 'No users found matching your search.' : 'No users available.'}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default UserListView;