Technical Details
=================

Implementation and Deployment
-----------------------------

Duplicate Checker is implemented in `Flask <https://palletsprojects.com/p/flask/>`_,
a WSGI web application framework that is part of the `Pallets Projects <https://palletsprojects.com>`_.
The code is open source and freely available under the Apache 2.0 license. The
application may be easily deployed in the cloud (e.g., Google App Engine,
AWS Elastic Beanstalk or Azure) or on one of several available WSGI servers.

Security
--------

Several steps have been taken to ensure the security of the application and of
the participant information being stored.

Encryption versus Hashing
~~~~~~~~~~~~~~~~~~~~~~~~~

As noted in the :ref:`Overview <info-encrypted>`, all participant information
is encrypted prior to storage, and the encryption key is stored separately
from the application database. Some readers may wonder why we are encrypting
this information rather than hashing it; after all, there is no need to access
this information after it has been submitted—only to compare it to that of
subsequent potential participants. Although encryption is secure as long as
the key is not compromised, the advantage of hashing is that there is no key
that must be protected. This is typically the rationale used for hashing
(e.g., as when handling user passwords).

What is important in this case, however, is that each time a new participant
is added, it is necessary to check his or her information against that of
*all* previous participants (this differs from the password management case,
where it is only required to check against the hashed value for the single
user attempting to authenticate). To do this while maintaining an acceptable
response time would require using a hash function with a very low *cost
factor*, thereby defeating the security of the hash. This is especially
problematic in this case, since the universe of possible user information
values is relatively small. For example, with two initials, two sexes, and 60
potential birth years, the participant information can take one of only
:math:`26^2 \times 2 \times (365 \times 60) \approx 30 \: \text{million}`
possible combinations. By contrast, an 8 character password including only
letters and numbers can take one of 218 trillion possible combinations. In
sum, if we were to hash the participant information we would need to set the
cost factor so low that it would be relatively easy to compute the hash of all
possible values of the participant information, even when using a different
*salt* for each entry. To wit, the additional security provided by hashing
would be essentially lost.

Participant information is encrypted using the
`Fernet <https://github.com/fernet/spec/blob/master/Spec.md>`_ symmetric
encryption (also known as "secret key") method as implemented in the Python
language `cryptography <https://cryptography.io/en/latest/index.html#>`_
package. Fernet uses 128-bit AES in CBC mode and PKCS7 padding, with HMAC
using SHA256 for authentication.

Transport Layer Security
~~~~~~~~~~~~~~~~~~~~~~~~

Duplicate Checker should be deployed so that all communication to and from the
application is protected by Transport Layer Security (TLS). This may be done
either by protecting the WSGI server itself or by deploying the application
behind a reverse proxy which is suitably secure.

Application Security
~~~~~~~~~~~~~~~~~~~~

Duplicate Checker takes several precautions to ensure the security of the
application itself:

1. We do not manage user credentials, but instead authenticate users via an
   established OAuth 2.0 provider (Google)
2. A user's session is automatically discarded and the user is logged out when
   the browser is closed (i.e., the user must re-authenticate before accessing
   the application again)
3. All input is validated and no raw queries of the database are performed,
   reducing the chance of an SQL Injection vulnerability
4. Vulnerability to a Cross-Site Request Forgery (CSRF) attack is reduced by
   using a CSRF token with all form submission
