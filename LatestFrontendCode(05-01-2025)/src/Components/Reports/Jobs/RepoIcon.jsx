import React from "react";
import nasLogo from "../../../Image/nas.png";
import localLogo from "../../../Image/localdisk.png";
import gdriveLogo from "../../../Image/googledrive.png";
import s3Logo from "../../../Image/aws1.png";
import azureLogo from "../../../Image/azure.png";
import dropboxLogo from "../../../Image/dropbox.png";
import oneDrive from "../../../assets/OneDrive.png";

const repoMap = {
    LOCALSTORAGE: localLogo,
    LAN: localLogo,
    GDRIVE: gdriveLogo,
    GOOGLEDRIVE: gdriveLogo,
    UNC: nasLogo,
    AZURE: azureLogo,
    AWSS3: s3Logo,
    DROPBOX: dropboxLogo,
    ONEDRIVE: oneDrive,
};

const RepoIcon = ({ repo }) => {
    const logo = repoMap[repo];
    if (!logo) return repo;

    return (
        <div className="relative group inline-flex ">
            <img
                src={logo}
                alt={repo}
                className="cursor-pointer transition-transform duration-200 group-hover:scale-105"
                style={{ width: "20px", height: "20px", objectFit: "contain" }}
            />

            <div
                className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2
                   opacity-0 group-hover:opacity-100 transition-opacity duration-200
                   bg-gray-800 text-white text-xs rounded-md px-2 py-1 z-50
                   whitespace-nowrap shadow-md pointer-events-none"
            >
                {repo === "LAN" || repo === "LOCALSTORAGE" ? "On-Premise" : repo === "UNC" ? "NAS/UNC" : repo}
                {/* <div
                    className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 
                     bg-gray-800 rotate-45"
                ></div> */}
            </div>
        </div>
    );
};

export default RepoIcon;
