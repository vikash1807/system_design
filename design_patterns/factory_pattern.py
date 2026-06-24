"""
object creation logic is complex or conditional

"""

# mainly there are three type of implementing factory pattern.

# 1 : simple factory -> Here you can add a simple factory class that returns the object of the specific class you need, by taking the input of type.

class NotifierFactory:

    @staticmethod
    def create_notifier(notifier_type):
        match notifier_type:
            case "email":
                return EmailNotifier()
            case "sms":
                return SMSNotifier()
            



# type 2 -> registry pattern -> Instead of hardcoding match cases, use a central registry (hash-map). new products register themselves.

from abc import ABC, abstractmethod

# 1. Base Product
class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount: float):
        pass

# 2. The Factory with a Registry
class PaymentFactory:
    _registry = {}

    @classmethod
    def register(cls, payment_type: str):
        """Decorator to register new processors automatically."""
        def decorator(subclass):
            cls._registry[payment_type] = subclass
            return subclass
        return decorator

    @classmethod
    def create(cls, payment_type: str, *args, **kwargs) -> PaymentProcessor:
        processor_class = cls._registry.get(payment_type)
        if not processor_class:
            raise ValueError(f"Unknown payment type: {payment_type}")
        return processor_class(*args, **kwargs)

# 3. Adding new products requires ZERO changes to the factory above
@PaymentFactory.register("stripe")
class StripeProcessor(PaymentProcessor):
    def process(self, amount: float):
        return f"Processing ${amount} via Stripe"

@PaymentFactory.register("paypal")
class PayPalProcessor(PaymentProcessor):
    def process(self, amount: float):
        return f"Processing ${amount} via PayPal"
    

# type 3 -> factory method pattern -> If creation logic is complex (e.g., different products require wildly different setup steps, dependencies, or configuration arguments), mapping strings to classes isn't enough.
# Then define creator subclasses as well.

from abc import ABC, abstractmethod

# Product Interface
class Document(ABC):
    @abstractmethod
    def export(self):
        pass

# Concrete Products
class PDFDocument(Document):
    def export(self): return "Exporting PDF..."

class CSVDocument(Document):
    def export(self): return "Exporting CSV..." 

# Creator Interface
class DocumentCreator(ABC):
    @abstractmethod
    def create_document(self) -> Document:
        """The Factory Method"""
        pass

    def business_logic(self):
        # The core application uses this to work with products polymorphically
        doc = self.create_document()
        return f"System Status: {doc.export()}"

# Concrete Creators
class PDFCreator(DocumentCreator):
    def create_document(self) -> Document:
        return PDFDocument()

class CSVCreator(DocumentCreator):
    def create_document(self) -> Document:
        return CSVDocument()

