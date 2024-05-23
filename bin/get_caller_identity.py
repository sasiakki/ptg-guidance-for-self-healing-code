import boto3

class AccountNumberGetter:
    def __init__(self):
        self.client = boto3.client('sts')

    def get_account_number(self):
        account_number = self.client.get_caller_identity().get('Account')
        return account_number