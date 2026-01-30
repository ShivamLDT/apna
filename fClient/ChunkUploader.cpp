//#include <windows.h>
//#include <bcrypt.h>
//#include <wincrypt.h>
//#include <winhttp.h>
//#include <cstdio>
//#include <string>
//#include <vector>
//#include <thread>
//#include <fstream>
//#include <iostream>
//#include <sstream>
//
//#pragma comment(lib, "bcrypt.lib")
//#pragma comment(lib, "winhttp.lib")
//
//// Utility: base64 encode
//std::string base64_encode(const std::vector<uint8_t>& data) {
//    DWORD len = 0;
//    if (!CryptBinaryToStringA(data.data(), (DWORD)data.size(), CRYPT_STRING_BASE64 | CRYPT_STRING_NOCRLF, nullptr, &len)) {
//        return {};
//    }
//    std::string out(len, '\0');
//    if (!CryptBinaryToStringA(data.data(), (DWORD)data.size(), CRYPT_STRING_BASE64 | CRYPT_STRING_NOCRLF, &out[0], &len)) {
//        return {};
//    }
//    out.resize(len - 1); // remove trailing null
//    return out;
//}
//
//// Utility: SHA256
//std::vector<uint8_t> sha256(const std::vector<uint8_t>& data) {
//    BCRYPT_ALG_HANDLE hAlg = nullptr;
//    BCRYPT_HASH_HANDLE hHash = nullptr;
//    DWORD hashObjectLen = 0, dataLen = 0;
//
//    if (BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_SHA256_ALGORITHM, nullptr, 0) < 0) return {};
//    if (BCryptGetProperty(hAlg, BCRYPT_OBJECT_LENGTH, (PUCHAR)&hashObjectLen, sizeof(DWORD), &dataLen, 0) < 0) return {};
//
//    std::vector<uint8_t> hashObj(hashObjectLen);
//    if (BCryptCreateHash(hAlg, &hHash, hashObj.data(), hashObjectLen, nullptr, 0, 0) < 0) return {};
//
//    if (BCryptHashData(hHash, (PUCHAR)data.data(), (ULONG)data.size(), 0) < 0) return {};
//    DWORD hashLen = 32;
//    std::vector<uint8_t> hash(hashLen);
//    if (BCryptFinishHash(hHash, hash.data(), hashLen, 0) < 0) return {};
//
//    if (hHash) BCryptDestroyHash(hHash);
//    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
//    return hash;
//}
//
//// Uploader class
//class ChunkUploader {
//public:
//    ChunkUploader(const std::wstring& server, INTERNET_PORT port)
//        : server_(server), port_(port) {
//    }
//
//    bool uploadFile1(const std::wstring& path) {
//        std::ifstream file(path, std::ios::binary);
//        if (!file.is_open()) {
//            std::wcerr << L"[!] Failed to open file: " << path << std::endl;
//            return false;
//        }
//
//        const size_t CHUNK_SIZE = 64*1024 * 1024; // 1MB
//        std::vector<uint8_t> buffer(CHUNK_SIZE);
//        size_t chunkIndex = 0;
//
//        while (file) {
//            file.read(reinterpret_cast<char*>(buffer.data()), buffer.size());
//            std::streamsize bytesRead = file.gcount();
//            if (bytesRead <= 0) break;
//
//            std::vector<uint8_t> chunk(buffer.begin(), buffer.begin() + bytesRead);
//            auto hash = sha256(chunk);
//            std::string hash64 = base64_encode(hash);
//
//            std::wcout << L"[*] Uploading chunk " << chunkIndex
//                << L" (" << bytesRead << L" bytes, SHA256=" << hash64.c_str() << L")"
//                << std::endl;
//
//            if (!sendChunk(chunk, hash64, chunkIndex)) {
//                std::wcerr << L"[!] Failed to upload chunk " << chunkIndex << std::endl;
//                return false;
//            }
//
//            ++chunkIndex;
//        }
//
//        std::wcout << L"[+] File upload complete!" << std::endl;
//        return true;
//    }
//    bool ChunkUploader::uploadFile(const std::wstring& path);
//private:
//    //bool sendChunk(const std::vector<uint8_t>& chunk, const std::string& hash64, size_t index) {
//    bool sendChunk(const std::vector<uint8_t>& chunk, const std::string& hash64, size_t index) {
//        HINTERNET hSession = WinHttpOpen(L"ChunkUploader/1.0",
//            WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
//            WINHTTP_NO_PROXY_NAME,
//            WINHTTP_NO_PROXY_BYPASS, 0);
//        if (!hSession) return false;
//
//        HINTERNET hConnect = WinHttpConnect(hSession, server_.c_str(), port_, 0);
//        if (!hConnect) { WinHttpCloseHandle(hSession); return false; }
//
//        HINTERNET hRequest = WinHttpOpenRequest(hConnect, L"POST", L"/upload",
//            nullptr, WINHTTP_NO_REFERER,
//            WINHTTP_DEFAULT_ACCEPT_TYPES,
//            0);
//        if (!hRequest) {
//            WinHttpCloseHandle(hConnect);
//            WinHttpCloseHandle(hSession);
//            return false;
//        }
//
//        std::wstringstream headers;
//        headers << L"X-Chunk-Index: " << index << L"\r\n";
//        headers << L"X-Chunk-Hash: " << std::wstring(hash64.begin(), hash64.end()) << L"\r\n";
//
//        BOOL bResults = WinHttpSendRequest(hRequest,
//            headers.str().c_str(),
//            (DWORD)-1L,
//            (LPVOID)chunk.data(),
//            (DWORD)chunk.size(),
//            (DWORD)chunk.size(),
//            0);
//
//        if (bResults) bResults = WinHttpReceiveResponse(hRequest, nullptr);
//
//        if (!bResults) {
//            std::wcerr << L"[!] WinHTTP error " << GetLastError() << std::endl;
//        }
//
//        WinHttpCloseHandle(hRequest);
//        WinHttpCloseHandle(hConnect);
//        WinHttpCloseHandle(hSession);
//
//        return bResults == TRUE;
//    }
//
//    std::wstring server_;
//    INTERNET_PORT port_;
//};
//bool ChunkUploader::uploadFile(const std::wstring& path) {
//    std::ifstream file(path, std::ios::binary);
//    if (!file.is_open()) {
//        std::wcerr << L"[!] Failed to open file: " << path << std::endl;
//        return false;
//    }
//
//    const size_t CHUNK_SIZE = 64 * 1024 * 1024; // 1MB
//    std::vector<uint8_t> buffer(CHUNK_SIZE);
//    size_t chunkIndex = 0;
//    std::vector<std::thread> threads;
//
//    while (file) {
//        file.read(reinterpret_cast<char*>(buffer.data()), buffer.size());
//        std::streamsize bytesRead = file.gcount();
//        if (bytesRead <= 0) break;
//
//        std::vector<uint8_t> chunk(buffer.begin(), buffer.begin() + bytesRead);
//        auto hash = sha256(chunk);
//        std::string hash64 = base64_encode(hash);
//
//        // Create a new thread to send the chunk
//        threads.emplace_back([this, chunk = std::move(chunk), hash64 = std::move(hash64), chunkIndex]() mutable {
//            std::wcout << L"[*] Uploading chunk " << chunkIndex
//                << L" (" << chunk.size() << L" bytes, SHA256=" << hash64.c_str() << L")"
//                << std::endl;
//            if (!this->sendChunk(chunk, hash64, chunkIndex)) {
//                std::wcerr << L"[!] Failed to upload chunk " << chunkIndex << std::endl;
//            }
//            });
//
//        // Optional: limit the number of concurrent threads
//        if (threads.size() >= std::thread::hardware_concurrency() * 2) {
//            for (auto& t : threads) {
//                if (t.joinable()) {
//                    t.join();
//                }
//            }
//            threads.clear();
//        }
//
//        ++chunkIndex;
//    }
//
//    // Wait for all threads to finish
//    for (auto& t : threads) {
//        if (t.joinable()) {
//            t.join();
//        }
//    }
//
//    std::wcout << L"[+] File upload complete!" << std::endl;
//    return true;
//}
//// ---------------------- MAIN -------------------------
//int wmain(int argc, wchar_t* argv[]) {
//    if (argc < 4) {
//        std::wcerr << L"Usage: ChunkUploader.exe <server> <port> <file>" << std::endl;
//        return 1;
//    }
//
//    std::wstring server = argv[1];
//    INTERNET_PORT port = (INTERNET_PORT)_wtoi(argv[2]);
//    std::wstring file = argv[3];
//
//    std::wcout << L"[+] Starting upload to " << server << L":" << port
//        << L" for file " << file << std::endl;
//
//    ChunkUploader uploader(server, port);
//    if (!uploader.uploadFile(file)) {
//        std::wcerr << L"[!] Upload failed" << std::endl;
//        return 1;
//    }
//
//    return 0;
//}
//
//
#include <windows.h>
#include <bcrypt.h>
#include <wincrypt.h>
#include <winhttp.h>
#include <cstdio>
#include <string>
#include <vector>
#include <thread>
#include <fstream>
#include <iostream>
#include <sstream>

