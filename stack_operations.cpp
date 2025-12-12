#include<iostream>
using namespace std;

class Stack 
{
    private:
    int stack [100];
    int size;
    int top;

    public:
    Stack(int s)
    {
        size = s;
        top = -1;
    }

    void push (int item)
    {
        if (top ==size -1)
        {
                cout<<"Stack Overflow!!";
        }
        else{
            top ++;
            stack [top] = item;
            cout<<item<<"has been pushed to the stack\n";
        } 
    }
    void pop (){
        if (top ==-1){
            cout<<"Stack is underflow"<<endl;

        } else {
            cout<<"The top item at the stack is :"<<stack[top];
            top --;
        }
    }
    void peek(){
        if (top ==-1){
            cout<<"Stack underflow"<<endl;
        }
        else{
            cout<<"The top element at the stack is :"<<stack[top];
        }
    }
    void display(){
        if (top ==-1){
            cout<<"The stack is empty:"<<endl;
        }
        else{
            cout<<"Stack elements: ";
            for ( int i = top; i >= 0; i--){
                cout<<stack [i] <<" ";
            }
            cout<<endl;
        }
        
    }
    void sum (){
        if (top ==-1){
            cout<<"The stack is empty"<<endl;
        }
        else{
            int total = 0;
            for (int i= top; i >= 0; i --){
                total = total + stack [i];
            }
            cout<<"Sum of all elements in stack: "<<total<<endl;
        }
    }

};

int main() {
    int size, choice, item;
    
    cout << "Enter the size of the stack: ";
    cin >> size;
    
    Stack s(size);
    
    do {
        cout << "\n===== Stack Operations Menu =====\n";
        cout << "1. Push\n";
        cout << "2. Pop\n";
        cout << "3. Peek\n";
        cout << "4. Display\n";
        cout << "5. Sum of elements\n";
        cout << "6. Exit\n";
        cout << "Enter your choice: ";
        cin >> choice;
        
        switch (choice) {
            case 1:
                cout << "Enter item to push: ";
                cin >> item;
                s.push(item);
                break;
            case 2:
                s.pop();
                break;
            case 3:
                s.peek();
                break;
            case 4:
                s.display();
                break;
            case 5:
                s.sum();
                break;
            case 6:
                cout << "Exiting program...\n";
                break;
            default:
                cout << "Invalid choice! Please try again.\n";
        }
    } while (choice != 6);
    
    return 0;
}