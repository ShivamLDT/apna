import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';

// import { encryptWithForge, decryptServerResponse } from './encryption';
// import CryptoJS from 'crypto-js';

// function decryptData(encryptedData) {
//   if (!encryptedData) return "";
//   try {
//     const bytes = CryptoJS.AES.decrypt(encryptedData, "1234567890");
//     const decrypted = bytes.toString(CryptoJS.enc.Utf8);
//     return decrypted || "";
//   } catch (error) {
//     console.error("Decryption error:", error);
//     return "";
//   }
// }

// const axiosInstance = axios.create({
//   // timeout: 10000,
// });

// export default axiosInstance;


// ====================================
// ====================================



import forge from 'node-forge';
import config from './config';
// ---------------- Helpers ----------------


const showSessionExpiredAndLogout = () => {
  logout();
  toast.error("Session Expired");
};


const logout = async () => {
  const accessToken = localStorage.getItem('AccessToken');

  try {
    if (accessToken) {
      const response = await axiosInstance.post(
        `${config.API.FLASK_URL}/logout`,
        null,
        {
          headers: {
            'Content-Type': 'application/json',
            'Token': `${accessToken}`,
          },
          validateStatus: () => true,
        }
      );

      if (response.status >= 400) {
        throw new Error('Logout request failed');
      }

      // Show success toast
      toast.success("Logged out successfully!")
    }

    // Clear local storage, set isLoggedIn to false, and reload the page
    localStorage.clear();
    // window.location.reload();
  } catch (error) {
    console.error('Error during logout:', error);
    // Show error toast

    // Ensure logout even if the API call fails
    localStorage.clear();
    // window.location.reload();
    toast.error("Error during logout. Please try again.");
  }
};

const tokenRefresh = async () => {
  const refreshToken = localStorage.getItem("RefreshToken");
  try {
    const res = await axios.post(`${config.API.Server_URL}/refresh`, null, {
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    });
    const newAccessToken = res.data.access_token;
    localStorage.setItem("AccessToken", newAccessToken)
  } catch (error) {
    if (error.response?.status >= 400) {
      // Refresh token is invalid or expired
      showSessionExpiredAndLogout();
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
    }
  }
}

