#include <iostream>
#include <vector>
#include <string>
#include <ctime>

#define BLOCK_VERSION	0
#define INITIAL_DIFFICULTY	10007

//struct PublicKey {
//	int 
//};

class Header {
	private:
		int _version, _timestamp, _difficulty;
		std::string _merkleRoot, _prevPrivateKey, _nextPublicKey;
		
	public:
		Header(){
			_version = 0;
			_timestamp = 0;
			_difficulty = 0;
			_merkleRoot = "";
			_prevPrivateKey = "";
			_nextPublicKey = "";
		}
		int getVersion() const{ return _version; }
		int getTimestamp() const{ return _timestamp; } 
		int getDifficulty() const{ return _difficulty; }
		
		const std::string& getMerkleRoot() const{ return _merkleRoot; }
		const std::string& getPrevPrivateKey() const{ return _prevPrivateKey; }
		const std::string& getNextPublicKey() const{ return _nextPublicKey; }
		
		
		void setVersion(int version){ _version = version; }
		void setTimestamp(int timestamp){ _timestamp = timestamp; } 
		void setDifficulty(int difficulty){ _difficulty = difficulty; }
		
		void setMerkleRoot(const std::string& merkleRoot){ _merkleRoot = merkleRoot; }
		void setPrevPrivateKey(const std::string& prevPrivateKey){ _prevPrivateKey = prevPrivateKey; }
		void setNextPublicKey(const std::string& nextPublicKey){ _nextPublicKey = nextPublicKey; }
		
		friend std::ostream& operator<<(std::ostream& os, const Header& header);
};

class Block {
	private:
		Header _header;
		std::vector<std::string> _body;
		int _blockNumber;
		std::string _publicKey, _privateKey;
		
		/**
 		* Read File and Load Block 
		* 
		* @ param int n -> Block Number
		* @ return is load Block Success
		*/
		bool _loadBlock(int num);
		
		/**
 		* Write Block to File 
		* 
		* @ return is Write File Success
		*/
		bool _writeBlock();
		
	public:
		Block();
		
		/**
 		* If n Block exist -> Load n BLock
 		* If n Block not Exist & n-1 Block exist -> create New Block 
		* 
		* @ param int n -> Block Number
		*/
		Block(int n);
		friend std::ostream& operator<<(std::ostream& os, const Block& block);
		
		/**
 		* Add content to body
		* 
		* @ param string str -> new Content
		*/
		void addContent(const std::string str){
			_body.push_back(str);
		}
		
		/**
 		* Mine Block & Write Block to File
		* 
		* @ exception if already mined Block, abort
		*/
		void mine();
		
		/**
 		* Mine Block & Write Block to File
		* 
		* @ return Decrpyted content
		*/
		std::vector<std::string> decrpyt() const;
		
		/**
 		* Check Block N is exist
		* 
		* @ param int n -> Block Number
		* @ return is Block Exist
		*/
		static bool isBlockExist(int n);
		
		/**
 		* Get Last Block Number
		* 
		* @ return Last Block Number
		*/
		static int getLastBlockNumber();
};

