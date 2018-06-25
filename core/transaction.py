# coding: UTF-8

class Transaction:
        
    def __init__(self, input, output, amount):
        self.input = input
        self.output = output
        self.amount = amount

    def __repr__(self):
        return f"input={self.input} output={self.output} amount={self.amount}"
