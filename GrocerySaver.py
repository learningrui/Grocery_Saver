import os
import pathlib
import sqlite3  as lite
import requests
from tkinter import *
from os import system
from tkinter import messagebox
from tkinter import filedialog


class ShoppingList:
    """
    Initialize shopping list
    """
    def __init__(self):
        self.items=[]
        self.get_items()


    def get_items(self):

        shoppinglist_file = os.path.join(pathlib.Path().absolute(),"myShoppingList.txt")
        shoppinglist = open(shoppinglist_file,'r')
        shoppingitems = shoppinglist.readlines()
        for item in shoppingitems:
            self.items.append(item.strip())


class Store:
    """Store Object for store information"""
    def __init__(self, store_name=""):
        self.store_name=store_name
        self.store_website = ""
        self.store_API = ""
        self.store_address =""
        self.store_hour=""
        self.store_API_key = ""
        self.store_info=self.query_store(self.store_name)
        self.get_store_info()
    def query_store(self,store_name):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        database=r"GrocerySaver.db"
        try:

            conn = lite.connect(database)
            cur = conn.cursor()

            cur.execute("SELECT * FROM Stores WHERE store_name=?COLLATE NOCASE", (store_name,))
        #         cur.execute("SELECT * FROM sqlite_master WHERE type='table'")
            store_info = (cur.fetchall())

        except Error as e:
            print(e)

        return store_info

    def get_store_info(self):
        self.store_website= self.store_info[0][2]
        self.store_address= self.store_info[0][3]
        self.store_hour = self.store_info[0][4]
        self.store_API = self.store_info[0][5]


class StoreShoppingList(ShoppingList):
    """Inheritence of the Shopinglist, share parent shoppinglist, and each store has its own fulfulment"""
    def __init__(self,store):
        super().__init__()
        self.Total = 0
        self.fulfilment = []
        self.fulfilled_Items = 0
        self.Total_Unit_Price = 0
        self.store = Store(store)
        self.shop()


    def shop(self):
        for item in self.items:
            #shop item
            #check if fulfille:
            item = Item(item, self.store)
            if item.fulfilled == 1:
                self.fulfilment.append(item)
                self.fulfilled_Items += 1
                self.Total += round(item.price, 2)
                self.Total_Unit_Price += round(item.unit_price.unit_price, 2)


class Item:
    """Item object for item information, price, unit proce"""
    def __init__(self, item = None, store = None):
        self.item = item
        self.store = store
        self.price = 0
        self.descritpion =""
        self.size = ""
        self.unit_price = UnitPrice()
        self.fulfilled = 0
        if (self.store.store_API =="Yes"):
            self.get_price_from_API(self.item)
        else:
            self.get_price_from_DB(self.store.store_name,self.item)



    def get_price_from_DB(self, store, item):
        """check product information"""
        conn = None
        database=r"GrocerySaver.db"
        try:

            conn = lite.connect(database)
            cur = conn.cursor()

            cur.execute("select pps. * from PricePerStore pps inner join stores s on pps.store_id=s.store_id where s.store_name=? COLLATE NOCASE and product like ? COLLATE NOCASE", (store, item))
        #         cur.execute("SELECT * FROM sqlite_master WHERE type='table'")
            product_info = (cur.fetchall())

        except Error as e:
            print(e)
        if len(product_info)>0:
            self.price = product_info[0][2]
            self.description = product_info[0][5]
            self.size = product_info[0][3]
            if float(self.size.split()[0]) != 0:
                self.unit_price.unit_price = round(self.price/float(self.size.split()[0]),2)
                for unit in range(1,len(self.size.split())):
                    self.unit_price.unit_type += self.size.split()[unit]
                self.unit_price.unit_price_converter()
            else:
                self.unit_price.unit_price = round(self.price, 2)
            self.fulfilled = 1


    def get_price_from_API(self,item):
        #if store has API, use this
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            #from my client info to get token
            'Authorization': 'Basic cnVpbGktYTQyYjk1ZWVhNmUwOGQ3MzM5NjY1MzU5YzQxN2I5NTY3NDQ5MjA4NTEwNjIzNjI0OTg2OlZrSHNHNDRFbkV0aWF3SExQRnJXaHBaSlFyekU2clBVRUhFUWJBMFg=',
        }

        data = {
          'grant_type': 'client_credentials',
          'scope': 'product.compact'

        }

        response = requests.post('https://api.kroger.com/v1/connect/oauth2/token', headers=headers, data=data)
        response_json=response.json()
        access_token=response_json["access_token"]

        item = item
        locationid="1400943".zfill(8)


        headers = {
            'Accept': 'application/json',
            'Authorization': '',
        }

        headers["Authorization"]="Bearer "+ access_token
        #todo::location should be by zipcode
        response = requests.get('https://api.kroger.com/v1/products?filter.term={term}&filter.locationId={location}'.format(term=item,location=locationid), headers=headers)
        #if found item
        if (len(response.json()["data"])>0):

            self.price=(response.json()["data"][1]["items"][0]["price"]["regular"])
            self.description= (response.json()["data"][1]["description"])
            self.size=response.json()["data"][1]["items"][0]["size"]
            if float(self.size.split()[0]) != 0:
                self.unit_price.unit_price = round(self.price/float(self.size.split()[0]),2)
                for unit in range(1,len(self.size.split())):
                    self.unit_price.unit_type += self.size.split()[unit]
                self.unit_price.unit_price_converter()
            else:
                 self.unit_price.unite_price = round(self.price, 2)
            self.fulfilled = 1


