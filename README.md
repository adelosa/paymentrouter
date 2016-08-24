# paymentrouter
a simple batch payment transaction warehouse and distribution system.

## What does it do?
Consider the steps involved in processing a file containing account 
payment instructions for a typical bank:

* You need to process files containing transactions that need to be 
posted to an account system.
* The transactions could be in different formats and you need to 
reformatted to the account system format
* The transactions may need to be routed to different account systems for 
processing because there is more the one account system
* You need to keep a record and reference to the original transaction 
details in case the transaction needs to be returned
* You need to ensure that transactions have not already been processed
* You need to do some account number swaps due to some account conversion 
performed long ago
* You need to warehouse some transactions for a future date rather than
processing right away
* You need to immediately return transactions that cannot be processed
by you.
* You need to deal with transactions that cannot be routed or processed.
* You need to create reports that -
    * show that "money in" = "momey out" + "money in the warehouse"
    * work out who owes who what
    * provide general ledger transactions

__paymentrouter__ provides this capability.

Current support for the following payment file formats
* Australian Direct Entry (BECS)


### Command line utilities

####pr_file_collection
_run this whenever you receive a payment file for processing_
* collect transaction file in given format
* determine destination queue based on rule config
* store transaction in warehouse

####pr_file_distribution
_run this whenever you want to send a payment file_
* get all transactions that have not been distributed for requested queue and processing date
* if transaction in wrong format, bridge to the new format by closing off the original 
transaction and creating new transaction in required format 
* output file in required file format

#### pr_roll_and_report
_run this when your logical business day ends and you want reports for the previous day_
* rolls business date forward one day
* generate trial balance: previous held balance + money in = money out + todays held balance
* generate detailed transaction reports
    * Collection report - what has been received
    * Distribution reports - what has been sent
* generate general ledger transaction file