#pragma comment(lib, "bcrypt.lib")
#pragma comment(lib, "winhttp.lib")

// Utility: base64 encode
std::string base64_encode(const std::vector<uint8_t>& data) {
    DWORD len = 0;
    if (!CryptBinaryToStringA(data.data(), (DWORD)data.size(), CRYPT_STRING_BASE64 | CRYPT_STRING_NOCRLF, nullptr, &len)) {
        return {};
    }
    std::string out(len, '\0');
    if (!CryptBinaryToStringA(data.data(), (DWORD)data.size(), CRYPT_STRING_BASE64 | CRYPT_STRING_NOCRLF, &out[0], &len)) {
        return {};
    }
    out.resize(len - 1); // remove trailing null
    return out;
}

// Utility: SHA256
std::vector<uint8_t> sha256(const std::vector<uint8_t>& data) {
    BCRYPT_ALG_HANDLE hAlg = nullptr;
    BCRYPT_HASH_HANDLE hHash = nullptr;
    DWORD hashObjectLen = 0, dataLen = 0;

    if (BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_SHA256_ALGORITHM, nullptr, 0) < 0) return {};
    if (BCryptGetProperty(hAlg, BCRYPT_OBJECT_LENGTH, (PUCHAR)&hashObjectLen, sizeof(DWORD), &dataLen, 0) < 0) return {};

    std::vector<uint8_t> hashObj(hashObjectLen);
    if (BCryptCreateHash(hAlg, &hHash, hashObj.data(), hashObjectLen, nullptr, 0, 0) < 0) return {};

    if (BCryptHashData(hHash, (PUCHAR)data.data(), (ULONG)data.size(), 0) < 0) return {};
    DWORD hashLen = 32;
    std::vector<uint8_t> hash(hashLen);
    if (BCryptFinishHash(hHash, hash.data(), hashLen, 0) < 0) return {};

    if (hHash) BCryptDestroyHash(hHash);
    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    return hash;
}

