import React, { useState, useEffect, useContext } from "react";
import "./FileExtensions.css";
import FilterJson from "./FileExtensions.json";
import { Backupindex } from "../../Context/Backupindex";
import pdfIcon from "./ExtensionIcon/pdf.png";
import excelIcon from "./ExtensionIcon/excel.png";
import docxIcon from "./ExtensionIcon/docx.png";
import pptIcon from "./ExtensionIcon/ppt.png";
import exeIcon from "./ExtensionIcon/exe.png";
import textIcon from "./ExtensionIcon/text.png";
import jpgIcon from "./ExtensionIcon/jpg.png";
import pngIcon from "./ExtensionIcon/png.png";
import jpegIcon from "./ExtensionIcon/jpeg.png";
import gifIcon from "./ExtensionIcon/gif.png";
import zipIcon from "./ExtensionIcon/zip.png";
import mp3Icon from "./ExtensionIcon/mp3.png";
import mp4Icon from "./ExtensionIcon/mp4.png";
import rarIcon from "./ExtensionIcon/rar.png";
import csvIcon from "./ExtensionIcon/csv.png";
import sqlIcon from "./ExtensionIcon/sql.png";
import emlIcon from "./ExtensionIcon/eml.png";
import aiIcon from "./ExtensionIcon/ai.png";
import xmlIcon from "./ExtensionIcon/xml.png";
import DeleteIcon from "../../assets/delete.png";
import AlertComponent from "../../AlertComponent";

const iconMap = {
    "./ExtensionIcon/pdf.png": pdfIcon,
    "./ExtensionIcon/excel.png": excelIcon,
    "./ExtensionIcon/docx.png": docxIcon,
    "./ExtensionIcon/ppt.png": pptIcon,
    "./ExtensionIcon/exe.png": exeIcon,
    "./ExtensionIcon/text.png": textIcon,
    "./ExtensionIcon/jpg.png": jpgIcon,
    "./ExtensionIcon/png.png": pngIcon,
    "./ExtensionIcon/jpeg.png": jpegIcon,
    "./ExtensionIcon/gif.png": gifIcon,
    "./ExtensionIcon/zip.png": zipIcon,
    "./ExtensionIcon/mp3.png": mp3Icon,
    "./ExtensionIcon/mp4.png": mp4Icon,
    "./ExtensionIcon/rar.png": rarIcon,
    "./ExtensionIcon/csv.png": csvIcon,
    "./ExtensionIcon/sql.png": sqlIcon,
    "./ExtensionIcon/eml.png": emlIcon,
    "./ExtensionIcon/ai.png": aiIcon,
    "./ExtensionIcon/xml.png": xmlIcon,
};

