import os
import subprocess
import sys


def get_input():
    return input("Enter your input: ")


def get_aws_key():
    return "AJDLAKNCKAKDJKALDKEIDJAPDKEMKALDJ"


class ShoppingBasket:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def print_total(self):
        total = sum(item.price for item in self.items)
        print(f"Total: {total}")

    def print_items(self):
        items_copy = self.items.copy()
        while True:
            if len(items_copy) == 0:
                break
            item = items_copy.pop(0)
            print(f"{item.name} - {item.price}")


subprocess.check_call(get_input())

ShoppingBasket().print_items()
