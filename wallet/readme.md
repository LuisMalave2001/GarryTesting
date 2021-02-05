# Wallet
This module add wallets base feature in odoo.
The actions that can be performed by the user are:

 - Load wallet with payments
 - Load wallet with credit notes
 - Get wallet balance
 - Pay invoices with wallet

## API for developers

All method below will have ensure_one() constrains

### res.partner


```python  
def load_wallet_with_payments(payment_ids, wallet_id, amount):  
    """ 
        Load the wallet with payments, please, be sure that the amount 
        is correctly
        :param payment_ids: payments that will pay the wallet
        :param wallet_id: the wallet to load
        :param amount: how much will be loaded.
        :return: the moves created to load wallet 
    """  
```

```python  
def load_wallet_with_credit_notes(credit_note_ids, wallet_id, amount)):
    """
        Load the wallet with credit notes, please, be sure that the 
        amount is correctly
        :param credit_note_ids: credit notes that will pay the wallet
        :param wallet_id: the wallet to load
        :param amount: how much will be loaded.
        :return: the moves created to load wallet
    """  
```

```python  
def get_wallet_balances_json(wallet_ids: list) -> str:  
    """ Returns wallet_id current balance as json with the form:
	    {
		    "wallet_name": "<wallet name>",
		    "wallet_id": <wallet id>,
			"wallet_balance": <wallet balance>
		    "partner_id": <partner_id>,
		    "partner_name": <partner_name>,
	    }
	    wallet_id : if empty or falsy it will return all wallet balances
    """ 
```
There is also a computed field that will return the same json, this is
used for example in *pos_pr_wallet*.
And there is a dict version of this: **get_wallet_balances_dict** 

The field is **json_dict_wallet_amounts**
### account.move

```python  
def pay_with_wallet(wallet_payment_dict):  
    """ Pay the current invoice with wallet 
        wallet_payment_dict: should be a dict with the form
        {wallet_id: amount,...} this method only work for invoices 
        that has the same partner_id. wallet_id is an wallet
        enviroment object
    """  
```