// Use current page origin so API/handshake work when opening from 127.0.0.1, localhost, or any host
const protocol = typeof window !== "undefined" ? window.location.protocol : "http:";
const wsProtocol = protocol === "https:" ? "wss:" : "ws:";
const httpProtocol = protocol === "https:" ? "https:" : "http:";
const host = typeof window !== "undefined" ? window.location.host : "127.0.0.1:53335";
const FLASK_URL = `${httpProtocol}//${host}`;
const DOWNLOAD_URL = `${httpProtocol}//${host}/agent/download`;
const Server_URL = `${httpProtocol}//${host}`;
const WEB_SOCKET = `${wsProtocol}//${host}`;

const config = {
  API: {
    FLASK_URL,
    DOWNLOAD_URL,
    UPGRADE_URL: "https://license.apnabackup.com/",
    SIGNUP_URL: "https://license.apnabackup.com/apna-backup/signup/",
    WEB_SOCKET,
    Server_URL,
  },
};
export default config;
