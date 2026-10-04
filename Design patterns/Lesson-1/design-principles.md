# Object-Oriented Design Principles

## Principle 1: Encapsulate what varies
> **Identify the aspects of your application that vary and separate them from what stays the same.**

**In other words:** 
Take the parts that vary and encapsulate them, so that later you can alter or extend the parts that vary without affecting those that don't.

## Principle 2: Program to an interface
> **Program to an interface, not an implementation.**

**In other words:**
Variables should be declared using a supertype (usually an interface or an abstract class). This way, the object assigned to those variables can be of any concrete implementation, decoupling the runtime object from the code that uses it.

## Principle 3: Favor composition over inheritance
> **Favor composition over inheritance.**

**In other words:**
Instead of inheriting behavior from a superclass, objects should get their behavior by holding references to other objects that provide it (like a `Duck` holding an `IFlyBehaviour`). This allows behaviors to be changed dynamically at runtime and avoids the rigid, deeply nested class hierarchies that inheritance often creates.
