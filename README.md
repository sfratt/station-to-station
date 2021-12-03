# Station to Station: Peer-to-Peer File System

## Assumptions
* Before performing any actions, client must be connected to the server first
* Database unique constraints only apply to client name, not IP addresses or TCP/UDP port numbers
* All client TCP port numbers are dynamically created by client on startup, while server is static
* Client cannot take over from another active client without deregister the client being taken over first
* Text files (information stored in plaintext) must have their associated file extention provided to client
* Only files having not been previously published can be published by a client (hence no automatic publish)
* No file system checks are performed on files being published to ensure validity (user must be honest)
* Publish or removal fails if any file in a list of files results in an error (ACID-compliant database)
* User moving with all the same files from one client to another can simply update their info
* User moving without the same files from one client to another must deregister existing client first
* Retries are only done on timeouts and all methods perform three retries
* Deregister and retrieve all commands get responses from the server
