Canvas Bot
==========

.. image:: https://dcbadge.vercel.app/api/server/s94Rz7Ypva
   :target: https://discord.gg/s94Rz7Ypva
   :alt: Discord server invite


A Discord bot integrated with the LMS Canvas to provide students with daily reminders.

Key Features
-------------

- Can be setup to support all Canvas courses
- Daily reminders at any time
- Commands to check upcoming assignments

Setting up
----------

`Invite the bot to your server <https://discord.com/api/oauth2/authorize?client_id=987093156531142736&permissions=85056&scope=bot>`_
####################################################################################################################################

Once the bot is in your server, you will need to initialize him.

You must execute **/initialize** command which will take in 3 inputs.

Execute this command in the channel you want to receive daily reminders in
By default, reminders are sent at 15:30 UTC, this can be changed.

First input - org
###################

You can find this on your Canvas homepage in the URL

.. image:: https://cdn.discordapp.com/attachments/1015313926738694234/1128945688932266025/image.png
   :alt: Canvas org in URL

Second input - course_id
########################

Find this by clicking on the course you want to track on the Canvas homepage and again looking at the URL.

.. image:: https://cdn.discordapp.com/attachments/1015313926738694234/1128945877835325491/image.png
   :alt: Course ID in URL

Third input - token
########################

While on the Canvas website on the top left click through:

**Account -> Settings -> + New Access Token**

**+ New Access Token** can be found under the Approved Integrations heading.

.. image:: https://cdn.discordapp.com/attachments/1015313926738694234/1128944670777544704/image.png
    :alt: New Access Token button

Input anything for **Purpose** and leave **Expires** blank or input the date your course ends

.. image:: https://cdn.discordapp.com/attachments/1015313926738694234/1128945118544662559/image.png
    :alt: Generate Token

Paste the token you get as the final input into the command

.. image:: https://cdn.discordapp.com/attachments/1015313926738694234/1128944949652631582/image.png
    :alt: Token Underlined

Example of finished command
###########################

.. code::

    /admin initialize org:csulb course_id:10908 token:21372~ast5aHVdWqAIFaVJ8ASvPYxjK1YNihbwAy9tMitupfikn0c61C6OvPw9pctzJjWJ

Changing the Time Daily Reminders are Sent
------------------------------------------

Use the **/time-set** command and it will take 1 input
which will be the time you want to receive daily reminders.

The input must be in the 24-hour clock / military time

Ex. 08:30 or 22:30

**NOTE**: you will need to convert your time to UTC

Example of finished command
###########################

.. code::

    /admin time-set time:08:30

Links
------

- `Invite the Bot <https://discord.com/api/oauth2/authorize?client_id=987093156531142736&permissions=85056&scope=bot>`_
- `Join the Discord Server <https://discord.gg/s94Rz7Ypva>`_
- `More Help and Pictures for Setting up the Bot <https://docs.google.com/document/d/17O27VwJ_KlOzfie85Enp58lcKrB0LOo0rgvrY4XqJCE/edit>`_
