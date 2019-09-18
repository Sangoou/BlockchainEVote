#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <ctime>

#include "lib/str_switch.h"
#include "lib/key.h"
#include "block.h"

using namespace std;

// string to vector.
vector<string> split(string str, char delimiter) {
    vector<string> internal;
    stringstream ss(str);
    string temp;
 
    while (getline(ss, temp, delimiter)) {
        internal.push_back(temp);
    }
 
    return internal;
}

// Start of Program.
int main(int argc, char *argv[]) {
	string cmdline;
	bool running = true;
	Block* currentBlock = new Block();

	while(running){
		// get command line
		cout << "/> ";
		getline(cin, cmdline);
		
		if(cmdline.empty())
			continue;
		
		// split command line
		vector<string> cmd = split(cmdline, ' ');
		
		// excute command
		STR_SWITCH_BEGIN(cmd[0])
			CASE("show") // show block. if no number show current block.
				if(cmd.size() > 1){
					if(Block::isBlockExist(atoi(cmd[1].c_str()))){
						cout << Block(atoi(cmd[1].c_str())) << endl;					
					} else {
						cout << "Block " << cmd[1] << " doesn't Exist." << endl;
					}
				} else {
					cout << *currentBlock << endl;					
				}
				break;
			CASE("write") // add content to current block
				if(cmd.size() > 1){
					string content = "";
					for(int i = 1; i< cmd.size(); i++)
						content += cmd[i];
						
					//두번째 인자 받아서 암호화 후 추가 
					currentBlock->addContent(content);
					///////////////
				} else {
					cout << "Input Content!" << endl;
				}
				break;
			CASE("decrypt") // Decrypt BLock.
				if(cmd.size() > 1) {
					if(Block::isBlockExist(atoi(cmd[1].c_str()) + 1)){
						Block block(atoi(cmd[1].c_str()));
						vector<string> decryptedContent = block.decrpyt();
						cout << cmd[1] << " Block Content" << endl;
						for(int i = 0; i < decryptedContent.size(); i++){
							cout << decryptedContent[i] << endl;
						}
					} else{
						cout << to_string(atoi(cmd[1].c_str()) + 1) << " Block isn't Mined yet." << endl;
					}
				} else {
					cout << "Input Block Number!" << endl;
				} 
				break;
			CASE("mine") // mine current block
				clock_t startTime = clock();
				clock_t endTime;
				cout << "Start Clock: " << startTime << endl;
				currentBlock->mine();
				endTime = clock();
				cout << "End Clock: " << endTime << endl;
				cout << "Excute Time: " << (endTime-startTime)/CLOCKS_PER_SEC << endl;
				
				// new Block
				delete currentBlock;
				currentBlock = new Block();
				break; 
			CASE("exit") // exit program.
				running = false;
				break;
			DEFAULT()
				cout << cmdline << " is invalid! please check your input." << endl;
		STR_SWITCH_END()
	}
	
	// program exit

	return 0;
}
