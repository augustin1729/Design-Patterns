#include <bits/stdc++.h>

using namespace std;

class Duck{
    public: 
    void display()
    {
        cout<<"display"<<endl;
    }
} 

class MallardDuck : public Duck{

    public:
    void display(){
        cout<<"MallardDuck display"<<endl;
    } 
    void fly(){
        cout<<"fly"<<endl;
    }
    
}

class BlueDuck : public Duck {
    public : 
    void display(){
        cout<<"BlueDuck display"<<endl;
    }
    void fly(){
        cout<<"fly"<<endl;
    }
}

class RubberDuck : public Duck{
    public : 
    void display(){
        cout<<"RubberDuck display"<<endl;
    }
}


int main (){

    return 0;
}
