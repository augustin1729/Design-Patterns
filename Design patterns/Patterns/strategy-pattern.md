# Strategy Pattern

> **The Strategy Pattern** defines a family of algorithms, encapsulates each one, and makes them interchangeable. Strategy lets the algorithm vary independently from clients that use it.

## Key Concepts
- **Family of Algorithms**: A set of related behaviors or logic (e.g., different ways a Duck can fly, or different ways to calculate a discount).
- **Encapsulation**: Each distinct behavior is moved into its own class (e.g., `FlyWithWings`, `FlyNoWay`).
- **Interchangeable**: Because all these classes implement the same common interface (e.g., `IFlyBehaviour`), they can be swapped out dynamically at runtime.

## Core Design Principles Used
This pattern is a direct implementation of three fundamental Object-Oriented Design Principles:
1. **Encapsulate what varies**: Separating the changing behaviors (like flying) from the static classes (like `Duck`).
2. **Program to an interface, not an implementation**: The client (`Duck`) holds a reference to an interface (`IFlyBehaviour`), not a concrete class.
3. **Favor composition over inheritance**: The client gets its behavior by holding an instance of a behavior class, rather than inheriting the behavior from a parent class.
