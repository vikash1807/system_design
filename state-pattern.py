"""
This pattern lets the object change its behaviour with change of its internal state.

object behaviour changes based on the current context.

It allows an object (the Context) to alter its behavior when its internal state changes. The object appears to change its class because its behavior is now delegated to a different state object.


"""
from abc import ABC, abstractmethod

# 1. THE STATE INTERFACE
class MachineState(ABC):

    @abstractmethod
    def select_item(self, context, item_code : str):
        pass

    @abstractmethod
    def insert_money(self, context, amount : float):
        pass

    @abstractmethod
    def dispense_item(self, context):
        pass


# 2. CONCRETE STATE 1: IDLE
class IdleState(MachineState):

    def select_item(self, context, item_code: str):

        if context.inventory.get(item_code, 0) > 0:
            context.selected_item = item_code

            print(f"Item '{item_code}' selected. Price: ${context.prices[item_code]}")

            context.set_state(HasMoneyState())

        else:
            print(f"Sorry, {item_code} is out of stock!")

    def insert_money(self, context, amount: float):
        print("Please select an item first before inserting money.")

    def dispense_item(self, context):
        print("Nothing to dispense. Please select an item.")


# 3. CONCRETE STATE 2: HAS MONEY
class HasMoneyState(MachineState):

    def select_item(self, machine, item_code: str):
        print("Item already selected. Complete current transaction or cancel.")

    def insert_money(self, context, amount: float):

        context.balance += amount
        required_price = context.prices[context.selected_item]

        print(f"Inserted: ${amount:.2f}. Total Balance: ${context.balance:.2f}")

        if context.balance >= required_price:
            print("Sufficient funds received. Ready to dispense.")
            context.set_state(DispensingState())
        else:
            print(f"Remaining balance required: ${required_price - context.balance:.2f}")

    def dispense_item(self, context):
        print("Incomplete funds. Please add money.")


# 4. CONCRETE STATE 3: DISPENSING
class DispensingState(MachineState):
    def select_item(self, context, item_code: str):
        print("Processing current order. Please wait.")

    def insert_money(self, context, amount: float):
        print("Cannot accept money while dispensing.")

    def dispense_item(self, context):
        item = context.selected_item
        price = context.prices[item]
        change = context.balance - price

        # Deduct inventory & dispense
        context.inventory[item] -= 1
        print(f"Vending context sounds: *Clunk!* Enjoy your {item}!")

        if change > 0:
            print(f"Returning your change: ${change:.2f}")

        # Reset context state properties
        context.balance = 0.0
        context.selected_item = None
        
        # Cycle back to Idle
        context.set_state(IdleState())


class VendingMachine:

    def __init__(self):
        self.current_state = IdleState()
        self.balance = 0.0
        self.selected_item = None
        
        self.inventory = {
            "A1" : 3,
            "B2" : 0
        }
        self.prices = {
            "A1" : 1.5,
            "B2" : 1.3
        }

    def set_state(self, state : MachineState):
        self.current_state = state

    def set_selected_item(self, item_code):
        self.selected_item = item_code

    def set_balance(self, amount):
        self.balance = amount

    def get_selected_item(self):
        return self.selected_item

    def select_item(self, item_code : str):
        self.current_state.select_item(self, item_code)

    def insert_money(self, amount : float):
        self.current_state.insert_money(self, amount)

    def dispense(self):
        return self.current_state.dispense_item(self)


if __name__ == "__main__":
    # Create the machine
    vm = VendingMachine()

    print("--- Step 1: Try to buy an out of stock item ---")
    vm.select_item("B2") 

    print("\n--- Step 2: Proper transaction workflow ---")
    vm.select_item("A1")       # Moves to HasMoneyState
    vm.insert_money(1.00)      # Insufficient, stays in HasMoneyState
    vm.insert_money(0.50)       # Reaches $1.50, moves to DispensingState
    vm.dispense()              # Dispenses item, returns change, resets to IdleState

    print("\n--- Step 3: Trying to break rules out of order ---")
    vm.dispense()              # Blocked because machine reset back to Idle State!