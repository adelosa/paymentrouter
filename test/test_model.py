import os
import datetime
import unittest
import logging

from paymentrouter.model import Payment, db

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class ModelTestCase(unittest.TestCase):

    def test_peewee_orm(self):

        db_filename = 'modeltestcase.db'
        if os.path.exists(db_filename):
            os.remove(db_filename)
        db.init(db_filename)
        # db.create_tables([Payment])
        db.create_table(Payment)

        # Create 50 trans on 1/1/2016
        for vari_val in range(1, 50):
            my_payment = Payment.create(
                payment_type="transfer",
                payment_amount=100+vari_val,
                payment_amount_exponent=2,
                payment_description="test transaction",
                source_type='account',
                source_routing='484799',
                source_reference="123456789",
                destination_type='account',
                destination_routing='484799',
                destination_reference="123456789",
                payment_in_date=datetime.datetime(2016, 1, 1)
            )
            my_payment.save()

        # Create 50 trans on 2/1/2016
        for vari_val in range(51, 100):
            my_payment = Payment.create(
                payment_type="transfer",
                payment_amount=100+vari_val,
                payment_amount_exponent=2,
                payment_description="test transaction",
                source_type='account',
                source_routing='484799',
                source_reference="123456789",
                destination_type='account',
                destination_routing='484799',
                destination_reference="123456789",
                payment_in_date=datetime.datetime(2016, 1, 2)
            )
            my_payment.save()

        for payment_item in Payment.select():
            print_table_values(payment_item)

        print("Retrieve a single record")
        a_payment = Payment.get(payment_id=65)
        print_table_values(a_payment)

        print("Retrieve a selection based on amount")
        some_payments = Payment.select().where(Payment.payment_amount > 160, Payment.payment_amount < 170)
        for payment_item in some_payments:
            print_table_values(payment_item)

        print("Retrieve based on in date")
        some_payments = Payment.select().where(Payment.payment_in_date == datetime.datetime(2016, 1, 1))
        for payment_item in some_payments:
            print_table_values(payment_item)

        db.close()


def print_table_values(record):
    output = ""
    for field in type(record)._meta.fields:
        output += "{}={},".format(field, getattr(record, field))
    print(output)


if __name__ == '__main__':
    unittest.main()