class UnitPrice:
       """Proof of concept, for now just implemented dozen to count, gal to fl oz converter"""
       def __init__(self):
           self.unit_price = 0.00
           self.unit_type = ""
       #compare item_unit_price
       #not used for this project, because it only consider total unit price saving.
       #this magic method can be potentially used to do item unit price comparison
       def __eq__(self, other):
           if self.unit_price == other.unit_price:
                   return True
           else:
                   return False
       def __lt__(self, other):
           if self.unit_price < other.unit_price:
                   return True
           else:
                   return False
       def __gt__(self, other):
           if self.unit_price > other.unit_price:
                   return True
           else:
                   return False
       def unit_price_converter(self):
               # dozen convert to 12 ct
               # proof of concept standard unit types are ct, lb, fl oz, oz
               if self.unit_type == "dozen":
                   self.unit_type = "ct"
                   self.unit_price = round(self.unit_price/12, 2)
               if self.unit_type == "gal":
                   self.unit_type = "fl oz"
                   self.unit_price = round(self.unit_price/128, 2)


class ShoppingStores:
     def __init__(self):
         self.stores = []
         self.get_stores()

     def get_stores(self):
         shoppingstorefile = os.path.join(pathlib.Path().absolute(),"ShoppingStoreList.txt")
         shoppingstorelist = open(shoppingstorefile,'r')
         shoppingstores = shoppingstorelist.readlines()
         for store in shoppingstores:
             self.stores.append(Store(','.join(store.split())))


class Suggestion:
     def __init__(self):
         self.Shopping_Stores = ShoppingStores()
         self.estimated_savings = 0
         self.suggested_store={}
         self.fulfilment_by_store = {}
         self.get_fulfilment_by_store()

     def get_fulfilment_by_store(self):
         for store in self.Shopping_Stores.stores:
             storeShoppingList=StoreShoppingList(store.store_name)
             self.fulfilment_by_store.update({store:[storeShoppingList.Total, storeShoppingList.fulfilment,storeShoppingList.fulfilled_Items, storeShoppingList.Total_Unit_Price]})


     def get_suggested_store(self):
         self.suggested_store = {}

     def get_estimated_savings(self):
         """for the same fulfilment, get the savings by Most expensive - Most inexpensive"""
         self.estimated_savings = 0

     def __repr__(self):
         s = ""
         return s


