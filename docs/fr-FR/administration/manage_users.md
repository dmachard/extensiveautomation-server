---
name: Manage users
---

# Manage users

The **ExtensiveTesting** solution is based on multi-user. You need to add new users to authorize testers to use it.
Also some default users exists:

- admin
- tester
- developer
- leader
- automation

For security reasons, don't forget to update password of all defaults users. No password are defined by default.

## Add a new user

1. From the web, connect in your online test center as administrator and navigate in the menu to `Administration > Users`

2. Click on ![](/docs/images/server_web_add.png) to add a user

3. Set the name and password of the user

    ![](/docs/images/web_admin_user_cred.png)

4. Selection the right level of the user and authorizations

    ![](/docs/images/web_admin_user_rights.png)

6. Set the mail. Notes: Add `;` to configure several addresses. The address email is used to send notification (test result, test report).

7. Set the default language and style of the interface web page

8. Set notification to receive by mail when one test or script is terminated

    ![](/docs/images/web_admin_user_notif.png)

9. Select projects authorized for this user and the default

    ![](/docs/images/web_admin_user_prjs.png)

10. Click on the button `Add` to validate the creation of the user.
