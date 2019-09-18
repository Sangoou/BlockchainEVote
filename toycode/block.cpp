#include "block.h"

#include "lib/hash.h"
#include "lib/key.h"

#include <iostream>
#include <fstream>
#include <string>
#include <ctime>

using namespace std;

Block::Block(){
	_blockNumber = Block::getLastBlockNumber() + 1;
	
	_header.setDifficulty(INITIAL_DIFFICULTY);
	_header.setVersion(BLOCK_VERSION);
	// 이전 블록 읽어와서
	Block prevBlock(_blockNumber - 1);
	string prevHeader 	= to_string(prevBlock._header.getVersion())	+ to_string(prevBlock._header.getTimestamp())
						+ prevBlock._header.getMerkleRoot()	+ to_string(prevBlock._header.getDifficulty())
						+ prevBlock._header.getPrevPrivateKey()	+ prevBlock._header.getNextPublicKey();
	
	while(true){
		// Prevheader를 이용하여 공개키 계산후 집어넣기 	
		
		_header.setNextPublicKey(to_string(hashString(prevHeader)));
		//////
		break;
	}
}

Block::Block(int n) {
	_loadBlock(n);
}

bool Block::_loadBlock(int n){
	if(Block::isBlockExist(n)){
		ifstream fp;
		fp.open("data/" + to_string(n) + ".txt");
		
		// Load Header
		string tmp;
		fp >> tmp;
		_header.setVersion(atoi(tmp.c_str()));
		
		fp >> tmp;
		_header.setTimestamp(atoi(tmp.c_str()));
		
		fp >> tmp;
		_header.setMerkleRoot(tmp);
		
		fp >> tmp;
		_header.setDifficulty(atoi(tmp.c_str()));
		
		fp >> tmp;
		_header.setPrevPrivateKey(tmp);
		
		fp >> tmp;
		_header.setNextPublicKey(tmp);
		
		// Load Body
		while(!fp.eof()){
			fp >> tmp;
			_body.push_back(tmp);
		}
		
		fp.close();
		
		return true;
	}
	else {
		cout << "Load Block Error! " << n << " Block doen't Exist." << endl; 
		return false;		
	}
}

bool Block::_writeBlock(){
	ofstream fp;
	fp.open("data/" + to_string(_blockNumber) + ".txt");
	
	// Write Header
	fp << _header.getVersion() << endl;
	fp << _header.getTimestamp() << endl;
	fp << _header.getMerkleRoot() << endl;
	fp << _header.getDifficulty() << endl;
	fp << _header.getPrevPrivateKey() << endl;
	fp << _header.getNextPublicKey() << endl;
	
	// Write Body
	for(int i = 0; i < _body.size(); i++){
		fp << _body[i] << endl;
	}
	
	fp.close();
}

vector<string> Block::decrpyt() const{
	vector<string> result;
	// 개인키 받기
	for(int i = 0; i < _body.size(); i++){
		// 하나하나 복호화	
	}
	return result;
}

void Block::mine(){
	if(!_header.getPrevPrivateKey().empty()){
		return;
	}
	
	while(true){
		// 개인키 계산 	
		break;
	}
	
	_header.setMerkleRoot(to_string(hashVector(_body)));
	_header.setTimestamp(time(0));
	_writeBlock(); 
}

bool Block::isBlockExist(int n){
	ifstream fp;
	
	fp.open("data/" + to_string(n) + ".txt");
	if(fp){
		fp.close();
		return true;
	}
	return false;
}

int Block::getLastBlockNumber(){
	for(int i = 1; ; i++){
		if(!Block::isBlockExist(i)){
			return i-1;
		}
	}	
}

ostream& operator<<(ostream& os, const Header& header){
	os << "Version:\t" << header._version << endl;
	os << "Time:\t\t" << header._timestamp << endl;
	os << "Merkle Root:\t" << header._merkleRoot << endl;
	os << "Difficulty: \t" << header._difficulty << endl;
	os << "Previous Block Private Key: \n\t" << header._prevPrivateKey << endl;
	os << "Next Block Public Key: \n\t" << header._nextPublicKey << endl;
	
	return os;
}

ostream& operator<<(ostream& os, const Block& block) {
	os << "<-------------- Header -------------->" << endl;
	os << block._header << std::endl;
	
	os << "<--------------- Body --------------->" << endl;
	for(int i = 0; i < block._body.size(); i++) {
		os << block._body[i] << std::endl;
	}
	
	return os;
}


