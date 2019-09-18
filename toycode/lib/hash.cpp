#include "hash.h"

#include <string>
#include <vector>

using namespace std;

unsigned int hashString(string& str){
	unsigned int result = 0;
	
	for(int i = 2; i < str.length(); i += 3){
		result = (result + str[i] * str[i-1] * str[i-2]) % HASH_PRIME_NUMBER;
	}
	
	 return result;
}


unsigned int hashVector(std::vector<std::string>& vec){
	unsigned result = 0;
	
	for(int i = 0; i < vec.size(); i++){
		result = (result + hashString(vec[i])) % HASH_PRIME_NUMBER;
	}
	
	return result;
}
