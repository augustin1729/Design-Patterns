using System;

namespace SimUDuck
{
    /* Initial Setup: 
    We have a base Duck class with several common methods like Display(), Swim(), and other duck-related behaviors.
    
    The Challenge:
    We want to introduce a Fly() behavior, but not all ducks can fly (e.g., RubberDucks or WoodenDecoys). 
    Let's discuss the initial approaches and why they fail:
    
    Approach 1: Adding the Fly() method to the base Duck class.
    Problem: In terms of maintenance, every derived class inherits this method. We would be forced to 
    override Fly() in subclasses that shouldn't fly (to do nothing), which is messy and error-prone.
    
    Approach 2: Creating an IFlyable interface and implementing it only in ducks that can fly.
    Problem: While this solves the issue of non-flying ducks inheriting the behavior, interfaces only provide 
    the structure, not the implementation. This forces us to write duplicate code in every flying duck class. 
    If the flying behavior ever changes, we have to track down and modify it in every single class.
    */

    /* 
    Solution Approach (The Strategy Pattern):
    To keep things flexible, we pull the varying behavior (flying) out of the Duck class entirely. 
    We define an IFlyBehaviour interface, and then create concrete classes for every specific 
    type of flying behavior (e.g., FlyWithWings, FlyNoWay).
    
    This allows us to compose our Ducks with specific behaviors rather than inheriting them, 
    meaning we can even change these behaviors dynamically at runtime!
    */

    // Step 1: Define the behavior interface 
    public interface IFlyBehaviour
    {
        void Fly();
    }
    
    public class FlyWithWings : IFlyBehaviour
    {
        public void Fly()
        {
            Console.WriteLine("fly");
        }
    }
    
    public class FlyNoWay : IFlyBehaviour
    {
        public void Fly()
        {
            Console.WriteLine("Can't fly");
        }
    }


    // Now here the Duck class now can be declared in the following manner. 

    // public class Duck
    // {
    //     protected IFlyBehaviour? flyBehaviour;

    //     public void FlyBehaviour(){
    //         flyBehaviour?.Fly();
    //     }

    //     public virtual void Display()
    //     {
    //         Console.WriteLine("display");
    //     }
    // }

    // Now let's see how we can set the behaviour during the runtime 

    public class Duck
    {
        protected IFlyBehaviour? flyBehaviour;

        public void FlyBehaviour()
        {
            flyBehaviour?.Fly();
        }

        public void setFlyBehaviour(IFlyBehaviour flyBehaviour)
        {
            this.flyBehaviour = flyBehaviour;
        }

        public virtual void Display()
        {
            Console.WriteLine("display");
        }
    }

    public class MallardDuck : Duck
    {
        public MallardDuck() {
            flyBehaviour = new FlyWithWings();
        }

        public override void Display()
        {
            Console.WriteLine("MallardDuck display");
        }

        public void Fly()
        {
            Console.WriteLine("fly");
        }
    }

    public class BlueDuck : Duck
    {
        public BlueDuck(){
            flyBehaviour = new FlyNoWay();
        }
        
        public override void Display()
        {
            Console.WriteLine("BlueDuck display");
        }

        public void Fly()
        {
            Console.WriteLine("fly");
        }
    }

    public class RubberDuck : Duck
    {
        public RubberDuck() {
            flyBehaviour = new FlyNoWay();
        }
        public override void Display()
        {
            Console.WriteLine("RubberDuck display");
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            // You can test your ducks here
            Duck mallard = new MallardDuck();
            mallard.Display();
            mallard.FlyBehaviour();

            Duck RubberDucky = new RubberDuck();
            RubberDucky.Display();
            RubberDucky.FlyBehaviour();

            RubberDucky.setFlyBehaviour(new FlyWithWings());
            RubberDucky.FlyBehaviour();
        }
    }
}
