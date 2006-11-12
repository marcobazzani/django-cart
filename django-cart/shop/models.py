# The shopping cart and the items within it.

# The cart is held in the Django session object, which is backed by
# the django_session DB table (and so you'll need to clear this table
# if you change the serialization of any members below e.g. by renaming 'Items').

from dharmaseed.talks.models import Talk

PRICE=12 # All units have a price of $12 for now.

class Item:
    def __init__(self, sku, count, desc, teacher):
        self.description = desc
        self.teacher = teacher
        self.sku = sku
        self.count = count
        self.unitprice = PRICE
        self.price = PRICE
        self.returnUrl = ''

    def summary_description(self):
        return (self.teacher + ": " + self.description)[:127]

    def incr_count(self):
        self.count += 1
        self.price = self.count*PRICE

    def set_count(self, count):
        self.count = count
        self.price = self.count*PRICE

# A Cart holds items. We take pains to maintain the list of items in
# the order they were originally added.

class Cart:
    def __init__(self):
        self.Items = {}
        self.itemorderer = 0

    def get_item(self, sku):
        for item in self.Items.values():
            if item.sku == sku:
                return item

    def get_item_key(self, sku):
        for key in self.Items.keys():
            if self.Items[key].sku == sku:
                return key
        self.itemorderer += 1
        return self.itemorderer

    def get_total_price(self):
        total = 0
        for item in self.Items.values():
            total += item.price
        return total

    def get_total_count(self):
        total = 0
        for item in self.Items.values():
            total += item.count
        return total

    def add_item(self, sku):
        object_list = Talk.objects.filter(talk_code__exact=sku)
        if len(object_list):
            desc = object_list[0].title
            teacher = object_list[0].teacher.name
            key = self.get_item_key(sku)
            self.Items[key] = self.get_item(sku) or Item(sku, 0, desc, teacher)
            self.Items[key].incr_count()

    def update_item(self, sku, count):
        item = self.get_item(sku)
        if item:
            item.set_count(count)
            if count == 0:
                del self.Items[self.get_item_key(sku)]

    def has_items(self):
        return len(self.Items) != 0

    def items(self):
        return self.Items.values()

    def empty_cart(self):
        self.Items = {}

    def set_return_page(self, url):
        self.returnUrl = url