const FileExtensions = ({ setFileNameSend }) => {
    const [data, setData] = useState([]);
    const [searchQuery, setSearchQuery] = useState(".");
    const [filteredResults, setFilteredResults] = useState([]);
    const [selectedValue, setSelectedValue] = useState([]);
    const [highlightedIndex, setHighlightedIndex] = useState(-1);
    const { setfileExtensionData, fileExtensionData, itemToDeleteFileExtension } = useContext(Backupindex);
    const [alert, setAlert] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            const jsonData = FilterJson;
            setData(jsonData);
        };
        fetchData();
    }, []);

    const SelectValue = (item) => {
        if (item.fileExtensions === '.all') {
            const updatedSelectedValue = [item];
            setSelectedValue(updatedSelectedValue);
            localStorage.setItem("SelectedExtension", JSON.stringify(updatedSelectedValue));
        } else {
            if (selectedValue.some(selectedItem => selectedItem.fileExtensions === '.all')) {
                setAlert({
                    message: "Already Selected all File Extension, Please Remove this",
                    type: 'error'
                });
            } else if (!selectedValue.some(selectedItem => selectedItem.fileExtensions === item.fileExtensions)) {
                const updatedSelectedValue = [...selectedValue, item];
                setSelectedValue(updatedSelectedValue);
                localStorage.setItem("SelectedExtension", JSON.stringify(updatedSelectedValue));
                localStorage.setItem("SelectedExtensionss", JSON.stringify(updatedSelectedValue));
            }
        }

        setSearchQuery(".");
        updateFilteredResults("");
        setHighlightedIndex(-1);
    };

    useEffect(() => {
        if (searchQuery === ".") {
            const results = data.filter(
                (item) =>
                    !selectedValue.some(
                        (selectedItem) => selectedItem.fileExtensions === item.fileExtensions
                    )
            );
            setFilteredResults(results);
            setHighlightedIndex(0);
        }
    }, [searchQuery, data, selectedValue]);

    useEffect(() => {
        if (selectedValue && selectedValue.length > 0) {
            const selectedNames = selectedValue.map(item => item.fileExtensions);
            const namesString = selectedNames.join(', ');
            setFileNameSend(namesString);
        } else {
            setFileNameSend('');
        }
    }, [selectedValue, setFileNameSend]);

    const SelectValueRemove = (item) => {
        setSelectedValue(prevValues => {
            const updatedValues = prevValues.filter(
                selectedItem => selectedItem.fileExtensions !== item.fileExtensions
            );

            if (updatedValues.length > 0) {
                localStorage.setItem("SelectedExtension", JSON.stringify(updatedValues));
                localStorage.setItem("SelectedExtensionss", JSON.stringify(updatedValues));
            } else {
                localStorage.removeItem("SelectedExtension");
                localStorage.removeItem("SelectedExtensionss");
            }

            return updatedValues;
        });
    };

    const handleSearch = (e) => {
        const query = e.target.value;
        setSearchQuery(query);
        updateFilteredResults(query);
        setHighlightedIndex(0);
    };

    const updateFilteredResults = (query) => {
        if (query) {
            const queryParts = query.toLowerCase().split(',').map(part => part.trim());
            const results = data.filter(item =>
                queryParts.some(part =>
                    (item.Name.toLowerCase().includes(part) ||
                        item.fileExtensions.toLowerCase().includes(part.startsWith('.') ? part : `.${part}`)) &&
                    !selectedValue.some(selectedItem => selectedItem.fileExtensions === item.fileExtensions)
                )
            );

            queryParts.forEach(part => {
                const normalizedPart = part.startsWith('.') ? part : `.${part}`;
                if (!results.some(result => result.fileExtensions.toLowerCase() === normalizedPart)) {
                    results.push({ fileExtensions: normalizedPart });
                }
            });

            setFilteredResults(results);
        } else {
            setFilteredResults([]);
        }
    };

    const handleKeyDown = (e) => {
        if (filteredResults.length > 0) {
            if (e.key === 'ArrowDown') {
                setHighlightedIndex(prevIndex => (prevIndex + 1) % filteredResults.length);
            } else if (e.key === 'ArrowUp') {
                setHighlightedIndex(prevIndex => (prevIndex - 1 + filteredResults.length) % filteredResults.length);
            } else if (e.key === 'Enter') {
                SelectValue(filteredResults[highlightedIndex]);
            }
        }
    };

    function handleBackspace() {
        setSelectedValue(prev => {
            const newArr = [...prev];
            newArr.pop();

            if (newArr.length > 0) {
                localStorage.setItem("SelectedExtension", JSON.stringify(newArr));
                localStorage.setItem("SelectedExtensionss", JSON.stringify(newArr));
            } else {
                localStorage.removeItem("SelectedExtension");
                localStorage.removeItem("SelectedExtensionss");
            }

            return newArr;
        });
    }

    useEffect(() => {
        setfileExtensionData(selectedValue);
    }, [selectedValue, setfileExtensionData]);

    useEffect(() => {
        if (itemToDeleteFileExtension) {
            const updatedSelected = selectedValue.filter(
                item => item?.fileExtensions !== itemToDeleteFileExtension?.fileExtensions
            );
            setSelectedValue(updatedSelected);
        }
    }, [itemToDeleteFileExtension]);

    const getIconPath = (iconPath) => {
        return iconMap[iconPath] || null;
    };

    const handleDeleteCross = (index, fileName) => {
        const updatedFileVal = selectedValue.filter((item) => item?.fileExtensions !== fileName);
        setSelectedValue(updatedFileVal);

        if (updatedFileVal.length > 0) {
            localStorage.setItem("SelectedExtension", JSON.stringify(updatedFileVal));
            localStorage.setItem("SelectedExtensionss", JSON.stringify(updatedFileVal));
        } else {
            localStorage.removeItem("SelectedExtension");
            localStorage.removeItem("SelectedExtensionss");
        }
    };

    const isAllSelected = selectedValue.some(item => item.fileExtensions === '.all');

    return (
        <div className="filterHome" onKeyDown={handleKeyDown} tabIndex="0">
            <div className="FilterContainer">
                <div className="SelectedContainer">
                    {fileExtensionData.map((item, index) => (
                        <div className="SelectedData" key={index}>
                            <img src={getIconPath(item.fileIcon)} className="SelectIcon" alt={item.fileExtensions} />
                            <h5 className="Filter-h5">{item.fileExtensions}</h5>
                            <span onClick={() => SelectValueRemove(item)} className="closebtn">
                                {/* <IoCloseSharp /> */}
                            </span>
                            <img
                                onClick={() => handleDeleteCross(index, item?.fileExtensions)}
                                src={DeleteIcon}
                                className="delete_icon"
                                alt="delete"
                            />
                        </div>
                    ))}
                    <input
                        type="search"
                        placeholder="Search Extensions"
                        value={searchQuery}
                        onChange={handleSearch}
                        onKeyDown={(e) => {
                            if (e.key === "Backspace" && searchQuery === "") {
                                handleBackspace();
                            }
                        }}
                    />
                </div>
                <div className="SearchList">
                    {filteredResults.map((item, index) => (
                        (isAllSelected && item.fileExtensions !== '.all') ? null : (
                            <button
                                onClick={() => SelectValue(item)}
                                key={index}
                                className={highlightedIndex === index ? 'highlighted' : ''}
                            >
                                <img src={getIconPath(item.fileIcon)} className="Selectfile-icon" alt="" />
                                <p>{item.fileExtensions}</p>
                                <p>{item.Name}</p>
                            </button>
                        )
                    ))}
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

export default FileExtensions;