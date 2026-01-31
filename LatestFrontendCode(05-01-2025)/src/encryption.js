import axios from 'axios';
import CryptoJS from 'crypto-js';
import forge from 'node-forge';
import config from "./config";

// AES decryption with secret key
const randomChar = () => {
  const isUpperCase = Math.random() < 0.5;
  const charCode = isUpperCase
    ? 65 + Math.floor(Math.random() * 26)
    : 97 + Math.floor(Math.random() * 26);
  return String.fromCharCode(charCode);
};


export const decryptAES = (encryptedData) => {
  try {
    // Validate input
    if (!encryptedData || typeof encryptedData !== 'string') {
      throw new Error('Invalid encrypted data format');
    }

    const SECRET_KEY = CryptoJS.enc.Utf8.parse('your-very-secure-secret-key'.padEnd(32).slice(0, 32));

    // Safely parse base64
    let encrypted;
    try {
      encrypted = CryptoJS.enc.Base64.parse(encryptedData);
      if (encrypted.sigBytes < 16) { // Must have at least IV size
        throw new Error('Invalid data length');
      }
    } catch (err) {
      throw new Error('Invalid base64 data');
    }

    const iv = encrypted.clone();
    iv.sigBytes = 16;
    iv.clamp();

    const ciphertext = encrypted.clone();
    ciphertext.words.splice(0, 4);
    ciphertext.sigBytes -= 16;

    // Perform decryption with exception handling
    let decrypted;
    try {
      decrypted = CryptoJS.AES.decrypt(
        { ciphertext },
        SECRET_KEY,
        {
          iv,
          mode: CryptoJS.mode.CBC,
          padding: CryptoJS.pad.Pkcs7
        }
      );
    } catch (err) {
      throw new Error('Decryption failed');
    }

    // Safely parse JSON result
    try {
      const decryptedStr = decrypted.toString(CryptoJS.enc.Utf8);
      if (!decryptedStr) {
        throw new Error('Decryption produced empty result');
      }
      return JSON.parse(decryptedStr);
    } catch (err) {
      throw new Error('Invalid decryption result format');
    }
  } catch (error) {
    // Log for debugging but don't expose details to user
    console.error('AES decryption error:', error);
    // Return a standardized error without specific details
    throw new Error('Decryption failed');
  }
};

// Fetch a new public key from backend
export const fetchNewPublicKey = async () => {
  try {
    // Add timeout to prevent hanging requests
    const response = await axios.get(`${config.API.FLASK_URL}/key`, {
      timeout: 10000,
      headers: {
        'Accept': 'application/json',
        'X-Internal-Call': 'true'
      }
    });

    if (!response || !response.data) {
      throw new Error('Invalid server response');
    }

    const remove = response.data;
    const str = remove.substring(1);

    return decryptAES(str);
  } catch (error) {
    // Don't leak specific error details to console in production
    console.error('Failed to fetch public key:', error.message);
    throw new Error('Could not retrieve encryption key');
  }
};

// Encrypt with Forge (Hybrid RSA + AES)
export const encryptWithForge = async (data) => {
  try {
    // Validate input
    if (data === undefined || data === null) {
      throw new Error('Invalid input data');
    }


    const keyData = await fetchNewPublicKey();
    if (!keyData || !keyData.key_id || !keyData.public_key) {
      throw new Error('Invalid key data received');
    }

    const keyId = keyData.key_id;

    // Validate PEM format before processing
    let publicKey;
    try {
      publicKey = forge.pki.publicKeyFromPem(keyData.public_key);
    } catch (err) {
      throw new Error('Invalid public key format');
    }

    // Generate secure random bytes for encryption
    const aesKey = forge.random.getBytesSync(32);
    const iv = forge.random.getBytesSync(16);
    const nonce = forge.util.bytesToHex(forge.random.getBytesSync(16));

    const cipher = forge.cipher.createCipher('AES-CBC', aesKey);
    cipher.start({ iv });

    const protectedData = {
      data,
      timestamp: Math.floor(Date.now() / 1000),
      nonce
    };

    // Add data to cipher
    try {
      cipher.update(forge.util.createBuffer(JSON.stringify(protectedData), 'utf8'));
      if (!cipher.finish()) {
        throw new Error('Cipher finalization failed');
      }
    } catch (err) {
      throw new Error('Data encryption failed');
    }

    const encryptedData = cipher.output.getBytes();

    // Encrypt AES key with RSA
    let encryptedKey;
    try {
      encryptedKey = publicKey.encrypt(aesKey, 'RSA-OAEP', {
        md: forge.md.sha256.create(),
        mgf1: { md: forge.md.sha256.create() }
      });
    } catch (err) {
      throw new Error('Key encryption failed');
    }

    const result = {
      algorithm: 'ENC-RYP-TION',
      keyEncryption: 'ENC-RYP-TION256',
      iv: forge.util.encode64(iv),
      encryptedKey: forge.util.encode64(encryptedKey),
      encryptedData: forge.util.encode64(encryptedData),
      keyId
    };

    // Ensure result is properly structured before encoding
    try {
      const jsonString = JSON.stringify(result);
      const strdata = randomChar()+forge.util.encode64(jsonString);
      return strdata
    } catch (err) {
      throw new Error('Result serialization failed');
    }
  } catch (err) {
    // Log error but don't expose internal details
    console.error("Encryption failed:", err.message);
    throw new Error('Encryption failed');
  }
};

