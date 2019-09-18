#include <string>
#include <map>

#define STR_SWITCH_BEGIN(key) { \
	static std::map<std::string, int> s_hm; \
	static bool s_bInit = false; \
	bool bLoop = true; \
	while(bLoop) { \
		int nKey = -1; \
		if(s_bInit) { nKey = s_hm[key]; bLoop = false; } \
		switch(nKey) { \
			case -1: {

#define CASE(token)	} case __LINE__: if(!s_bInit) s_hm[token] = __LINE__; else {
#define DEFAULT()	} case 0: default: if(s_bInit) {

#define STR_SWITCH_END() \
			} \
		} \
		if(!s_bInit) s_bInit=true; \
	} \
}


