#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

/**
 * Reads a file into a dynamically-allocated buffer, which the caller must free.
 * This corresponds to `declare i8* @read_file(i8*)` in the LLVM IR.
 */
char* read_file(char* filename) {
    FILE* fp = fopen(filename, "rb");
    if (!fp) {
        return NULL; // or return an error sentinel
    }

    // Seek to end of file to get size
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    // Allocate buffer (size + 1 for null terminator)
    char* buffer = (char*)malloc(size + 1);
    if (!buffer) {
        fclose(fp);
        return NULL;
    }

    // Read file
    fread(buffer, 1, size, fp);
    buffer[size] = '\0'; // null-terminate
    fclose(fp);

    return buffer;
}

/**
 * Writes a string `content` to `filename`.
 * This corresponds to `declare i1 @write_file(i8*, i8*)` in the LLVM IR.
 */
bool write_file(char* filename, char* content) {
    FILE* fp = fopen(filename, "wb");
    if (!fp) {
        return false;
    }

    size_t len = strlen(content);
    size_t written = fwrite(content, 1, len, fp);
    fclose(fp);

    return (written == len);
}

/**
 * Mock HTTP GET function for demonstration.
 * In a real project, you'd replace this with an actual HTTP request library (like libcurl).
 * Corresponds to `declare i8* @http_get(i8*)` in the IR.
 */
char* http_get(char* url) {
    // For demonstration: just return a static JSON string or something similar
    // In real usage: perform an actual HTTP GET with a library, store the response
    const char* mock_response = "{\"status\": \"ok\", \"data\": \"This is a mock GET response.\"}";
    char* result = strdup(mock_response);
    return result;
}

/**
 * Mock HTTP POST function for demonstration.
 * In real usage, you might use libcurl or another library. 
 * Corresponds to `declare i8* @http_post(i8*, i8*)`.
 */
char* http_post(char* url, char* data) {
    // For demonstration: just echo back the data in a JSON
    // In real usage: perform actual POST with data
    const char* mock_prefix = "{\"status\": \"ok\", \"url\": \"";
    const char* mock_mid = "\", \"postedData\": \"";
    const char* mock_suffix = "\"}";
    size_t total_len = strlen(mock_prefix) + strlen(url) +
                       strlen(mock_mid) + strlen(data) +
                       strlen(mock_suffix) + 1;

    char* result = (char*)malloc(total_len);
    if (!result) {
        return NULL;
    }
    sprintf(result, "%s%s%s%s%s", mock_prefix, url, mock_mid, data, mock_suffix);
    return result;
}

/**
 * Returns the current timestamp (seconds since epoch).
 * Corresponds to `declare i64 @current_timestamp()`.
 */
long current_timestamp() {
    return (long)time(NULL);
}

/**
 * Formats a timestamp with a given format string. 
 * The IR calls it as `declare i8* @format_date(i64, i8*)`.
 * This function returns a newly allocated string which the caller must free.
 */
char* format_date(long timestamp, char* format) {
    time_t t = (time_t)timestamp;
    struct tm* info = localtime(&t);

    // Create a buffer to hold the formatted date
    char buffer[256];
    strftime(buffer, sizeof(buffer), format, info);

    return strdup(buffer); // dynamically allocate and return
}
