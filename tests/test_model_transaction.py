import unittest

from sqlalchemy import create_engine, Integer
from sqlalchemy.orm import sessionmaker
import testing.postgresql

from paymentrouter.model.Transaction import Base, Transaction, TransactionStatus, build_message


class ModelTransactionTestCase(unittest.TestCase):

    def test_creating_transaction(self):

        with testing.postgresql.Postgresql() as postgresql:
            print("url={}".format(postgresql.url()))
            print("data directory={}".format(postgresql.get_data_directory()))

            engine = create_engine(postgresql.url())
            Session = sessionmaker(bind=engine)

            # Create schema
            Base.metadata.create_all(engine)

            # Create session
            session = Session()
            print("session started")

            # Add transactions
            for sub_id in range(20):
                session.add(build_message(submission_id=sub_id, collection_data={'json_id': sub_id, 'two': 2}))
            session.commit()
            print("added transaction")

            # test standard query
            all_transactions = session.query(Transaction).filter(Transaction.status == TransactionStatus.ready).all()
            self.assertEqual(20, len(all_transactions))

            # test json field query
            json_query = session.query(Transaction).filter(Transaction.collection_data['json_id'].astext.cast(Integer) >= 10).all()
            self.assertEqual(10, len(json_query))

            session.close()


if __name__ == '__main__':
    unittest.main()