// Decrypt server response
export async function decryptServerResponse(response1) {
  try {
    const remove = response1;
    const response = remove.substring(1);

    // Input validation
    if (!response || typeof response !== 'string') {
      throw new Error('Invalid response format');
    }

    // Safely decode base64
    let jsonString;
    try {
      jsonString = atob(response);
    } catch (err) {
      throw new Error('Invalid base64 encoding');
    }

    // Safely parse JSON
    let encryptedResponse;
    try {
      encryptedResponse = JSON.parse(jsonString);
    } catch (err) {
      throw new Error('Invalid JSON format');
    }

    // Validate required fields
    const { encrypted_data, encryption_method, key_id, timestamp } = encryptedResponse;
    if (!encrypted_data || !encryption_method || !key_id || !timestamp) {
      throw new Error('Missing required encryption parameters');
    }

    // Validate timestamp is a number and check for expiration
    const parsedTimestamp = parseInt(timestamp, 10);
    if (isNaN(parsedTimestamp)) {
      throw new Error('Invalid timestamp format');
    }

    const currentTime = Math.floor(Date.now() / 1000);
    if (currentTime - parsedTimestamp > 300) {
      throw new Error('Response expired');
    }

    // Fetch private key with timeout
    let privateKeyResponse;
    try {
      privateKeyResponse = await axios.get(`${config.API.FLASK_URL}/keys/${key_id}`, {
        timeout: 10000,
        headers: {
          'Accept': 'application/json',
          'X-Internal-Call': 'true'
        }
      });

      if (!privateKeyResponse || !privateKeyResponse.data) {
        throw new Error('Invalid key response from server');
      }
    } catch (err) {
      // Don't reveal if key exists or not
      throw new Error('Failed to retrieve decryption key');
    }

    // Decrypt the key data
    let keyData;
    try {
      const remove = privateKeyResponse.data;
      const str = remove.substring(1);
      keyData = decryptAES(str);
      if (!keyData || !keyData.private_key_pem) {
        throw new Error('Invalid key data format');
      }
    } catch (err) {
      throw new Error('Failed to process decryption key');
    }

    const private_key_pem = keyData.private_key_pem;

    // Route to appropriate decryption method
    if (encryption_method === 'rsa') {
      return await decryptRSA(encrypted_data, private_key_pem);
    } else if (encryption_method === 'aes-gcm') {
      return await decryptAESGCM(encryptedResponse, private_key_pem);
    } else {
      throw new Error('Unsupported encryption method');
    }
  } catch (error) {
    // Log error but standardize the error message to avoid information leakage
    console.error('Decryption failed:', error.message);

    // Use standardized error messages
    const allowedErrorMessages = [
      'Response expired',
      'Unsupported encryption method'
    ];

    const errorMessage = allowedErrorMessages.includes(error.message)
      ? error.message
      : 'Decryption failed';

    throw new Error(errorMessage);
  }
}

