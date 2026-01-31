import React, { useState, useEffect, useContext, useMemo, useRef } from 'react';
import { Backupindex } from '../../../Context/Backupindex';
import config from '../../../config';
import "./RestoreBackupModel.css";
import axios from 'axios';
import axiosInstance from '../../../axiosinstance';
import { AlertTriangle, ChevronRight, Folder, Home, RefreshCcw } from 'lucide-react';
import { debounce } from "lodash";
import { UIContext } from '../../../Context/UIContext';
import Drive from "../../../assets/drive.png"
import LoadingComponent from '../../../LoadingComponent';

const RestoreBackupModel = ({ setEndPointListPopup, setShowRestorePopup, setShowpopup, setSourceCheck }) => {
  const { checkBoxData, endPointAgentName, sourceData, setSourceData, setGetRestoreData } = useContext(Backupindex);

  // CRITICAL FIX: Initialize checkedPaths from sourceData only once when dialog opens
  const [initialSourceData] = useState(sourceData || []); // Store original on mount
  const [checkedPaths, setCheckedPaths] = useState([...initialSourceData]); // Use spread to create new array

  const [expandedPaths, setExpandedPaths] = useState(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [path, setPath] = useState('');
  const [rootDrives, setRootDrives] = useState([]);
  const [loadingBar, setLoadingBar] = useState(true);
  const [expandingPath, setExpandingPath] = useState(null);
  const [treeData, setTreeData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const controllerRef = useRef(null);
  const [searchMode, setSearchMode] = useState("path");
  const [innerPath, setIneerPath] = useState('');
  const [openInput, setOpenInput] = useState(false);
  const [isOpenInput, setIsOpenInput] = useState(false);
  const [searchPath, setSearchPath] = useState('');
  const [filteredItems, setFilteredItems] = useState([]);
  const [isUseTree, setIsUseTree] = useState(false);
  const [navigationPath, setNavigationPath] = useState([])
  const [originalDelimiters, setOriginalDelimiters] = useState([]);
  const [showHover, setShowHover] = useState(false);
  const [confirmModal, setConfirmModal] = useState({
    isOpen: false,
    pendingPath: null,
    oldDrive: '',
    newDrive: ''
  });

  const { setPopupEnable, setonechecktable, setonecheckendpointlisttable, setShowEndpointBackup, setShowTreePopup } = useContext(UIContext);

  function normalizePath(p) {
    if (!p) return p;
    return p
      .replace(/\\\\/g, "\\")
      .replace(/\/+/g, "\\")
      .replace(/\\+/g, "\\")
      .replace(/^([A-Za-z]):\\+/, "$1:\\");
  }

  const getIcon = (segment, index) => {
    if (index === 0 && (segment.includes(":") || segment === "Amazon S3")) {
      return <Home onClick={handleHomeClick} className="w-4 h-4" />;
    } else {
      return <Folder className="w-4 h-4" />;
    }
  };

  const handleHomeClick = () => {
    setPath('');
    setTimeout(() => {
      setSearchPath('');
    }, 100)
  }

  const parsePathWithDelimiters = (path) => {
    if (!path) return { segments: [], delimiters: [] };
    const delimiters = [];
    const segments = [];
    let currentSegment = '';

    for (let i = 0; i < path.length; i++) {
      const char = path[i];
      if (char === '\\' || char === '/') {
        if (currentSegment) {
          segments.push(currentSegment);
          delimiters.push(char);
          currentSegment = '';
        }
      } else {
        currentSegment += char;
      }
    }

    if (currentSegment) {
      segments.push(currentSegment);
    }

    return { segments: segments.filter(seg => seg !== ''), delimiters };
  };

  useEffect(() => {
    if (searchPath) {
      const { segments, delimiters } = parsePathWithDelimiters(searchPath);
      setNavigationPath(segments);
      setOriginalDelimiters(delimiters);
    }
  }, [searchPath])

  function splitPath(p) {
    return p.replace(/\\/g, "/").split("/").filter(Boolean);
  }

  function getDisplayName(p) {
    const parts = splitPath(p);
    return parts[parts.length - 1] || p;
  }

  function prettyName(p) {
    const last = getDisplayName(p);
    return /^[A-Z]:$/i.test(last) ? `${last}\\` : last;
  }

  function insertIntoTree(prev, fullPath, contents) {
    const parts = splitPath(fullPath);
    let node = { ...prev };
    let current = node;
    let currentPath = "";

    parts.forEach((part, idx) => {
      currentPath = idx === 0 ? part : `${currentPath}//${part}`;
      if (!current[currentPath]) current[currentPath] = [];
      if (idx === parts.length - 1) current[currentPath] = contents;
    });
    return node;
  }

  const fetchDrives = async () => {
    try {
      setLoadingBar(true);
      const token = localStorage.getItem("AccessToken");
      const res = await axiosInstance.post(
        `${config.API.Server_URL}/api/browse`,
        { path: "", node: endPointAgentName },
        { headers: { "Content-Type": "application/json", token } }
      );
      setRootDrives(res.data?.paths || []);
    } catch (err) {
      // console.error("Drive fetch failed", err);
    } finally {
      setLoadingBar(false);
    }
  };

  useEffect(() => {
    fetchDrives();
  }, [endPointAgentName]);

  async function expandFullPath(fullPath) {
    const segments = splitPath(fullPath);
    let currentPath = "";
    for (let i = 0; i < segments.length; i++) {
      currentPath = i === 0 ? segments[i] : `${currentPath}//${segments[i]}`;
      if (!treeData[currentPath]) {
        try {
          const token = localStorage.getItem("AccessToken");
          const res = await axiosInstance.post(`${config.API.Server_URL}/api/browse`, {
            path: currentPath,
            node: endPointAgentName
          }, { headers: { "Content-Type": "application/json", token } });
          const contents = res.data?.paths?.[0]?.contents || [];
          setTreeData(prev => insertIntoTree(prev, currentPath, contents));
        } catch (err) {
          break;
        }
      }
      await new Promise(r => setTimeout(r, 0));
      requestAnimationFrame(() => showChildren(currentPath, i + 1));
    }
  }

  const fetchSearch = async (value) => {
    if (!value) return;

    if (controllerRef.current) {
      controllerRef.current.abort();
    }

    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("AccessToken");
      const res = await axiosInstance.post(
        `${config.API.Server_URL}/api/browse`,
        { path: value, node: endPointAgentName },
        {
          headers: { "Content-Type": "application/json", token },
          signal: controller.signal,
          timeout: 10000,
        }
      );
      const contents = res.data?.paths?.[0]?.contents || [];
      if (contents.length === 0) {
        setError("Path not found");
      }
      setSearchResults(contents);
    } catch (err) {
      if (axios.isCancel(err)) {
        return;
      }
      setError("Path not found");
    } finally {
      setLoading(false);
    }
  }

  const debouncedFetch = useMemo(() => debounce(fetchSearch, 300), []);

  const handleChange = (e) => {
    const value2 = e.target.value.trim();
    setPath(value2);
    if (e.key === "Enter") {
      setIsOpenInput(false);
      debouncedFetch(value2);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      const value2 = e.target.value.trim();
      setPath(value2)
      setIsOpenInput(false);
      debouncedFetch(value2);
    }
  };

  const getRootDrive = (fullPath) => {
    if (!fullPath) return "";
    const normalized = normalizePath(fullPath);
    const root = normalized.split('\\')[0];
    return root ? root.toUpperCase() : "";
  };

  const handleConfirmSwitch = () => {
    const path = confirmModal.pendingPath;
    if (!path) return;
    // FIXED: Only update local state
    setCheckedPaths([path]);
    setConfirmModal({ isOpen: false, pendingPath: null, oldDrive: '', newDrive: '' });
  };

  const isAncestryChecked = (currentPath) => {
    const normalizedCurrent = normalizePath(currentPath);
    if (checkedPaths.includes(normalizedCurrent)) return true;
    return checkedPaths.some(parentPath => {
      const normalizedParent = normalizePath(parentPath);
      if (normalizedParent.match(/^[A-Za-z]:\\$/)) {
        return normalizedCurrent.startsWith(normalizedParent);
      }
      return normalizedCurrent.startsWith(normalizedParent + '\\');
    });
  };

  const isNodeChecked = (currentPath) => {
    if (checkedPaths.includes(currentPath)) return true;
    return checkedPaths.some(parentPath => {
      if (currentPath.startsWith(parentPath)) {
        const remainder = currentPath.slice(parentPath.length);
        return remainder.startsWith('\\') || (parentPath.endsWith(':') && remainder.startsWith('\\'));
      }
      return false;
    });
  };

  const isDescendantChecked = (currentPath) => {
    if (checkedPaths.includes(currentPath)) return true;
    return checkedPaths.some(parentPath => {
      const normalizedParent = normalizePath(parentPath);
      const normalizedCurrent = normalizePath(currentPath);
      if (normalizedCurrent.startsWith(normalizedParent)) {
        const remainder = normalizedCurrent.slice(normalizedParent.length);
        return normalizedParent.endsWith('\\') || remainder.startsWith('\\');
      }
      return false;
    });
  };

  // FIXED: Only update local checkedPaths, NOT sourceData
  function HandlePathCheckBox(rawPath, isChecked) {
    const path = normalizePath(rawPath);

    if (!isChecked) {
      setCheckedPaths(prev => prev.filter(p => !p.startsWith(path)));
      return;
    }

    if (checkedPaths.length > 0) {
      const existingRoot = getRootDrive(checkedPaths[0]);
      const newRoot = getRootDrive(path);

      if (existingRoot !== newRoot) {
        setConfirmModal({
          isOpen: true,
          pendingPath: path,
          oldDrive: existingRoot,
          newDrive: newRoot
        });
        return;
      }
    }

    const newPath = path;
    const filteredChecked = checkedPaths.filter(existing => !existing.startsWith(newPath + "\\"));
    const finalCheckedPaths = [...filteredChecked, newPath];

    // FIXED: Only update local state
    setCheckedPaths(finalCheckedPaths);
  }

  const toggleExpand = async (iconEl, path, level) => {
    const expanded = iconEl.classList.contains("expanded");
    if (expanded) {
      if (level == 1) {
        setOpenInput(false);
      }
      iconEl.classList.remove("expanded");
      iconEl.classList.add("collapsed");
      hideChildren(path);
      setExpandedPaths(prev => {
        const newSet = new Set(prev);
        newSet.delete(path);
        return newSet;
      });
    } else {
      setOpenInput(true);
      iconEl.classList.remove("collapsed");
      iconEl.classList.add("expanded");
      setExpandedPaths(prev => new Set(prev).add(path));
      if (treeData[path]) {
        requestAnimationFrame(() => showChildren(path, level + 1));
      } else {
        setExpandingPath(path);
        try {
          const token = localStorage.getItem("AccessToken");
          const res = await axiosInstance.post(`${config.API.Server_URL}/api/browse`, {
            path, node: endPointAgentName
          }, { headers: { "Content-Type": "application/json", token } });
          const contents = res.data?.paths?.[0]?.contents || [];
          setTreeData(prev => ({ ...prev, [path]: contents }));
          setTimeout(() => requestAnimationFrame(() => showChildren(path, level + 1)), 0);
        } catch (err) {
        } finally {
          setExpandingPath(null);
        }
      }
    }
  };

  function hideChildren(parentPath) {
    document.querySelectorAll('.tree-item').forEach(item => {
      if (item.dataset.parent?.startsWith(parentPath)) {
        item.classList.add("tg-hidden");
        const icon = item.querySelector('.expand-icon.expanded');
        if (icon) {
          icon.classList.remove("expanded");
          icon.classList.add("collapsed");
        }
      }
    });
  }

  function showChildren(parentPath, childLevel) {
    document.querySelectorAll('.tree-item').forEach(item => {
      if (item.dataset.parent === parentPath && parseInt(item.dataset.level) === childLevel) {
        item.classList.remove("tg-hidden");
      }
    });
  }

  const showParentItems = (item) => {
    const parentPath = item.dataset.parent;
    if (!parentPath) return;

    const parent = document.querySelector(`.tree-item[data-path="${parentPath}"]`);
    if (parent) {
      parent.style.display = '';
      const expandIcon = parent.querySelector('.expand-icon');
      if (expandIcon) {
        expandIcon.classList.remove('collapsed');
        expandIcon.classList.add('expanded');
      }
      showParentItems(parent);
    }
  };

  const filterTree = (term) => {
    setSearchTerm(term);
    setIneerPath(term);

    const allItems = document.querySelectorAll('.tree-item');

    if (!term || term.length === 0) {
      allItems.forEach(item => {
        item.style.display = '';
      });
      return;
    }

    const searchTerm = term.toLowerCase();

    allItems.forEach(item => {
      const itemName = item.querySelector('.item-name')?.textContent.toLowerCase() || '';
      const expandIcon = item.querySelector('.expand-icon');

      const childMatches = Array.from(item.querySelectorAll('.item-name'))
        .some(child => child.textContent.toLowerCase().includes(searchTerm));

      if (itemName.includes(searchTerm) || childMatches) {
        item.style.display = '';
        showParentItems(item);

        if (expandIcon && expandIcon.classList.contains("expanded")) {
          const children = document.querySelectorAll(`.tree-item[data-parent="${item.dataset.path}"]`);
          children.forEach(child => {
            child.style.display = '';
          });
        }
      } else {
        item.style.display = 'none';
      }
    });
  };

  async function handleChangeData(e) {
    const value = e.target.value.trim();

    try {
      const token = localStorage.getItem("AccessToken");
      const res = await axiosInstance.post(`${config.API.Server_URL}/api/browse`, {
        path: value, node: endPointAgentName
      }, { headers: { "Content-Type": "application/json", token } });
      const contents = res.data?.paths?.[0]?.contents || [];
      setTreeData(prev => insertIntoTree(prev, value, contents));
      await expandFullPath(value);
    } catch (err) {
    }
  }

  const renderTreeItems = (path, level = 1) => {
    let items;

    if (isUseTree) {
      if (path === "C:\\" && filteredItems.length > 0) {
        items = filteredItems;
      } else {
        items = [];
      }
    } else {
      items = treeData[path];
    }

    if (items && items.length === 0 && expandedPaths.has(path)) {
      return (
        <div
          className="tree-item"
          data-level={level}
          data-parent={path}
          style={{ paddingLeft: `${level * 53}px` }}
        >
          <div className="item-name" style={{ color: '#6b7280', fontStyle: 'italic' }}>
            No data available in this folder
          </div>
        </div>
      );
    }

    // if (!items || items.length === 0) return null;
    if (!items) return null;

    return items.map(item => {
      const isFolder = item.type === "directory";
      const fullPath = normalizePath(`${path}\\${item.name}`);

      return (
        <React.Fragment key={isUseTree ? item?.id : fullPath}>
          <div
            className="tree-item tg-hidden"
            data-level={level}
            data-parent={path}
            data-path={fullPath}
          >
            {Array.from({ length: level }).map((_, i) =>
              <div key={i} className="indent" />
            )}

            <div
              className={`expand-icon ${isFolder ? "expandable collapsed" : ""}`}
              onClick={(e) => isFolder && toggleExpand(e.currentTarget, fullPath, level)}
            />

            <input
              type="checkbox"
              checked={isAncestryChecked(fullPath)}
              disabled={isAncestryChecked(fullPath) && !checkedPaths.includes(fullPath)}
              onChange={(e) => HandlePathCheckBox(fullPath, e.target.checked)}
              className="item-checkbox"
            />

            <div className="item-icon">{isFolder ? "📁" : "📄"}</div>
            <div className="item-name">{getDisplayName(fullPath)}</div>
            {isFolder && fullPath === expandingPath && (
              <div className="folder-loader">
                <div className="folder-loader-spinner"></div>
              </div>
            )}
          </div>

          {!isUseTree && treeData[fullPath] && renderTreeItems(fullPath, level + 1)}
        </React.Fragment>
      );
    });
  };

  // FIXED: Reset to original state on cancel
  const closeDialog = () => {
    setCheckedPaths([...initialSourceData]); // Reset to original
    setShowpopup(false);
    setShowTreePopup(false);
    setEndPointListPopup(false);
    setShowRestorePopup(true);
    setPopupEnable(false);
  };

  // FIXED: Save changes to sourceData only when user clicks Save
  const saveSelection = () => {
    setSourceData(checkedPaths); // Commit changes
    setGetRestoreData(checkedPaths); // Commit changes

    setShowEndpointBackup(true);
    setShowpopup(false);
    setonechecktable(false);
    setonecheckendpointlisttable(false);
    setSourceCheck(true);
    setPopupEnable(false);
    setShowTreePopup(false);
    setEndPointListPopup(false);
    setShowRestorePopup(true);
  };

  const handlePathClick = (index) => {
    const selectedSegments = navigationPath.slice(0, index + 1);
    const selectedDelimiters = originalDelimiters.slice(0, index);

    let reconstructedPath = '';
    for (let i = 0; i < selectedSegments.length; i++) {
      reconstructedPath += selectedSegments[i];
      if (i < selectedDelimiters.length) {
        reconstructedPath += selectedDelimiters[i];
      }
    }

    let apiPath = reconstructedPath;
    if (isDriveLetter(reconstructedPath)) {
      apiPath = reconstructedPath + "\\";
    }
    debouncedFetch(apiPath);
    setSearchPath(reconstructedPath);
  };

  const isDriveLetter = (path) => {
    return /^[A-Za-z]:$/.test(path);
  };

  return (
    <div className="dialog-container">
      <div className="dialog">
        <div className="dialog-header">
          <h2 className="dialog-title">Select Folder or File Location</h2>
          <input
            type="text"
            className="search-input"
            placeholder="Type or paste path and press Enter..."
            value={searchPath}
            onChange={(e) => setSearchPath(e.target.value.trim())}
            onKeyDown={(e) => handleKeyDown(e)}
          />
          <button onClick={fetchDrives}>
            <RefreshCcw size={20} />
          </button>

          <button
            className="close-btn "
            onClick={closeDialog}
          >
            &times;
          </button>
        </div>

        {loadingBar ? (
          // <div className="flex items-center justify-center h-full">
          //   <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
          //     <div
          //       className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
          //       style={{ animation: 'oceanSlide 3s infinite' }}
          //     />
          //     <style>{`
          //           @keyframes oceanSlide {
          //             0% { transform: translateX(-150%); }
          //             66% { transform: translateX(0%); }
          //             100% { transform: translateX(150%); }
          //             }
          //             `}</style>
          //   </div>
          // </div>

          <LoadingComponent />
        ) : (
          <>
            <div className="folder-tree">

              {path && path.length > 0 && (
                <div className="search-results">
                  {loading ? (
                    <div className="flex items-center justify-center h-32">
                      <div className="relative w-80 h-4 bg-blue-200 rounded-xl overflow-hidden">
                        <div
                          className="absolute inset-0 bg-blue-600 w-3/5 rounded-xl transform -translate-x-full"
                          style={{ animation: "oceanSlide 3s infinite" }}
                        />
                        <style>{`
                              @keyframes oceanSlide {
                                0% { transform: translateX(-150%); }
                                66% { transform: translateX(0%); }
                                100% { transform: translateX(150%); }
                              }
                        `}</style>
                      </div>
                    </div>
                  ) : error ? (
                    <h1 className="text-center text-red-600 font-semibold py-6">
                      {error}
                    </h1>
                  ) : searchResults?.length === 0 ? (
                    <h1 className="text-center text-gray-500 font-medium py-6">
                      No Data Found
                    </h1>
                  ) : (
                    <>
                      <div className='flex'>
                        <div className="bg-gray-50 border border-gray-200 rounded-lg  folder_Bar">
                          <div className="flex items-center space-x-1 overflow-x-auto custom-scbar">
                            {navigationPath?.length > 0 ? (
                              navigationPath.map((path, index) => {
                                const isFirst = index === 0 && (path.includes(":") || path === "Amazon S3");

                                return (
                                  <div key={index} className="flex items-center space-x-1">
                                    <button
                                      onClick={() => handlePathClick(index)}
                                      className={`flex items-center space-x-2 px-3 py-1 text-sm text-blue-600 rounded-md transition-colors duration-200 whitespace-nowrap
            ${isFirst ? "mr-2" : "hover:text-blue-800 hover:bg-blue-50"}
          `}
                                    >
                                      {getIcon(path, index)}
                                      <span>{getDisplayName(path)}</span>
                                    </button>

                                    {index < navigationPath.length - 1 && (
                                      <ChevronRight className="w-4 h-4 text-gray-400" />
                                    )}
                                  </div>
                                );
                              })
                            ) : (
                              <span className="text-gray-500 italic">No path selected</span>
                            )}
                          </div>
                        </div>
                        <div>
                          <input
                            type="text"
                            className="search-input-inner"
                            placeholder={"Search your Folder"}
                            value={innerPath}
                            onChange={(e) => filterTree(e.target.value)}
                          />

                        </div>
                      </div>

                      {searchResults.map((item) => {
                        const level = 1;
                        const isFolder = item.type === "directory";
                        const fullPath = normalizePath(item.path);

                        return (
                          <React.Fragment key={fullPath}>
                            <div
                              className="tree-item"
                              data-level={level}
                              data-parent={path}
                              data-path={fullPath}
                            >
                              {Array.from({ length: level }).map((_, i) => (
                                <div key={i} className="indent" />
                              ))}

                              <div
                                className={`expand-icon ${isFolder ? "expandable collapsed" : ""
                                  }`}
                                onClick={(e) =>
                                  isFolder && toggleExpand(e.currentTarget, fullPath, level)
                                }
                              />

                              <input
                                type="checkbox"
                                checked={checkedPaths.includes(fullPath)}
                                onChange={(e) =>
                                  HandlePathCheckBox(fullPath, e.target.checked)
                                }
                                className="item-checkbox"
                              />

                              <div className="item-icon">{isFolder ? "📁" : "📄"}</div>
                              <div className="item-name">{getDisplayName(fullPath)}</div>
                            </div>

                            {treeData[fullPath] && renderTreeItems(fullPath, level + 1)}
                          </React.Fragment>
                        );
                      })}
                    </>
                  )}
                </div>
              )}

              {!path ? (
                <>
                  <div className="tree-item" data-level="0" data-parent="">
                    <div className="item-icon">🖥️</div>

                    <div className="item-name">{endPointAgentName}</div>
                  </div>

                  {openInput ? <input
                    type="text"
                    className="search-input-inner"
                    placeholder={"Search your Folder"}
                    value={innerPath}
                    onChange={(e) => filterTree(e.target.value)}
                  /> : ""}
                  {rootDrives.map(drive => (
                    <React.Fragment key={drive.path}>
                      <div className="tree-item" data-level="1" data-parent="" data-path={drive.path}>
                        <div className="indent"></div>
                        <div className="expand-icon expandable collapsed"
                          onClick={(e) => toggleExpand(e.currentTarget, drive.path, 1)} />
                        <input type="checkbox"
                          checked={isAncestryChecked(drive.path)}
                          onChange={(e) => HandlePathCheckBox(drive.path, e.target.checked)}
                          className="item-checkbox" />
                        <div className="item-icon"><img width="50" height="50" src={Drive} alt="hdd" /></div>
                        <div className="item-name">{prettyName(drive.path)}</div>
                        {drive.path === expandingPath && (
                          <div className="folder-loader">
                            <div className="folder-loader-spinner"></div>
                          </div>
                        )}
                      </div>
                      {treeData[drive.path] && renderTreeItems(drive.path, 2)}
                    </React.Fragment>
                  ))}
                </>
              ) : null}
            </div>

            <div className="dialog-footer">
              <div className="selected-info" id="selectedInfo">
                {checkedPaths.length === 0 ? "No items selected" :
                  `${checkedPaths.length} item(s) selected`}
              </div>
              <div className="footer-buttons">
                <button className="cancel-btn" onClick={closeDialog}>Cancel</button>
                <button className="save-btn2" onClick={saveSelection}>Save</button>
              </div>
            </div>
          </>
        )}
      </div>
      {confirmModal.isOpen && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-lg shadow-2xl w-full max-w-md border border-gray-200 overflow-hidden transform transition-all scale-100">

            <div className="bg-yellow-50 px-6 py-4 border-b border-yellow-100 flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-full">
                <AlertTriangle size={24} color='#d69e2e' />
              </div>
              <h3 className="text-lg font-semibold text-yellow-800">Switch Drive?</h3>
            </div>

            <div className="px-6 py-6">
              <p className="text-gray-700 text-sm leading-relaxed">
                You are switching from <span className="font-bold text-gray-900">{confirmModal.oldDrive}</span> to <span className="font-bold text-gray-900">{confirmModal.newDrive}</span>.
              </p>
              <p className="mt-3 text-gray-600 text-sm">
                If you proceed, all previously selected files will be <span className="text-red-600 font-medium">removed</span> from your selection.
              </p>
            </div>

            <div className="px-6 py-4 bg-gray-50 flex justify-end gap-3 border-t border-gray-100">
              <button
                onClick={() => setConfirmModal({ ...confirmModal, isOpen: false })}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmSwitch}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 shadow-sm transition-colors"
              >
                Yes, Change Drive
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RestoreBackupModel;