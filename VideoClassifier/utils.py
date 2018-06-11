# Simple function wrapping mkdir in catch FileExistsError
def tryCreateDirectory(self, dir):
    try:
        os.mkdir(dir);
    except FileExistsError:
        pass