// Uploader class
class ChunkUploader {
public:
    ChunkUploader(const std::wstring& server, INTERNET_PORT port)
        : server_(server), port_(port) {
    }

    bool uploadFile(const std::wstring& path) {
        std::ifstream file(path, std::ios::binary);
        if (!file.is_open()) {
            std::wcerr << L"[!] Failed to open file: " << path << std::endl;
            return false;
        }

        const size_t CHUNK_SIZE = 1 * 1024 * 1024; // 64 KB
        std::vector<uint8_t> buffer(CHUNK_SIZE);
        size_t chunkIndex = 0;
        std::vector<std::thread> threads;

        while (file) {
            file.read(reinterpret_cast<char*>(buffer.data()), buffer.size());
            std::streamsize bytesRead = file.gcount();
            if (bytesRead <= 0) break;

            std::vector<uint8_t> chunk(buffer.begin(), buffer.begin() + bytesRead);

            // Capture a copy of the chunkIndex and move the other data to the thread
            threads.emplace_back([this, chunk = std::move(chunk), chunkIndex]() mutable {
                auto hash = sha256(chunk);
                std::string hash64 = base64_encode(hash);

                std::wcout << L"[*] Uploading chunk " << chunkIndex
                    << L" (" << chunk.size() << L" bytes, SHA256=" << hash64.c_str() << L")"
                    << std::endl;

                if (!sendChunk(chunk, hash64, chunkIndex)) {
                    std::wcerr << L"[!] Failed to upload chunk " << chunkIndex << std::endl;
                }
                });

            // Limit the number of concurrent threads to avoid overwhelming the system
            if (threads.size() >= std::thread::hardware_concurrency()) {
                for (auto& t : threads) {
                    if (t.joinable()) {
                        t.join();
                    }
                }
                threads.clear();
            }

            ++chunkIndex;
        }

        // Wait for all remaining threads to finish
        for (auto& t : threads) {
            if (t.joinable()) {
                t.join();
            }
        }

        std::wcout << L"[+] File upload complete!" << std::endl;
        return true;
    }

private:
    bool sendChunk(const std::vector<uint8_t>& chunk, const std::string& hash64, size_t index) {
        HINTERNET hSession = WinHttpOpen(L"ChunkUploader/1.0",
            WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
            WINHTTP_NO_PROXY_NAME,
            WINHTTP_NO_PROXY_BYPASS, 0);
        if (!hSession) return false;

        HINTERNET hConnect = WinHttpConnect(hSession, server_.c_str(), port_, 0);
        if (!hConnect) { WinHttpCloseHandle(hSession); return false; }

        HINTERNET hRequest = WinHttpOpenRequest(hConnect, L"POST", L"/upload",
            nullptr, WINHTTP_NO_REFERER,
            WINHTTP_DEFAULT_ACCEPT_TYPES,
            0);
        if (!hRequest) {
            WinHttpCloseHandle(hConnect);
            WinHttpCloseHandle(hSession);
            return false;
        }

        std::wstringstream headers;
        headers << L"X-Chunk-Index: " << static_cast<unsigned long long>(index) << L"\r\n";
        headers << L"X-Chunk-Hash: " << std::wstring(hash64.begin(), hash64.end()) << L"\r\n";
        std::wstring headers_str = headers.str();

        BOOL bResults = WinHttpSendRequest(hRequest,
            headers_str.c_str(),
            static_cast<DWORD>(headers_str.length()),
            (LPVOID)chunk.data(),
            static_cast<DWORD>(chunk.size()),
            static_cast<DWORD>(chunk.size()),
            0);

        if (bResults) bResults = WinHttpReceiveResponse(hRequest, nullptr);

        if (!bResults) {
            std::wcerr << L"[!] WinHTTP error " << GetLastError() << std::endl;
        }

        WinHttpCloseHandle(hRequest);
        WinHttpCloseHandle(hConnect);
        WinHttpCloseHandle(hSession);

        return bResults == TRUE;
    }

    std::wstring server_;
    INTERNET_PORT port_;
};

// ---------------------- MAIN -------------------------
int wmain(int argc, wchar_t* argv[]) {
    if (argc < 4) {
        std::wcerr << L"Usage: ChunkUploader.exe <server> <port> <file>" << std::endl;
        return 1;
    }

    std::wstring server = argv[1];
    INTERNET_PORT port = (INTERNET_PORT)_wtoi(argv[2]);
    std::wstring file = argv[3];

    std::wcout << L"[+] Starting upload to " << server << L":" << port
        << L" for file " << file << std::endl;

    ChunkUploader uploader(server, port);
    if (!uploader.uploadFile(file)) {
        std::wcerr << L"[!] Upload failed" << std::endl;
        return 1;
    }

    return 0;
}