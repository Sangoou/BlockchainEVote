#include <stdio.h>
#include "key.h"
#include <cstdlib>
#include <ctime>
#include <cmath>
#include <vector>

using namespace std;
vector<point> inits;
int x,x_,y,y_;
int private_key;

int isPrime(int p)
{
    int ceil = sqrt(p);
    int A = 1;
    for(int i=2;i<=ceil;i++)
    {
        if(p%i==0) A=0;
    }
    return A;
}

point doubling(int p,int a,point p_)
{
    int temp_x = p_.x;
    int temp_y = p_.y;
    int temp1 = 3*pow(temp_x,2) + a;

    int temp2 = 2*temp_y;
    double lambda;
    if(temp1 % temp2 == 0) lambda = temp1 / temp2;
    else
    {
        temp1 = temp1 % p;
        temp2 = temp2 % p;

        for(int i=0;i<p-2;i++)
        {
            temp1 *= temp2;
            temp1 = temp1 % p;
        }
        
        lambda = temp1;
    }

    int next_x = (pow(lambda,2) - 2*temp_x);

    if(next_x < 0)
    {
        int temp = next_x / p * -1;
        next_x += (temp+1)*p;
    }

    next_x = next_x % p;
    int next_y = ((temp_x-next_x) * lambda - temp_y) ;  

    if(next_y < 0)
    {
        int temp = next_y / p * -1;
        next_y += (temp+1)*p;
    }

    next_y = next_y % p;
    point next(next_x,next_y);

    return next;
}

point addition(int p,point p_,point q_)
{
    int temp1 = p_.y - q_.y;
    int temp2 = p_.x - q_.x;
    double lambda;
    if(temp1 < 0)
    {
        int temp = temp1 / p * -1;
        temp1 += (temp+1)*p;
    }

    if(temp2 < 0)
    {
        int temp = temp2 / p * -1;
        temp2 += (temp+1)*p;
    }

    if(temp1 % temp2 == 0) lambda = temp1 / temp2;
    else
    {
        temp1 = temp1 % p;
        temp2 = temp2 % p;
        for(int i=0;i<p-2;i++)
        {
            temp1 *= temp2;
            temp1 = temp1 % p;
        }
        
        lambda = temp1;
    }

    int next_x = ((int) pow(lambda,2) - q_.x - p_.x) ;
    
    if(next_x < 0)
    {
        int temp = next_x / p * -1;
        next_x += (temp+1)*p;
    }
    next_x = next_x % p;
    int next_y = ((p_.x-next_x)*(int)lambda - p_.y);

    if(next_y < 0)
    {
        int temp = next_y / p * -1;
        next_y += (temp+1)*p;
    }

    next_y = next_y % p;
    point next(next_x,next_y);
    return next;
        
}
bool Point :: check()
{
    if(x!= -1 && y != -1 && r != -1 && s != -1)
    {
        return true;
    }
    else    return false;
}

bool Point :: check2()
{
    if(p==-1)
    {
        return false;
    }
    else    return true;
}

Point :: Point(int P) 
{
    x = -1;
    y = -1;
    r = -1;
    s = -1;
    a = 0;
    b = 7;
    p = -1;
    int check = 1;
    for(int i=0;i<P;i++)
    {
        double temp=1;
        for(int j=0;j<3;j++)
        {
            temp*=i;
            temp = (int) temp % P;
        }
        temp += a*i + b ;
        temp = (int)temp % P;

        for(int j=0;j<P;j++)
        {
            if( (j*j) % P == (int) temp)
            { 
                if(temp == 0) check = 0; 
                inits.push_back(point(i,j));
            }
        }
    }

    if(check==0) printf("Please Enter another prime P\n");
    else{
        p = P;
    }
}

