using System;

namespace SimUDuck
{
    public class Duck
    {
        public virtual void Display()
        {
            Console.WriteLine("display");
        }
    }

    public class MallardDuck : Duck
    {
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
        }
    }
}
