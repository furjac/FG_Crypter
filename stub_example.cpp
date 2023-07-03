#include <iostream>
#include <fstream>
#include <string>
#include <cryptopp/aes.h>
#include <cryptopp/modes.h>
#include <cryptopp/filters.h>
#include <cryptopp/base64.h>

using namespace CryptoPP;

void decryptAndExecute(const std::string& encryptedFilePath, const std::string& keyStr, const std::string& ivStr) {
    byte key[32];
    byte iv[AES::BLOCKSIZE];

    // Convert hex-encoded key and iv strings to bytes
    HexDecoder decoder;
    decoder.Put((byte*)keyStr.data(), keyStr.size());
    decoder.MessageEnd();
    decoder.Get(key, sizeof(key));

    decoder.Put((byte*)ivStr.data(), ivStr.size());
    decoder.MessageEnd();
    decoder.Get(iv, sizeof(iv));

    CBC_Mode<AES>::Decryption decryption(key, sizeof(key), iv);

    // Read the encrypted file into memory
    std::ifstream inputFile(encryptedFilePath, std::ios::binary);
    std::stringstream encryptedData;
    encryptedData << inputFile.rdbuf();
    inputFile.close();

    // Decrypt the encrypted data
    std::string decryptedData;
    StringSource(encryptedData.str(), true, new StreamTransformationFilter(decryption, new StringSink(decryptedData)));

    // Execute the decrypted code
    std::cout << "Executing decrypted code..." << std::endl;
    // Your code here to execute the decrypted data as needed

    std::cout << "Decryption and execution completed successfully." << std::endl;
}

int main() {
    std::string encryptedFilePath = "encrypted_file.exe";
    std::string keyStr = "encryption key";
    std::string ivStr = "iv key";

    decryptAndExecute(encryptedFilePath, keyStr, ivStr);

    return 0;
}
