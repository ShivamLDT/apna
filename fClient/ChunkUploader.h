//#pragma once
//#include <string>
//#include <vector>
//#include <cstdint>
//
//// Simple options for uploader
//struct CUOptions {
//    size_t chunk_size = 4 * 1024 * 1024; // default 4MB
//    int retry_limit = 5;
//    int retry_backoff_base_seconds = 2;
//    bool send_tag_as_header = false; // if true, tag is sent in header; otherwise appended to payload
//    // Additional headers you want to always include
//    std::vector<std::pair<std::string, std::string>> extra_headers;
//};
//
//class ChunkUploader {
//public:
//    // serverHost: e.g. "server.com"
//    // port: integer port, e.g. 80 or 443 (if https you must modify WinHTTP flags; sample uses plain HTTP)
//    // uploadPath: e.g. "/upload"
//    // rawKey: 32 bytes AES-256 key (caller is responsible for key management)
//    ChunkUploader(const std::string& serverHost,
//        uint16_t port,
//        const std::string& uploadPath,
//        const std::vector<uint8_t>& rawKey,
//        const CUOptions& opts = CUOptions());
//
//    ~ChunkUploader();
//
//    // Upload file in chunks. The function streams, compresses each chunk with ZSTD,
//    // encrypts with AES-256-GCM, then POSTs the chunk with metadata headers encoded like Python.
//    // returns true if entire file succeeded; false if failed.
//    bool uploadFile(const std::string& localFilePath);
//
//private:
//    // pimpl-like private methods (not exposed)
//    struct Impl;
//    Impl* impl_;
//};
//
//// --- C API wrapper for easier plugin / dynamic language use ---
//extern "C" {
//    typedef void* CU_HANDLE;
//    CU_HANDLE CU_CreateUploader(const char* serverHost, uint16_t port, const char* uploadPath,
//        const uint8_t* rawKey32, size_t keyLen, const CUOptions* opts);
//    void CU_DestroyUploader(CU_HANDLE h);
//    int CU_UploadFile(CU_HANDLE h, const char* localFilePath); // returns 0 success, nonzero failure
//}
