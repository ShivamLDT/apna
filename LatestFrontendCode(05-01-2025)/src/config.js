const FLASK_URL = "http://192.168.2.5:53335";
const config = {
  API: {
    FLASK_URL,
    DOWNLOAD_URL: "http://192.168.2.5:53335/agent/download",
    UPGRADE_URL: "https://license.apnabackup.com/",
    SIGNUP_URL: "https://license.apnabackup.com/apna-backup/signup/",
    WEB_SOCKET: "http://192.168.2.5:53335",
    Server_URL: "http://192.168.2.5:53335"
  },
};
export default config;


// const protocol = window.location.protocol;
// const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
// const httpProtocol = protocol === 'https:' ? 'https:' : 'http:';

// const FLASK_URL = `${httpProtocol}//${window.location.host}`;
// const DOWNLOAD_URL = `${httpProtocol}//${window.location.host}/agent/download`;
// const Server_URL = `${httpProtocol}//${window.location.host}`;
// const WEB_SOCKET = `${wsProtocol}//${window.location.host}`;
// const config = {
//   API: {
//     FLASK_URL,
//     DOWNLOAD_URL,
//     UPGRADE_URL: "https://license.apnabackup.com/",
//     SIGNUP_URL: "https://license.apnabackup.com/apna-backup/signup/",
//     WEB_SOCKET,
//     Server_URL
//   },
// };
// export default config;