from enum import Enum


class DeliveryStatus(Enum):
    AT_HUB = 1;
    EN_ROUTE = 2;
    DELIVERED = 3;
    NOT_PREPARED = 4;

class DelPackage:
    def __init__(self, id, address, city, zipcode, weight, specialNotes = None, deadline="EOD",
     status=DeliveryStatus.AT_HUB, timeDelivered=None):
        self.id = id;
        self.address = address;
        self.city = city;
        self.zipcode = zipcode;
        self.weight = weight;
        self.specialNotes = specialNotes;
        self.deadline = deadline;
        self.status = status;
        self.timeDelivered = timeDelivered;
        self.sortedFlag = False

    
    def setStatus(self, value):
        if self.status == value:
            raise Exception(("DelPackage value is already set"))
        print(f"Changing status of package {self.id} from {self.status.name} to {value.name}")
        self.status = value