import React, { useState, useEffect, useContext } from "react";
import "./FileExtensions.css";
// import { IoCloseSharp } from "react-icons/io5";
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

const FilexExten = ({ setFileNameSend }) => {
    const [data, setData] = useState([]);
    const [searchQuery, setSearchQuery] = useState(".");
    const [filteredResults, setFilteredResults] = useState([]);
    const [selectedValue, setSelectedValue] = useState([]);
    const [highlightedIndex, setHighlightedIndex] = useState(-1);
};

export default FilexExten;