// RSA decryption
export async function decryptRSA(encrypted_data, privatePem) {
  try {
    // Input validation
    if (!encrypted_data || typeof encrypted_data !== 'string') {
      throw new Error('Invalid encrypted data');
    }

    if (!privatePem || typeof privatePem !== 'string') {
      throw new Error('Invalid private key');
    }

    // Safely parse private key
    let privateKey;
    try {
      privateKey = forge.pki.privateKeyFromPem(privatePem);
    } catch (err) {
      throw new Error('Invalid private key format');
    }

    // Safely decode base64
    let encryptedBytes;
    try {
      encryptedBytes = forge.util.decode64(encrypted_data);
    } catch (err) {
      throw new Error('Invalid base64 data');
    }

    // Try RSA-OAEP first, then fallback to PKCS1v1.5 with error handling
    let decryptedBytes;
    try {
      decryptedBytes = privateKey.decrypt(encryptedBytes, 'RSA-OAEP', {
        md: forge.md.sha256.create()
      });
    } catch (err) {
      // Try fallback decryption method
      try {
        decryptedBytes = privateKey.decrypt(encryptedBytes, 'RSAES-PKCS1-V1_5');
      } catch (fallbackErr) {
        throw new Error('RSA decryption failed');
      }
    }

    // Safely parse JSON result
    try {
      const parsedData = JSON.parse(decryptedBytes);
      if (!parsedData || !parsedData.data) {
        throw new Error('Invalid decrypted data format');
      }
      return parsedData.data;
    } catch (err) {
      throw new Error('Invalid decryption result format');
    }
  } catch (error) {
    // Log error but don't expose specific details
    console.error('RSA decryption error:', error.message);
    throw new Error('Decryption failed');
  }
}

// AES-GCM decryption
export async function decryptAESGCM(encryptedResponse, privatePem) {
  try {
    // Validate required fields
    const { encrypted_data, encrypted_key, iv, tag } = encryptedResponse;
    if (!encrypted_data || !encrypted_key || !iv || !tag) {
      throw new Error('Missing required encryption parameters');
    }

    // AAD is optional
    const aad = encryptedResponse.aad || '';

    // Safely parse private key
    let privateKey;
    try {
      privateKey = forge.pki.privateKeyFromPem(privatePem);
    } catch (err) {
      throw new Error('Invalid private key format');
    }

    // Decrypt the AES key with RSA
    let aesKeyBytes;
    try {
      aesKeyBytes = privateKey.decrypt(forge.util.decode64(encrypted_key), 'RSA-OAEP', {
        md: forge.md.sha256.create()
      });
    } catch (err) {
      throw new Error('Key decryption failed');
    }

    // Set up AES-GCM decipher
    const decipher = forge.cipher.createDecipher('AES-GCM', aesKeyBytes);

    // Safely decode components
    let decodedIv, decodedTag, decodedAad, decodedData;
    try {
      decodedIv = forge.util.decode64(iv);
      decodedTag = forge.util.decode64(tag);
      decodedAad = aad ? forge.util.decode64(aad) : '';
      decodedData = forge.util.decode64(encrypted_data);
    } catch (err) {
      throw new Error('Invalid encryption components');
    }

    // Start decryption with parameters
    try {
      decipher.start({
        iv: decodedIv,
        additionalData: decodedAad,
        tag: decodedTag
      });
      decipher.update(forge.util.createBuffer(decodedData));
    } catch (err) {
      throw new Error('Decipher initialization failed');
    }

    // Finalize decryption
    if (!decipher.finish()) {
      throw new Error('Authentication failed');
    }

    // Safely parse JSON result
    try {
      const decryptedStr = decipher.output.toString();
      if (!decryptedStr) {
        throw new Error('Decryption produced empty result');
      }

      const parsedData = JSON.parse(decryptedStr);
      if (!parsedData || !parsedData.data) {
        throw new Error('Invalid decrypted data format');
      }

      return parsedData.data;
    } catch (err) {
      throw new Error('Invalid decryption result format');
    }
  } catch (error) {
    // Log error but don't expose specific details
    console.error('AES-GCM decryption error:', error.message);

    // Use standardized error messages
    const allowedErrorMessages = [
      'Authentication failed',
      'Missing required encryption parameters'
    ];

    const errorMessage = allowedErrorMessages.includes(error.message)
      ? error.message
      : 'Decryption failed';

    throw new Error(errorMessage);
  }
}
