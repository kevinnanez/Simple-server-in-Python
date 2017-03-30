# encoding: utf-8

class Queue:

     def __init__(self):
         self.container = []  

     def isEmpty(self):
         return self.size() == 0   

     def push(self, item):
         self.container.append(item)

     def pop(self):
         return self.container.pop()

     def size(self):
         return len(self.container)

