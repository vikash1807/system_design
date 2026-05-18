from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def process_payment(self, amount: int):
        pass

class CreditPayment(PaymentMethod):
    def process_payment(self, amount):
        print(f"processing credit card payment of {amount}")
        
class UPIPayment(PaymentMethod):
    def process_payment(self, amount):
        print(f"processing UPI payment of {amount}")
        
class PaypalPayment(PaymentMethod):
    def process_payment(self, amount):
        print(f"processing paypal payment of {amount}")

class PaymentProcessor:
    def process(self, payment_method: PaymentMethod, amount: int):
        payment_method.process_payment(amount)
        

class CheckoutService:
    def process_payment(self, method: PaymentMethod, amount: int):
        processor = PaymentProcessor()
        processor.process(method, amount)


checkout = CheckoutService()
checkout.process_payment(CreditPayment(), 2000)
checkout.process_payment(UPIPayment(), 3445)
checkout.process_payment(PaypalPayment(), 23223)
checkout.process_payment(CreditPayment(), 122434)