class Email:
    def __init__(self, builder):
        self.to = builder._to
        self.subject = builder._subject
        self.cc = builder._cc
        self.bcc = builder._bcc
        self.body = builder._body
        self.priority = builder._priority
        self.attachments = builder._attachments

    def __str__(self):
        # TODO: Return formatted string showing all fields
        # Expected format: Email{to='...', subject='...', cc=[...], bcc=[...], body='...', priority='...', attachments=[...]}

        return f"Email(to={self.to}, subject={self.subject}, cc={self.cc}, bcc={self.bcc}, body={self.body}, priority={self.priority}, attachments={self.attachments})"

    class Builder:
        def __init__(self, to, subject):
            self._to = to
            self._subject = subject
            self._cc = []
            self._bcc = []
            self._body = None
            self._priority = "normal"
            self._attachments = []


        def cc(self, cc):
            self._cc.append(cc)
            return self

        def bcc(self, cc):
            self._bcc.append(cc)
            return self
        
        def body(self, body):
            self._body = body
            return self
        
        def priority(self, priority):
            self._priority = priority
            return self
        
        def attachment(self, attechment):
            self._attachments.append(attechment)
            return self

        def build(self):
            return Email(self)
        


if __name__ == "__main__":
    email1 = Email.Builder("alice@example.com", "Meeting Tomorrow") \
        .body("Let's meet at 10am in conference room B.") \
        .build()

    email2 = Email.Builder("bob@example.com", "Project Update") \
        .cc("carol@example.com") \
        .cc("dave@example.com") \
        .bcc("manager@example.com") \
        .body("Attached is the Q4 report.") \
        .priority("high") \
        .attachment("q4-report.pdf") \
        .attachment("summary.xlsx") \
        .build()

    print(email1)
    print()
    print(email2)
