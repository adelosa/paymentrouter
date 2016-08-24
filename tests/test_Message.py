from __future__ import absolute_import

import unittest
from datetime import date

from mongoengine import connect, Q

from paymentrouter.model.Message import Message, build_message


class MessageTestCase(unittest.TestCase):

    def test_get_message_data(self):
        """
        demo how to construct transaction document for storage
        """
        # create messages
        messages = list()
        template = {
            'source': 'RBA',
            'format_name': 'my_format',
            'format_version': 2,
            'queue': 'my_queue',
            'payment_date': date(2000, 1, 1),
            'data': {'value1': '123123', 'value2': 123123}
        }
        # OK - process
        messages.append(build_message(template=template))
        # wrong format - bridge
        messages.append(build_message(format_name='new_format', template=template))
        # wrong version - bridge
        messages.append(build_message(format_version=1, template=template))
        # future date
        messages.append(build_message(payment_date=date(2000, 1, 2), template=template))

        # use the mock instance
        connect('test', host='mongomock://localhost')

        # save the record
        for message in messages:
            message.save()

        # get the items back
        messages_out = Message.objects(
            Q(distribution__queue='my_queue') &
            Q(status='ready') &
            Q(payment_date__lte=date(2000, 1, 1)) & (
                Q(collection__format__name='my_format') &
                Q(collection__format__version=2)
            )
        )

        # check the output
        self.assertEqual(1, len(messages_out))
        output_record = messages[0]
        self.assertIsNotNone(output_record.id)
        self.assertEqual('RBA', output_record.collection.source)
        self.assertEqual('my_queue', output_record.distribution.queue)
        self.assertEqual('123123', output_record.collection.data['value1'])
        self.assertEqual(2, output_record.collection.format.version)
        self.assertEqual('ready', output_record.status)

        print("{},{},{}".format(
            output_record.collection.source,
            output_record.collection.data['value1'],
            output_record.status)
        )

        # get the messages requiring bridging back
        bridge_out = Message.objects(
            Q(distribution__queue='my_queue') &
            Q(status='ready') &
            Q(payment_date__lte=date(2000, 1, 1)) & (
                Q(collection__format__name__ne='my_format') |
                Q(collection__format__version__ne=2)
            )
        )

        self.assertEqual(2, len(bridge_out))
