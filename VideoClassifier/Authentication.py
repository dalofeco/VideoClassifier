

class AccountManager():
    
    def __init__(self):
        
        # Associative array mapping username hashes to keys
        self.accounts = {}
        
    def addAccount(self, username, password):
        
        salt = generateID(8)
        
        account = {
            "username": username,
            "authentication": sha1(username + salt + password),
            "salt": salt
        }
        
    def authenticateAccount(self, username, authentication)

class SessionManager():
    
    def __init__(self):
        
        # Associative array mapping session id to client
        self.sessions = {}
        
        
    # Creates a new session for a client and returns its ID
    def newSession(self, clientData):
        
        sessionID = generateID(8)
        
        # Add a session start time stamp
        clientData.sessionStart = time.time()
        
        # Save client data under session id
        sessions[sessionID] = clientData
        
        return sessionID
        
        
# Generates a random secure ID 
def generateID(length):

    # List of valid chars for session ID
    validChars = string.ascii_uppercase + string.ascii_lowercase + string.digits

    # Generate the random id of defined length
    return "".join(random.choice(validChars) for _ in range(length))

        
# SHA1 hash function helper
def sha1(plaintext):
    
    # Compute sha1 hash and transform to hex
    hash = binascii.hexlify(hashlib.sha1(plaintext.encode()).digest())
    
    return hash