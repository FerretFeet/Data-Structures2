from enum import Enum


class Hashmap:
    def __init__(self, length):
        self.data = [[None] for el in range(length)];
        self.length = length;


    def _hash(self, key):
        return key % self.length;
    
    def insert(self, key, value):
        hashvalue = self._hash(key)
        # counter used to check if range is full
        counter = 0;
        if self.data[hashvalue] == [None]:
            self.data[hashvalue] = [key, value];
            return self.data[hashvalue]

        # Collision handling
        elif self.data[hashvalue] != [None]:
            if counter == self.length:
                print("Hashmap storage is full.")
            counter += 1;
            if hashvalue < self.length - 1:
                hashvalue += 1;
            elif hashvalue >= self.length - 1:
                hashvalue = 0;
    
    def lookup(self, key):
        target = self.data[self._hash(int(key))]
        if target == False:
            print("Object not found with key: " + key);
        #generate a list of key:values for object attributes
        attributes = vars(target[1])

        #print items, then return the object
        # for attr_name, attr_val in attributes.items():
            #Enum needs special case to look nice
            # if isinstance(attr_val, Enum):
            #     print(f"{attr_name}: {attr_val.name}")
            # else:
            #     print(f"{attr_name}: {attr_val}");
        
        return target;