class SuggestionbyTotal(Suggestion):
    """set suggestions, savings and printing basing on Total Price"""
    def __init__(self):
        super().__init__()
        self.get_suggested_store()
        self.get_estimated_savings()

    def get_suggested_store(self):
        fulfilmentItems = 0
        bestPrice = 0.0
        bestStore = ""
        for storeFulfilment in self.fulfilment_by_store:
            if self.fulfilment_by_store[storeFulfilment][2] > fulfilmentItems:
                fulfilmentItems = len(self.fulfilment_by_store[storeFulfilment][1])
                bestStore = storeFulfilment
                bestPrice = self.fulfilment_by_store[storeFulfilment][0]
            elif self.fulfilment_by_store[storeFulfilment][2] == fulfilmentItems:

                if self.fulfilment_by_store[storeFulfilment][0] < bestPrice:
                    bestPrice = self.fulfilment_by_store[storeFulfilment][0]
                    bestStore = storeFulfilment
        self.suggested_store = {f"Suggested Store": bestStore, "Total Price": round(bestPrice,2),"Fulfilled Items": fulfilmentItems}

    def get_estimated_savings(self):
        """for the same fulfilment, get the savings by Most expensive - Most inexpensive"""
        all_prices= [self.fulfilment_by_store[store][0] for store in self.fulfilment_by_store if self.fulfilment_by_store[store][2] == self.suggested_store["Fulfilled Items"]]
        self.estimated_savings = round(max(all_prices)- min(all_prices),2)

    def __repr__(self):
        #Suggested Store Information
        s = "Suggested Store is: " + self.suggested_store["Suggested Store"].store_name + "\n\n"
        s += "Store Address: "+self.suggested_store["Suggested Store"].store_address + "\n"
        s += "Store Website: "+self.suggested_store["Suggested Store"].store_website + "\n"
        s += "Store Hours: "+self.suggested_store["Suggested Store"].store_hour + "\n\n\n"
        #Estimated Savings
        s += "Estimated Savings is: $" + str(self.estimated_savings) +"\n"
        s += "The suggestion is based on total price\n"
        if self.estimated_savings==0:
            s += "The suggestion is the store that fulfill the most grocery items\n"
        s += "\n\n"

        for storeFulfilment in self.fulfilment_by_store:
            s += storeFulfilment.store_name +": Estimated Receipt\n\n"
            s += "Item".ljust(20, "-")+ "Item Description".ljust(40, "-") + "size".ljust(20, "-")+ "Price".ljust(15, "-")
            s += "\n"+ "-"*100+'\n'
            s += "\n".join([item.item.ljust(20, "-") + item.description[0:40].ljust(40, "-") + item.size.ljust(20, "-") + str(item.price).ljust(15, "-") for item in self.fulfilment_by_store[storeFulfilment][1]])
            s += "\n"+ "-"*100+'\n'
            s += "Estimated total: " + str(round(self.fulfilment_by_store[storeFulfilment][0],2)) + "\t" + "Fulfilled Items: "+str(self.fulfilment_by_store[storeFulfilment][2]) +"\n\n\n\n"

        return s


class SuggestionbyUnitPrice(Suggestion):
    def __init__(self):
        super().__init__()
        self.get_suggested_store()
        self.get_estimated_savings()

    def get_suggested_store(self):
        fulfilmentItems = 0
        bestUnitPrice = 0.0
        bestStore = ""
        for storeFulfilment in self.fulfilment_by_store:

            if self.fulfilment_by_store[storeFulfilment][2] > fulfilmentItems:
                fulfilmentItems = len(self.fulfilment_by_store[storeFulfilment][1])
                bestStore = storeFulfilment
                bestUnitPrice = self.fulfilment_by_store[storeFulfilment][3]
            elif self.fulfilment_by_store[storeFulfilment][2] == fulfilmentItems:

                if self.fulfilment_by_store[storeFulfilment][3] < bestUnitPrice:
                    bestUnitPrice = self.fulfilment_by_store[storeFulfilment][3]
                    bestStore = storeFulfilment
        self.suggested_store = {f"Suggested Store": bestStore, "Total Unit Price": round(bestUnitPrice,2),"Fulfilled Items": fulfilmentItems}

    def get_estimated_savings(self):
        """for the same fulfilment, get the savings by Most expensive - Most inexpensive"""
        all_prices= [self.fulfilment_by_store[store][3] for store in self.fulfilment_by_store if self.fulfilment_by_store[store][2] == self.suggested_store["Fulfilled Items"]]
        self.estimated_savings = round(max(all_prices)- min(all_prices),2)

    def __repr__(self):
        #Suggested Store Information
        s = f"Suggested Store is: " + self.suggested_store["Suggested Store"].store_name + "\n\n"
        s += "Store Address: "+self.suggested_store["Suggested Store"].store_address + "\n"
        s += "Store Website: "+self.suggested_store["Suggested Store"].store_website + "\n"
        s += "Store Hours: "+self.suggested_store["Suggested Store"].store_hour + "\n\n\n"
        #Estimated Savings
        s += "Estimated Unit Price Savings is: $" + str(self.estimated_savings) +"\n"
        s += "The suggestion is based on unit price\n"
        if self.estimated_savings==0:
            s += "The suggestion is the store that fulfill the most grocery items\n"
        s += "\n\n"

        for storeFulfilment in self.fulfilment_by_store:
            s += storeFulfilment.store_name +": Estimated Receipt\n\n"
            # s += "{:^20s}{:^50}{:^20s}{:^20s}{:^20s}{:^20s}".format("Item", "Item Description", "Size", "Price", "Unit Price", "Unit Type")
            s += "Item".ljust(15, "-") + "Description".ljust(40, "-") + "Size".ljust(20, "-") + "Price".ljust(20, "-") + "Unit Price".ljust(20, "-") + "Unit Type"
            s += "\n"+ "-"*150+'\n'
            s += "\n".join([item.item.ljust(15, "-") + item.description[0:40].ljust(40, "-") + item.size.ljust(20, "-") + str(item.price).ljust(20, "-") + str(item.unit_price.unit_price).ljust(20, "-") + item.unit_price.unit_type.ljust(20, "-") for item in self.fulfilment_by_store[storeFulfilment][1]])
            s += "\n"+ "-"*150+'\n'
            s += "Estimated total unit price: " + str(round(self.fulfilment_by_store[storeFulfilment][3],2))+"\t"+"Estimated total price: " + str(self.fulfilment_by_store[storeFulfilment][0]) + "\t" + "Fulfilled Items: "+str(self.fulfilment_by_store[storeFulfilment][2]) +"\n\n\n\n"

        return s


