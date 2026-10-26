# Python OOP and UML — Revision Notes

A concise reference for revising intermediate Python OOP fundamentals and UML concepts for low-level design (LLD) interviews.

## Contents

1. [Classes and objects](#1-classes-and-objects)
2. [Method types](#2-method-types)
3. [Four pillars of OOP](#3-four-pillars-of-oop)
4. [Inheritance, overriding, `super()`, and MRO](#4-inheritance-overriding-super-and-mro)
5. [Encapsulation and properties](#5-encapsulation-and-properties)
6. [Composition, aggregation, association, and dependency](#6-composition-aggregation-association-and-dependency)
7. [Python special methods and built-in protocols](#7-python-special-methods-and-built-in-protocols)
8. [Dataclasses](#8-dataclasses)
9. [Duck typing, ABCs, and Protocols](#9-duck-typing-abcs-and-protocols)
10. [Other Python object-model details](#10-other-python-object-model-details)
11. [UML fundamentals](#11-uml-fundamentals)
12. [UML class relationships](#12-uml-class-relationships)
13. [Multiplicity and interfaces](#13-multiplicity-and-interfaces)
---

## 1. Classes and objects

A **class** defines data and behavior; an **object** is an instance of a class.

```python
class Employee:
    company = "Acme"  # Class attribute

    def __init__(self, name, salary):
        self.name = name       # Instance attributes
        self.salary = salary

    def display(self):
        return f"{self.name}: {self.salary}"


e1 = Employee("Aman", 50_000)
e2 = Employee("Riya", 60_000)
```

Key points:

- `__new__` creates an instance; `__init__` initializes it.
- `self` is the conventional name for the current instance, not a keyword.
- Class attributes are stored on the class and can be shared by instances.
- Instance attributes belong to a particular instance and can shadow class attributes.
- Avoid mutable class attributes when each object needs its own list or dictionary.

```python
class Team:
    def __init__(self):
        self.members = []  # Separate list per Team instance
```

---

## 2. Method types

### Instance method

Receives `self`; typically reads or changes instance state.

```python
def set_salary(self, salary):
    self.salary = salary
```

### Class method

Uses `@classmethod` and receives `cls`, the class through which it was called. Useful for alternate constructors and class-level operations.

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    @classmethod
    def from_string(cls, text):
        name, salary = text.split(",")
        return cls(name, int(salary))
```

Using `cls(...)` supports subclass construction better than hardcoding `Employee(...)`.

### Static method

Uses `@staticmethod`; no `self` or `cls` is passed automatically. Useful for a related utility that doesn't need instance or class state.

```python
@staticmethod
def valid_salary(salary):
    return salary >= 0
```

---

## 3. Four pillars of OOP

### Encapsulation

Bundle state and behavior together; provide controlled access to internal state. Python uses conventions rather than strict public/protected/private access modifiers.

- `name`: public
- `_name`: intended for internal use by convention
- `__name`: name-mangled to reduce accidental collisions in subclasses; not truly private

### Inheritance

A subclass specializes and reuses behavior from a parent class: an **IS-A** relationship.

```python
class Animal:
    def speak(self):
        return "sound"

class Dog(Animal):
    def speak(self):
        return "bark"
```

### Polymorphism

The same operation can behave differently for different objects.

```python
def make_sound(animal):
    return animal.speak()

make_sound(Dog())  # "bark"
```

Python often uses duck typing; a common base class is not always required.

### Abstraction

Expose essential operations while hiding implementation details. Abstract base classes can define required methods.

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, data):
        pass
```

A concrete subclass must implement abstract methods before it can be instantiated.

---

## 4. Inheritance, overriding, `super()`, and MRO

### Overriding

A subclass provides its own implementation of an inherited method.

### Overloading

Traditional signature-based method overloading is not directly supported in Python. Related patterns can use default arguments, `*args`, or dispatch tools such as `functools.singledispatchmethod`.

### `super()`

`super()` continues method lookup after the current class according to the **Method Resolution Order (MRO)**. It does not simply mean “call my direct parent.”

```python
class A:
    def greet(self):
        print("A")

class B(A):
    def greet(self):
        print("B")
        super().greet()

class C(A):
    def greet(self):
        print("C")
        super().greet()

class D(B, C):
    pass

print(D.mro())  # D -> B -> C -> A -> object
D().greet()     # B, C, A
```

Python uses C3 linearization to calculate MRO. Cooperative multiple inheritance relies on participating methods consistently calling `super()`.

**Use MRO knowledge to:** understand which implementation runs, debug mixins, and avoid incorrect assumptions in multiple inheritance.

Prefer simple hierarchies; use composition when the relationship is HAS-A rather than IS-A.

---

## 5. Encapsulation and properties

A property provides attribute-style access while allowing custom getter/setter logic.

```python
class Account:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = value


account = Account(1000)
print(account.balance)  # Calls getter
account.balance = 2000  # Calls setter
# account.balance = -5  # Raises ValueError
```

- `@property` defines the getter.
- `@balance.setter` defines what happens on `account.balance = value`.
- Store the value under a different internal name, such as `_balance`, to avoid recursively calling the property.
- `@balance.deleter` can define deletion behavior if needed.
- Properties are useful for validation, computed attributes, and evolving an API without changing attribute-style access.
- A leading underscore is a convention, not a security boundary.

---

## 6. Composition, aggregation, association, and dependency

These are conceptual design relationships, not separate Python keywords. They describe how objects are connected and who owns what.

### Composition — strong ownership, HAS-A

An object owns a component as part of its design. The component's conceptual lifecycle is tied closely to the owner.

```python
class Engine:
    def start(self):
        print("Started")

class Car:
    def __init__(self):
        self.engine = Engine()

    def start(self):
        self.engine.start()
```

The car creates its engine. Python does not enforce ownership or automatically destroy an engine when the car is deleted; object lifetime depends on references.

**Use when:** a component is an integral part of the owning object.

### Aggregation — grouping independent objects, HAS-A

A container references objects that can exist independently.

```python
class Player:
    def __init__(self, name):
        self.name = name

class Team:
    def __init__(self, players):
        self.players = players

p1 = Player("Aman")
p2 = Player("Riya")
team = Team([p1, p2])
```

The players are created independently and passed into the team.

**Use when:** an object groups or references independently meaningful objects.

### Association — objects are related

One object knows about or references another. Neither necessarily owns the other.

```python
class TrainingJob:
    def __init__(self, job_id):
        self.job_id = job_id

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.jobs = []

    def submit(self, job):
        self.jobs.append(job)
```

Associations can be one-way or bidirectional, and can have different multiplicities. Bidirectional references need consistency management.

### Dependency — one object uses another

A class temporarily uses another object, often through a method parameter or local variable.

```python
class ModelService:
    def publish(self, storage, filename):
        storage.save(filename)
```

**Use when:** a class needs another object to perform an operation but need not retain it as state.

### Dependency injection

Supply a dependency from outside instead of constructing it inside the class. This makes implementations easier to swap and test.

```python
class ModelService:
    def __init__(self, storage):
        self.storage = storage

    def publish(self, filename):
        self.storage.save(filename)
```

A service that stores a dependency has an association with that object and also depends on its behavior. These categories can overlap.

---

## 7. Python special methods and built-in protocols

A **protocol** is a set of behaviors or methods that lets an object work with a Python operation. Special methods are often called “dunder” methods because their names have double underscores.

Python's implicit special-method lookup is not always identical to ordinary attribute lookup; direct calls below are useful mental models.

| Operation / protocol | Method(s) | Example use |
|---|---|---|
| String representation | `__str__`, `__repr__` | `print(obj)`, debugging |
| Length | `__len__` | `len(obj)` |
| Iteration | `__iter__`, `__next__` | `for item in obj` |
| Membership | `__contains__` | `item in obj` |
| Item access | `__getitem__`, `__setitem__` | `obj[key]`, `obj[key] = value` |
| Equality / ordering | `__eq__`, `__lt__` | `a == b`, `a < b` |
| Arithmetic | `__add__`, `__mul__` | `a + b`, `a * b` |
| Context manager | `__enter__`, `__exit__` | `with resource:` |
| Callable instance | `__call__` | `obj(args)` |
| Hashing | `__hash__` | Dictionary keys and set elements |

### Length protocol

```python
class Team:
    def __init__(self, members):
        self.members = members

    def __len__(self):
        return len(self.members)

team = Team(["Aman", "Riya"])
print(len(team))  # 2
```

### Iteration protocol

```python
class TaskBatch:
    def __init__(self, tasks):
        self.tasks = tasks

    def __iter__(self):
        return iter(self.tasks)

for task in TaskBatch(["train", "infer"]):
    print(task)
```

Returning an existing iterator means you don't need to implement `__next__` yourself.

### Context manager protocol

```python
class ManagedResource:
    def __enter__(self):
        print("Acquire")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Release")
        return False  # Do not suppress exceptions

with ManagedResource():
    print("Use")
```

`__exit__` runs when leaving the block, including when an exception occurs. Context managers are useful for files, locks, transactions, and other resources.

### Callable objects

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, number):
        return number * self.factor

double = Multiplier(2)
print(double(5))  # 10
```

Useful for stateful processors, validators, and configurable functions.

### Equality and hashing

```python
class User:
    def __init__(self, user_id):
        self.user_id = user_id

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return self.user_id == other.user_id
```

Defining `__eq__` without a compatible `__hash__` normally makes instances unhashable. Hashes must be consistent with equality, and hash-relevant fields must not change while an object is in a set or used as a dictionary key.

Implement protocols when their behavior makes sense for your class; don't add every special method automatically.

---

## 8. Dataclasses

`dataclasses` reduce boilerplate for classes primarily used to hold structured data.

```python
from dataclasses import dataclass

@dataclass
class TrainingJob:
    job_id: str
    model_name: str
    epochs: int

job = TrainingJob("job-101", "detector-v1", 20)
print(job)
```

By default, a dataclass generates methods including `__init__`, `__repr__`, and `__eq__`. Type annotations describe expected types but do not automatically validate them at runtime.

### `default_factory` for mutable values

```python
from dataclasses import dataclass, field

@dataclass
class TrainingJob:
    job_id: str
    tags: list[str] = field(default_factory=list)

job1 = TrainingJob("job-1")
job2 = TrainingJob("job-2")
job1.tags.append("gpu")

print(job1.tags)  # ['gpu']
print(job2.tags)  # []
```

Each instance gets a separate list.

### Other useful options

```python
@dataclass(frozen=True)
class ModelConfig:
    name: str
    version: int
```

- `frozen=True`: prevents normal attribute reassignment; shallow, not deep, immutability.
- `order=True`: generates ordering comparisons based on declared fields.
- `slots=True`: uses slots to restrict arbitrary instance attributes and may reduce memory use.
- `field(default_factory=list)`: creates a new list for each instance.

**Use dataclasses for:** job records, configuration, structured results, and internal data objects.

**Use a regular class when:** construction, lifecycle, or state management needs substantial custom behavior. For external API input with runtime validation, a library such as Pydantic may be more appropriate.

---

## 9. Duck typing, ABCs, and Protocols

### Duck typing

“An object is suitable if it supports the behavior the code needs.” A common base class is not required.

```python
class EmailNotifier:
    def send(self, message):
        print(f"Email: {message}")

class SlackNotifier:
    def send(self, message):
        print(f"Slack: {message}")

def notify(notifier, message):
    notifier.send(message)

notify(EmailNotifier(), "Job completed")
notify(SlackNotifier(), "Job completed")
```

`notify` only requires a compatible `send()` method. This makes it easy to add implementations and fake objects for tests. The method must have compatible arguments and behavior, not merely the same name.

### Abstract base class (ABC)

Use `ABC` and `@abstractmethod` to define a contract and prevent instantiation until required methods are implemented.

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, data):
        pass

class LocalStorage(Storage):
    def save(self, data):
        print("Saving locally")
```

### `typing.Protocol`

A protocol describes a structural interface primarily for static type checking. Compatible classes do not have to inherit from it.

```python
from typing import Protocol

class Storage(Protocol):
    def save(self, data: bytes) -> None:
        ...

class S3Storage:
    def save(self, data: bytes) -> None:
        print("Saving to S3")
```

| Approach | Compatibility | Typical use |
|---|---|---|
| Duck typing | Required behavior works | Flexible runtime code |
| ABC | Explicit inheritance; abstract methods can be enforced at instantiation | Shared contract and possibly shared implementation |
| `Protocol` | Structural compatibility, primarily checked by type checkers | Typed interfaces and dependency injection |

---

## 10. Other Python object-model details

### Everything is an object

```python
class A:
    pass

a = A()
print(type(a))  # A
print(type(A))  # type
print(isinstance(a, A))  # True
```

Classes are themselves objects; user-defined classes are normally instances of `type`.

### Attribute lookup

For ordinary instance attribute lookup, Python generally checks data descriptors on the class/MRO, then the instance dictionary, then non-data descriptors and other class attributes. Properties are data descriptors; methods defined as ordinary functions on a class are non-data descriptors.

This explains why a property can take precedence over an instance attribute with the same name.

### Bound methods

```python
class Demo:
    def greet(self):
        return "Hello"

obj = Demo()
obj.greet()       # Python supplies obj as self
Demo.greet(obj)   # Explicit equivalent
```

### Identity vs. equality

- `is`: checks whether two references point to the same object.
- `==`: checks equality, using `__eq__` where appropriate.
- `id(obj)`: identity value for the object's lifetime.

### `__slots__`

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
p.x = 10       # Allowed
# p.z = 3       # AttributeError
```

Slots can restrict arbitrary instance attributes and reduce memory overhead. They do not automatically make instances immutable.

### Type hints

Python type annotations support documentation, editors, and static analysis; they do not enforce types at runtime by themselves.

---

## 11. UML fundamentals

**UML (Unified Modeling Language)** is a standard visual language for describing software systems.

Useful diagrams for LLD:

- **Class diagram:** classes, attributes, methods, and relationships.
- **Sequence diagram:** object interactions over time.
- **Activity diagram:** workflow, branches, and loops.
- **State machine diagram:** object states and transitions.

Start with class diagrams for most LLD exercises.

### UML class box

A class rectangle commonly has three sections:

```text
TrainingJob
-------------------------
- job_id: str
- status: str
- epochs: int
-------------------------
+ start(): None
+ cancel(): bool
+ get_status(): str
```

- Top: class name.
- Middle: attributes.
- Bottom: methods.

Visibility symbols:

| Symbol | UML meaning | Python convention |
|---|---|---|
| `+` | Public | `name` |
| `-` | Private | Often `_name` by convention; not strict privacy |
| `#` | Protected | Often `_name` by convention |
| `~` | Package | No direct equivalent |

Method signatures show parameter and return types, for example `+ retry(delay_seconds: int): bool`. UML normally omits `self` because it is implicit in ordinary instance-method calls.

---

## 12. UML class relationships

### Inheritance / generalization

Solid line with a hollow triangle pointing to the parent:

```text
Dog ─────────▷ Animal
```

Read as: Dog **is an** Animal.

Python: `class Dog(Animal):`

### Realization / implements an interface

Dashed line with a hollow triangle pointing to the interface:

```text
S3Storage - - - -▷ Storage
```

Read as: S3Storage implements the Storage contract.

### Composition

Solid line with a **filled diamond at the owner end**:

```text
Car ◆──────── Engine
```

Read as: Car strongly owns an Engine as a component.

### Aggregation

Solid line with a **hollow diamond at the grouping end**:

```text
Team ◇──────── Player
```

Read as: Team groups independent Player objects.

### Association

A solid line; an optional arrowhead can indicate navigability:

```text
User ───────── TrainingJob
```

Read as: User is associated with TrainingJob.

### Dependency

Dashed line with an open arrowhead pointing toward the dependency:

```text
TrainingService - - - - > Storage
```

Read as: TrainingService uses Storage.

### Relationship cheat sheet

| Relationship | Main question | Example |
|---|---|---|
| Inheritance | Is A a type of B? | Dog is an Animal |
| Realization | Does A implement B's contract? | S3Storage implements Storage |
| Composition | Does A strongly own B? | Car owns Engine |
| Aggregation | Does A group independent B objects? | Team groups Players |
| Association | Are A and B connected? | User and TrainingJob |
| Dependency | Does A use B to do work? | Service uses Storage |

These categories are conceptual and can overlap. Python doesn't enforce composition or aggregation as language-level constructs.

---

## 13. Multiplicity and interfaces

### Multiplicity

Multiplicity states how many objects can participate in a relationship.

| Notation | Meaning |
|---|---|
| `1` | Exactly one |
| `0..1` | Zero or one |
| `*` / `0..*` | Zero or many |
| `1..*` | One or many |
| `2..5` | Between two and five |

Example: each training job has exactly one owner, while a user can have zero or many jobs.

```text
User "1" ───────── "0..*" TrainingJob
```

The number beside `User` means each job relates to one user. The number beside `TrainingJob` means a user may relate to many jobs.

### Interfaces in UML

An interface defines operations without specifying implementation details. It can be shown using `<<interface>>`.

```text
        <<interface>>
           Storage
    ---------------------
    + save(data): None
    + load(key): bytes
             △
             ┆
      ┌──────┴──────┐
  S3Storage    LocalStorage
```

The implementation lines are dashed and point to the interface with hollow triangles.

In Python, an interface-like contract can be expressed with an ABC or a `Protocol`.