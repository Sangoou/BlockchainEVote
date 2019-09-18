#ifndef __KEY__
#define __KEY__
#include <stdio.h>
#include <vector>

using namespace std;

struct point {
    point(int X,int Y) : x(X), y(Y) {};
    int x;
    int y;
};


class Point{
    
    int private_key;    
    vector<point> inits;
    int p;
    int a,b,x,y,r,s;
    
    public:
        Point(int P);
        void ShowData()
        {
            printf("%d %d %d %d %d %d \n",p,x,y,r,s,private_key);
        }

        bool check();
        bool check2();
        void public_key_generation();
        void private_key_generation();
        vector<point> cryptography(point msg);
        point decryptography(vector <point> msg);
        point hashing(int data);
};


#endif