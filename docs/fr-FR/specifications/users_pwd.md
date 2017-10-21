---
name: User's password storage
---

# User's password storage

User's password are not stored in the database in clear. The password is stored in the table `xtc-users` based on a SHA1 hash with a salt.

Algorithm:

```
hash_password = SHA1 ( SALT + SHA1(user_password) )
```

Extract of the database:

![](/docs/images/server_table_pwd.png)