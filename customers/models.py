import json
from typing import List, Dict, Optional

from django.contrib.auth.models import User
from django.db import models


# class EmailList(models.Model):
#     dictionary = models.TextField()
#
#     def __init__(self, email_list: Optional[Dict[str, List[str]]]):
#         super(EmailList, self).__init__()
#         if email_list is not None:
#             self.dictionary = json.dumps(email_list)
#         else:
#             self.dictionary = "{}"
#
#     def __dict__(self):
#         return json.loads(self.dictionary)
#
#     def __getitem__(self, email: str):
#         return json.loads(self.dictionary)[email].split(",")
#
#     def __setitem__(self, email: str, value: List[str]):
#         dictionary = json.loads(self.dictionary)
#         dictionary[email] = ",".join(value)
#         self.dictionary = json.dumps(dictionary)
#
#     def __repr__(self):
#         return f"EmailList({json.dumps(self.dictionary)})"


class Customer(models.Model):
    display_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15)
    status = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # email_list = models.OneToOneField(EmailList, on_delete=models.CASCADE)

    def __str__(self):
        return self.display_name
