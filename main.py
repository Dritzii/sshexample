import paramiko
from pathlib import Path
from stat import S_ISDIR, S_ISREG


class sftpClient:
    def __init__(self, host, username, password, port):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.host, port=self.port, username=self.username, password=self.password)

    def getFilestoLocalMachine(self, locationRemote, locationLocal):
        ftp_client = self.ssh.open_sftp()
        ftp_client.get(locationRemote, locationLocal)
        ftp_client.close()

    def listAllDirectory(self):
        ftp = self.ssh.open_sftp()
        for i in ftp.listdir():
           lstatout = str(ftp.lstat(i)).split()[0]
           if 'd' in lstatout:
               print(i, 'is a directory')
           elif 'd' not in lstatout:
               print(i, 'is a file')
        for entry in ftp.listdir_attr():
            mode = entry.st_mode
            if S_ISDIR(mode):
                print(entry.filename + " is folder")
            elif S_ISREG(mode):
                print(entry.filename + " is file")


    @staticmethod
    def stringpath(path):
        # just a helper to get string of PosixPath
        return str(path)

    def tree_sftp(self, path='.', parent='/', prefix=''):
        ftp = self.ssh.open_sftp()
        # prefix components:
        space =  '    '
        branch = '│   '
        # pointers:
        tee =    '├── '
        last =   '└── '

        """
        Loop through files to print it out
        for file in tree_ftp(ftp):
            print(file)
        """
        fullpath = Path(parent, path)
        strpath = str(fullpath)

        dirs = ftp.listdir_attr(strpath)
        pointers = [tee] * (len(dirs) - 1) + [last]
        pdirs = [Path(fullpath, d.filename) for d in dirs]
        sdirs = [str(path) for path in pdirs]

        for pointer, sd, d in zip(pointers, sdirs, dirs):
            yield prefix + pointer + d.filename
            if S_ISDIR(d.st_mode):
                extension = branch if pointer == tee else space
                yield from tree_sftp(ftp, sd, prefix=prefix + extension)