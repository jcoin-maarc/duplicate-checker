Duplicate Checker
=================

Check for potential duplicates during participant enrollment based on
initials, date of birth and assigned sex.


Setup
=====

Step 0: Install Dependencies
----------------------------

Create Python virtual environment in whichever way you prefer, and install
required packages::

    pip install -r requirements.txt

Step 1: Get OAuth credentials from Google
-----------------------------------------

Visit the Google Developers Console at https://console.developers.google.com
and create a new project. In the "APIs & auth" section, click on "Credentials",
and then click the "Create a new Client ID" button. Select "Web Application"
for the application type, and click the "Configure consent screen" button.
Put in your application information, and click Save. Once you’ve done that,
you’ll see two new fields: "Authorized JavaScript origins" and
"Authorized redirect URIs". Set the authorized redirect URI to
``http://localhost:5000/login/google/authorized``, and click "Create Client ID".
Google will give you a client ID and client secret, which we'll use in step 3.

Step 2: Create the database
---------------------------

Since we're storing OAuth data in the SQLAlchemy storage, we need to
create the database to hold that data. Fortunately, this project includes
basic command line support, so doing so is pretty straightforward.
Run this code::

    flask createdb

If it worked, you should see the message "Database tables created".

Step 3: Set environment variables
---------------------------------

You'll need to set the following environment variables:

* ``FLASK_APP``: set this to ``app``. Since this is the default value, you
  can leave it unset it you prefer.
* ``FLASK_SECRET_KEY``: set this to a random string. This is used for
  signing the Flask session cookie. This can be generated with::
  
      import secrets
      secrets.token_hex(32)
  
* ``GOOGLE_OAUTH_CLIENT_ID``: set this to the client ID
  you got from Google.
* ``GOOGLE_OAUTH_CLIENT_SECRET``: set this to the client secret
  you got from Google.
* ``OAUTHLIB_RELAX_TOKEN_SCOPE``: set this to ``true``. This indicates that
  it's OK for Google to return different OAuth scopes than requested; Google
  does that sometimes
* ``OAUTHLIB_INSECURE_TRANSPORT``: set this to ``true``. This indicates that
  you're doing local testing, and it's OK to use HTTP instead of HTTPS for
  OAuth. You should only do this for local testing.
  Do **not** set this in production!
* ``PARTICIPANT_INFO_KEY``: set this to a URL-safe base64-encoded 32-byte key
  which will be used to encrypt participant characteristics. This can be
  generated with::
  
      from cryptography.fernet import Fernet
      Fernet.generate_key().decode('utf-8')
  
  *Make sure to store this in a secure place and not lose it!*

The easiest way to set these environment variables is to define them in an
``.env`` file. You can then install the ``python-dotenv`` package to make
Flask automatically read this file when you run the dev server. This
repository has a ``.env.example`` file that you can copy to ``.env`` to get a
head start.

Step 4: Run your app and login with Google!
-------------------------------------------

If you're setting environment variables manually, run your app using the
``flask`` command::

    flask run

Then, go to http://127.0.0.1:5000/ to visit your app and log in with Google!

If your application isn't loading the environment variables from your ``.env``
file, then you need to install the ``python-dotenv`` package using ``pip``::

    pip install python-dotenv

Once the package is installed, try the ``flask run`` command again.