class Checkbar(Frame):
    def __init__(self, parent=None, picks=[], side=LEFT, anchor=W):
        Frame.__init__(self, parent)
        self.vars = {}
        for pick in picks:
            var = IntVar()
            chk = Checkbutton(self, text=pick, variable=var)
            chk.pack(side=side, anchor=anchor, expand=YES)
            self.vars.update({pick:var})
    def state(self):
        return  self.vars[0].get()

class NewWindow(Toplevel):

    def __init__(self, master = None, SuggestionType = None):

        super().__init__(master = master)
        self.title("New Window")
        self.geometry("1000x1000")

        if SuggestionType == "byTotal":
            s = SuggestionbyTotal()

        elif SuggestionType == "byUnit":
            s = SuggestionbyUnitPrice()

        label = Label(self, text = "Price Comparison" )
        label.pack()

        result = Label(self, text = str(s))
        result.pack()


class GrocerySaver(Frame):
    def __init__(self, parent = None):

        Frame.__init__(self, parent)

        self.parent = parent

        self.initUI()


    def initUI(self):

        # def Save():
        #     text = e.get() + " " + e1.get() + "\n"
        #     with open("text.txt", "a") as f:
        #         f.write(text)

        # frame inside root window

        # geometry method
        def Submit():
            #validate if any grocery is entered
            if not T.get("1.0","end-1c"):
                messagebox.showinfo (title = "ERROR", \
                                         message = 'Please enter your grocery list.')
            #validate if any store is selected
            elif len([var for var in stores.vars if stores.vars[var].get()==1]) == 0:
                messagebox.showinfo (title = "ERROR", \
                                         message = 'Please select at least a store.')
            #passed validation
            else:
                MsgBox = messagebox.askquestion("Form",
                                       "Are you ready to compare price?", icon="warning")
                if MsgBox == "yes":
                    SaveGroceryList()
                    SaveStoreList()
                    create_suggestion()


        self.pack()

        # button inside frame which is
        # inside root
        w = Label(self, text ='Grocery Saver', font = "50")
        w.pack()

        stores = Checkbar(self, ['Kroger', 'Walmart', 'Meijer', 'Aldi', 'Giant'])
        stores.pack(side="top",  fill=X)
        #label to indicate the grocery list
        l = Label(self, text = "Type in your grocery list below")
        #text area to enter the grocery list
        T = Text(self, height = 20, width = 50)

        T.focus_set()


        l.pack(side = "top")
        T.pack(side = "left")

        CompareOption = IntVar()
        CompareOption.set(0)

        Radiobutton(self, text="By Total Price", variable=CompareOption, value=0).pack(anchor=W)
        Radiobutton(self, text="By Unit Price", variable=CompareOption, value=1).pack(anchor=W)

        button = Button(self, text ='Compare Price', command = Submit)

        button.pack(side="top")


        def SaveGroceryList():
            #get all entered grocery list
            GroceryList=T.get("1.0","end-1c")
            Groceryfile = open("myShoppingList.txt","w")
            Groceryfile.writelines(GroceryList)
            Groceryfile.close() #to change file access modes

        def SaveStoreList():
            StoreList = ('\n'.join([var for var in stores.vars if stores.vars[var].get()==1]))
            Storefile = open("ShoppingStoreList.txt","w")
            Storefile.writelines(StoreList)
            Storefile.close()

        def create_suggestion():
            SuggestionType = "byTotal"
            if (CompareOption.get() == 1):
                 SuggestionType = "byUnit"
            NewWindow(self.parent,SuggestionType)


        self.mainloop()




def main():
    root = Tk()
    root.title("Grocery Saver")
    root.geometry("500x500")
    app = GrocerySaver(root)


if __name__ == '__main__':
    main()
