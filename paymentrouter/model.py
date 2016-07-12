from datetime import datetime
from peewee import *

db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Payment(BaseModel):

    payment_id = PrimaryKeyField()         # our reference
    payment_user_id = CharField(null=True)  # source reference
    payment_type = CharField()             # transfer, bpay, etc
    payment_amount = BigIntegerField()     # amount in units
    payment_amount_exponent = SmallIntegerField()     # currency exponent
    payment_description = CharField()
    source_type = CharField()              # account, bpay biller
    source_routing = CharField()           # bsb, biller code
    source_reference = CharField()         # account number, biller reference
    destination_type = CharField()
    destination_routing = CharField()      # bsb, biller code
    destination_reference = CharField()
    payment_in_date = DateField(default=datetime.today)
    payment_out_date = DateField(null=True)



