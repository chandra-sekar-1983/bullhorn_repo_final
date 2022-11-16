# Dialpad Integration Framework ORM

A simple ORM for integrating both relational database and nosql through injecting an interfaced
client handling transformation between.

## Model Configuration

To exclude fields get indexed, set exclude_from_indexes in subclass model.
```python

class Example(Model):
  exclude_from_indexes = ['fields', 'to', 'exclude']
  ...
  ...
``` 

To access client
```python
User.client # pointing to the ORM_CLIENT client
user.client
```

1. Get instance
```python
user = await User.get_by_id(user_id)
```
2. Create instance
```python
user = await User.create(**dict(user))
```
3. Update instance
```python
user.age = 32
user.update()
```

4. Filter instances
```python
users = [user async for in User.all().filter(age, '=', 32)]
users = [user async for in User.all().filter(age, '>=', 32)]
users = [user async for in User.all().filter(age, '<=', 32)]
users = [user async for in User.all().filter(age, '!=', 32)]
```

5. Delete instance
```python
user.delete()
User.delete_by_id(id)
```

## Field Configuration
| NAME | TYPE | DEFAULT |
| --- | --- | --- |
| unique_key | bool | False |
| required | bool | False |
| choices | list | None |
| default | Any | None |
| indexed | bool | True |
| nullable | bool | True |


## Fields
1. IntegerField
2. ReferenceField
3. StringField
4. TextField
5. DateTimeField
6. BooleanField


## ReferenceField Usage
```python
# 1-to-1
class Token(Model):
  user = fields.ReferenceField(User, unique_key=True) # Uses user_id as token_id

# 1-to-many
class Order(Model):
  customer = fields.ReferenceField(Customer)
  ...

```