void Point ::  public_key_generation()
{
    srand((unsigned int)time(NULL));
    int size = inits.size();
    int temp_x,temp_y=-1;
    int check=0;
    
    while(temp_y < 0)
    {
        temp_x = rand() % p;
        double temp=1;
        for(int j=0;j<3;j++)
        {
            temp*=temp_x;
            temp = (int) temp % p;
        }
        temp += a*temp_x + b ;
        temp = (int)temp % p;
        for(int i=0;i<p;i++)
        {
            if( (i*i) % p == temp)
            {
                temp_y = i;
                break;
            }
        } 

    }           
    x = temp_x;
    y = temp_y;
    r = temp_x;
    s = p-temp_y;
}

void Point :: private_key_generation()
{
    int count=1;
    point next(0,0);
    next = doubling(p,a, point(x,y));
    count++;
    while(next.x != r || next.y != s)
    {   
        next = addition(p,next,point(x,y));
        count++;
    }
    private_key = count;
}

vector<point> Point :: cryptography(point msg)
{
    vector<point> result;
    srand((unsigned int)time(NULL));
    int rand_num = 0;
    int temp1, temp2;
    int next_x,next_y;
    point next(0,0);
    int check=0;

    while(check==0)
    {
        rand_num = (rand() % 10)+2;
        next.x=0;
        next.y=0;
        result.clear();
        for(int i=0;i<rand_num;i++)
        {   
            if(next.x == x && next.y != y)
            {
                next.x=0;
                next.y=0;
            }

            else if(next.x == 0 && next.y == 0)
            {
                next.x = x;
                next.y = y;
            }
            
            else if(next.x == x && next.y == y)
                next = doubling(p,a,point(x,y));

            else
                next = addition(p,next,point(x,y));
        }

        if(next.x==0 && next.y == 0 ) continue;
        result.push_back(next);
        next.x=0;
        next.y=0;

        for(int i=0;i<rand_num;i++)
        {            
            if(next.x == r && next.y != s)
            {
                next.x=0;
                next.y=0;
            }

            else if(next.x == 0 && next.y == 0)
            {
                next.x = r;
                next.y = s;
            }
            
            else if(next.x == r && next.y == s)
                next = doubling(p,a,point(r,s));

            else
                next = addition(p,next,point(r,s));
        }

        if(next.x == msg.x)
        {
            continue;
        }
        
        else
        {
            check = 1;
            next = addition(p,next,msg);
        }
    }
    result.push_back(next);

    return result;
}

point Point :: decryptography(vector <point> msg)
{
    point next(0,0);
    for(int i=0;i<private_key;i++)
    {
        if(next.x == msg[0].x && next.y != msg[0].y)
        {
            next.x=0;
            next.y=0;
        }

        else if(next.x == 0 && next.y == 0)
        {
            next.x = msg[0].x;
            next.y = msg[0].y;
        }
        
        else if(next.x == msg[0].x && next.y == msg[0].y)
            next = doubling(p,a,msg[0]);

        else
            next = addition(p,next,msg[0]);
    }

    next.y = p-next.y;

    point result(0,0);

    if(msg[1].x != next.x)
        result = addition(p,msg[1],next);

    else if(msg[1].x == next.x && msg[1].y == next.y)
        result = doubling(p,a,next);

    return result;
}

point Point :: hashing(int data)
{
    srand((unsigned int)time(NULL));
    point next(0,0);
    int check = 0;

    while(check==0)
    {
        next.x = 0;
        next.y = 0;
        data = rand() % 100 + 5;

        for(int i=0;i<data;i++)
        {
            
            if(next.x == x && next.y != y)
            {
                next.x=0;
                next.y=0;
            }

            else if(next.x == 0 && next.y == 0)
            {
                next.x = x;
                next.y = y;
            }
            
            else if(next.x == x && next.y == y)
                next = doubling(p,a,point(x,y));

            else
                next = addition(p,next,point(x,y));
        }

        if(next.x !=0 && next.y !=0)    check=1;
    }
    return next;
}