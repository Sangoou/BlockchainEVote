#include <iostream>
#include <string>

class Header {
	private:
		int _version, _timestamp, _difficulty;
		std::string _merkleRoot, _prevPrivateKey, _nextPublicKey;
		
	public:
		Header(){
			_version = _timestamp = _difficulty = 0;
			_merkleRoot = "root";
			_prevPrivateKey = "priv";
			_nextPublicKey = "pub";
		}
		friend std::ostream& operator<<(std::ostream& os, const Header& header);
};

std::ostream& operator<<(std::ostream& os, const Header& header){
	os << "Version:\t" << header._version << std::endl;
	os << "Time:\t\t" << header._timestamp << std::endl;
	os << "Merkle Root:\t" << header._merkleRoot << std::endl;
	os << "Difficulty: \t" << header._difficulty << std::endl;
	os << "Previous Block Private Key: \n\t" << header._prevPrivateKey << std::endl;
	os << "Next Block Public Key: \n\t" << header._nextPublicKey << std::endl;
	
	return os;
}