function u8ToStr(u8) {
  if (!u8 || u8.length === 0) return '';
  const CHUNK = 0x8000;
  let result = [];
  for (let i = 0; i < u8.length; i += CHUNK) {
    result.push(String.fromCharCode.apply(null, u8.subarray(i, i + CHUNK)));
  }
  return result.join('');
}
function normalizeKeyBytes(key) {
  if (!key) return '';
  if (typeof key === 'string') return key;
  if (key instanceof Uint8Array) {
    return forge.util.binary.raw.encode(key);
  }
  if (Array.isArray(key)) {
    return forge.util.binary.raw.encode(new Uint8Array(key));
  }
  if (key.buffer && key.byteLength != null) {
    return forge.util.binary.raw.encode(new Uint8Array(key));
  }
  if (typeof key.getBytes === 'function') {
    return key.getBytes();
  }
  return '';
}
function normalizeBytes(value) {
  if (!value) return '';
  if (typeof value === 'string') return value;
  if (value instanceof Uint8Array) {
    return forge.util.binary.raw.encode(value);
  }
  if (Array.isArray(value)) {
    return forge.util.binary.raw.encode(new Uint8Array(value));
  }
  if (value.buffer && value.byteLength != null) {
    return forge.util.binary.raw.encode(new Uint8Array(value));
  }
  if (typeof value.getBytes === 'function') {
    return value.getBytes();
  }
  return '';
}
function strToU8(str) {
  const u8 = new Uint8Array(str.length);
  for (let i = 0; i < str.length; i++) {
    u8[i] = str.charCodeAt(i);
  }
  return u8;
}
function ab2b64(buf) {
  const u8 = new Uint8Array(buf);
  const CHUNK = 0x8000;
  let result = '';
  for (let i = 0; i < u8.length; i += CHUNK) {
    const chunk = u8.subarray(i, Math.min(i + CHUNK, u8.length));
    result += String.fromCharCode.apply(null, chunk);
  }
  return btoa(result);
}
function b642ab(b64) {
  const str = atob(b64);
  const buf = new ArrayBuffer(str.length);
  const view = new Uint8Array(buf);
  for (let i = 0; i < str.length; i++) {
    view[i] = str.charCodeAt(i);
  }
  return buf;
}
function sha256(dataUint8) {
  const md = forge.md.sha256.create();
  md.update(forge.util.createBuffer(dataUint8));
  const digestBytes = md.digest().getBytes();
  return new Uint8Array(forge.util.binary.raw.decode(digestBytes));
}
// ---------------- Browser Fingerprint for Key Derivation ----------------
async function getBrowserFingerprint() {
  const components = [
    navigator.userAgent,
    navigator.language,
    new Date().getTimezoneOffset(),
    screen.width + 'x' + screen.height,
    navigator.hardwareConcurrency || 4,
    navigator.deviceMemory || 8,
  ].join('|');
  const encoder = new TextEncoder();
  const data = encoder.encode(components);
  return sha256(data);
}
function deriveKeyPBKDF2(passwordUint8, saltUint8, iterations, keyLenBytes) {
  // forge expects strings for password/salt, so convert Uint8Array to bytes string
  const passwordBytes = forge.util.binary.raw.encode(passwordUint8);
  const saltBytes = forge.util.binary.raw.encode(saltUint8);
  const derivedKeyBytes = forge.pkcs5.pbkdf2(passwordBytes, saltBytes, iterations, keyLenBytes, forge.md.sha256.create());
  return new Uint8Array(forge.util.binary.raw.decode(derivedKeyBytes));
}
// ---------------- Secure Session Storage with Encryption ----------------
async function deriveStorageKey() {
  const fingerprint = await getBrowserFingerprint();
  const salt = new TextEncoder().encode('secure-session-salt-v1');
  const derivedKey = deriveKeyPBKDF2(fingerprint, salt, 100000, 32);
  return derivedKey;
}
async function encryptSessionData(data) {
  const key = await deriveStorageKey();
  return aesEncrypt(data, key);
}
async function decryptSessionData(encryptedObj) {
  try {
    const key = await deriveStorageKey();
    return await aesDecrypt(encryptedObj, key);
  } catch (e) {
    console.warn('Failed to decrypt session data:', e);
    return null;
  }
}
// ---------------- Secure Storage in SessionStorage (per-tab) ----------------
async function saveSession(keyId, aesKey, expiresAt) {
  if (!keyId || !aesKey) return;
  const sessionData = {
    keyId: keyId,
    aesKey: Array.from(aesKey),
    expiresAt: expiresAt,
    timestamp: Date.now()
  };
  const encrypted = await encryptSessionData(sessionData);
  sessionStorage.setItem('enc_session', JSON.stringify(encrypted));
}
async function loadSession() {
  try {
    const encryptedStr = sessionStorage.getItem('enc_session');
    if (!encryptedStr) return null;
    const encrypted = JSON.parse(encryptedStr);
    const sessionData = await decryptSessionData(encrypted);
    if (!sessionData) return null;
    if (sessionData.expiresAt < Date.now()) {
      sessionStorage.removeItem('enc_session');
      return null;
    }
    return {
      keyId: sessionData.keyId,
      aesKey: new Uint8Array(sessionData.aesKey),
      expiresAt: sessionData.expiresAt
    };
  } catch (e) {
    console.warn('Failed to load session:', e);
    return null;
  }
}
function clearSession() {
  sessionStorage.removeItem('enc_session');
}
// ---------------- RSA Import and Encrypt ----------------
function importRSAPublicKey(pem) {
  return forge.pki.publicKeyFromPem(pem);
}
function encryptAESKeyWithRSA(aesKeyBytes, rsaPubKey) {
  const binaryString = u8ToStr(aesKeyBytes);
  const encrypted = rsaPubKey.encrypt(binaryString, "RSAES-PKCS1-V1_5");
  return ab2b64(strToU8(encrypted).buffer);
}
// ---------------- AES-GCM encrypt/decrypt (forge) ----------------
async function generateAESKey() {
  const key = forge.random.getBytesSync(32);
  return strToU8(key);
}
async function aesEncrypt(data, aesKey) {
  const plaintext = JSON.stringify(data);
  const ivBytes = forge.random.getBytesSync(12);
  const keyStr = normalizeKeyBytes(aesKey);
  if (![16, 24, 32].includes(keyStr.length)) {
    throw new Error('Invalid AES key length');
  }
  const cipher = forge.cipher.createCipher('AES-GCM', keyStr);
  cipher.start({ iv: ivBytes, tagLength: 128 });
  cipher.update(forge.util.createBuffer(plaintext, 'utf8'));
  const ok = cipher.finish();
  if (!ok) throw new Error('Encryption failed');
  const ciphertext = cipher.output.getBytes();
  const tag = cipher.mode.tag.getBytes();
  const combined = ciphertext + tag;
  return {
    iv: btoa(ivBytes),
    ct: btoa(combined),
  };
}
async function aesDecrypt(enc, aesKey) {
  if (!enc || !enc.iv || !enc.ct) {
    throw new Error('Invalid encrypted data structure');
  }
  const ivStr = normalizeBytes(atob(enc.iv));
  const combinedStr = normalizeBytes(atob(enc.ct));
  if (combinedStr.length < 16) {
    throw new Error('Invalid ciphertext: too short for tag');
  }
  const ciphertextStr = combinedStr.slice(0, -16);
  const tagStr = combinedStr.slice(-16);
  const keyStr = normalizeKeyBytes(aesKey);
  if (![16, 24, 32].includes(keyStr.length)) {
    throw new Error('Invalid AES key length');
  }
  const decipher = forge.cipher.createDecipher('AES-GCM', keyStr);
  decipher.start({
    iv: ivStr,
    tag: tagStr,
    tagLength: 128
  });
  decipher.update(forge.util.createBuffer(ciphertextStr, 'raw'));
  const ok = decipher.finish();
  if (!ok) {
    throw new Error('AES-GCM decryption failed');
  }
  const plain = decipher.output.toString('utf8');
  return JSON.parse(plain);
}
// ---------------- Session Management ----------------
let aesKey = null;
let keyId = null;
let sessionExpiry = null;
let handshakePromise = null;
const SESSION_LIFETIME_MS = 60 * 60 * 1000;  // 60 min (matches server SESSION_TTL_SECONDS)
function isSessionValid() {
  return aesKey && keyId && sessionExpiry && Date.now() < sessionExpiry;
}
async function performHandshake() {
  const { data } = await axios.get(`${config.API.Server_URL}/handshake`);
  const newKeyId = data.key_id;
  const rsaPubKey = importRSAPublicKey(data.pub_pem);
  const newAesKey = await generateAESKey();
  const encAES = encryptAESKeyWithRSA(newAesKey, rsaPubKey);
  try {
    await axios.post(`${config.API.Server_URL}/handshake/confirm`, {
      key_id: newKeyId,
      enc_aes_b64: encAES,
    });
  } catch (error) {
    console.error(error)
  }
  aesKey = newAesKey;
  keyId = newKeyId;
  sessionExpiry = Date.now() + SESSION_LIFETIME_MS;
  await saveSession(keyId, aesKey, sessionExpiry);
}
export async function ensureSession() {
  if (isSessionValid()) return;
  if (handshakePromise) return handshakePromise;
  handshakePromise = (async () => {
    try {
      const saved = await loadSession();
      if (saved && saved.keyId && saved.aesKey) {
        try {
          const { data } = await axios.post(
            `${config.API.Server_URL}/handshake/check-key`,
            { key_id: saved.keyId }
          );
          if (data?.ok) {
            aesKey = saved.aesKey;
            keyId = saved.keyId;
            sessionExpiry = data.ttl != null ? Date.now() + data.ttl * 1000 : saved.expiresAt;
            return;
          } else {
            clearSession();
          }
        } catch (e) {
          clearSession();
        }
      }
    } catch (e) {
      console.warn("Could not restore session:", e);
    }
    await performHandshake();
  })();
  try {
    await handshakePromise;
  } finally {
    handshakePromise = null;
  }
}
function invalidateSession() {
  aesKey = null;
  keyId = null;
  sessionExpiry = null;
  clearSession();
}
window.addEventListener('beforeunload', () => {
  if (aesKey && keyId) {
    saveSession(keyId, aesKey, sessionExpiry);
  }
});
// ---------------- Crypto axios wrapper with retry logic ----------------
async function request(method, url, data = null, config = {}) {
  const maxRetries = 1;
  let retried = 0;
  let unixTime = Date.now() / 1000;
  while (retried <= maxRetries) {
    try {
      await ensureSession();
      if (!aesKey || !keyId) {
        throw new Error('Session not established');
      }
      const token = localStorage.getItem("AccessToken");
      const newConfig = {
        ...config,
        method,
        url,
        headers: {
          "X-Key-Id": keyId,
          "Authorization": token ? `Bearer ${token}` : undefined,
          ...(config.headers || {}),
        },
        // timeout: config.timeout || 60000,
      };
      if (data) {
        const payloadWithTime = {
          ...(data || {}),
          time: unixTime,
        };
        // console.log('====================================');
        // console.log("Payload with unixTime:", payloadWithTime);
        const encBody = await aesEncrypt(payloadWithTime, aesKey);
        newConfig.data = encBody;
      }
      const resp = await axios(newConfig);
      const payload = resp?.data;
      if (payload && typeof payload === 'object' && 'iv' in payload) {
        if (!('ct' in payload) || !payload.ct) {
          console.warn('Encrypted response missing "ct", invalidating session and retrying');
          invalidateSession();
          if (retried < maxRetries) {
            retried++;
            await new Promise(resolve => setTimeout(resolve, 500 * retried));
            continue;
          }
          throw new Error('Invalid encrypted response (missing ciphertext)');
        }
        try {
          resp.data = await aesDecrypt(payload, aesKey);
        } catch (err) {
          console.error('Decryption failed, invalidating session', err);
          invalidateSession();
          if (retried < maxRetries) {
            retried++;
            await new Promise(resolve => setTimeout(resolve, 500 * retried));
            continue;
          }
          throw err;
        }
      }
      return resp;
    } catch (error) {

      const errObj = error?.response?.data || {};
      let errCode = errObj?.error || errObj?.msg || error?.response?.error || error?.code || error?.message || null;
      if (typeof errObj === "string") {
        errCode = errObj;
      }
      const retryableErrors = [
        "TokenMissing",
        "invalid_or_expired_key",
        "session_expired",
        "Bad request",
        "Invalid request format",
        "database_timeout",
        "decryption_failed",
        "AuthorizationHeaderMissing",
        "MalformedJwtException",
        "InvalidJwtFormat",
        "InvalidSignatureException",
        "TokenExpiredError",
        "JwtNotYetValid",
        "InvalidAudienceException",
        "InvalidIssuerException",
        "MissingClaimException",
        "AlgorithmMismatchException",
        "JwtTampered",
        "TokenRevoked",
        "UnsupportedJwt",
        "JwtDecryptionError",
        "user not found",
        "Token has expired",
        "InsufficientPermissions",
        "ERR_BAD_REQUEST",
        "404_NOT_FOUND",
        "Not Found",
        "404",
        "Not enough segments",
        "Bad request",
        "Invalid request format"
      ];

      if (retryableErrors.includes(errCode) && retried < maxRetries) {
        tokenRefresh();
        invalidateSession();
        retried++;
        await new Promise(res => setTimeout(res, 500 * retried));
        continue;
      }

      if (error?.code === 'ECONNABORTED' || error?.code === 'ERR_NETWORK') {
        if (retried < maxRetries) {
          invalidateSession();
          retried++;
          await new Promise(resolve => setTimeout(resolve, 1000 * retried));
          continue;
        }
      }
      throw error;
    }
  }
}
<ToastContainer position="top-right" autoClose={3000} />

const axiosInstance = {
  get: (url, config) => request("get", url, null, config),
  delete: (url, data = null, config = {}) => request("delete", url, data, config),
  head: (url, config) => request("head", url, null, config),
  options: (url, config) => request("options", url, null, config),
  post: (url, data, config) => request("post", url, data, config),
  put: (url, data, config) => request("put", url, data, config),
  patch: (url, data, config) => request("patch", url, data, config),
};
export default axiosInstance;