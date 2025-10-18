"""
Core honeypot functionality
Contains the fake system simulation and command processing
"""


class FakeSystem:
    """Simulates a fake Linux system for honeypot"""

    def __init__(self) -> None:
        self.file_system = {
            "/": ["bin", "etc", "home", "usr", "var"],
            "/home": ["student", "admin", "guest"],
            "/etc": ["passwd", "shadow", "ssh", "hosts"],
            "/bin": ["ls", "cat", "who", "pwd", "cd"],
            "/usr": ["bin", "lib", "local"],
            "/var": ["log", "tmp", "cache"],
        }

        self.password_file = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-timesync:x:100:102:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
systemd-network:x:101:103:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:102:104:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
systemd-bus-proxy:x:103:105:systemd Bus Proxy,,,:/run/systemd:/usr/sbin/nologin
syslog:x:104:108::/home/syslog:/usr/sbin/nologin
_apt:x:105:65534::/nonexistent:/usr/sbin/nologin
messagebus:x:106:110::/var/run/dbus:/usr/sbin/nologin
uuidd:x:107:111::/run/uuidd:/usr/sbin/nologin
lightdm:x:108:114:Light Display Manager:/var/lib/lightdm:/bin/false
whoopsie:x:109:116::/nonexistent:/bin/false
avahi-autoipd:x:110:119:Avahi autoip daemon,,,:/var/lib/avahi-autoipd:/usr/sbin/nologin
avahi:x:111:120:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/usr/sbin/nologin
colord:x:112:121:colord colour management daemon,,,:/var/lib/colord:/usr/sbin/nologin
dnsmasq:x:113:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
kernoops:x:114:65534:Kernel Oops Tracking Daemon,,,:/:/usr/sbin/nologin
pulse:x:115:123:PulseAudio daemon,,,:/var/run/pulse:/usr/sbin/nologin
rtkit:x:116:124:RealtimeKit,,,:/proc:/usr/sbin/nologin
speech-dispatcher:x:117:29:Speech Dispatcher,,,:/var/run/speech-dispatcher:/bin/false
usbmux:x:118:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
hplip:x:119:7:HPLIP system user,,,:/var/run/hplip:/usr/sbin/nologin
saned:x:120:125::/var/lib/saned:/usr/sbin/nologin
mythtv:x:121:126::/var/lib/mythtv:/usr/sbin/nologin
admin:x:1000:1000:admin,,,:/home/admin:/bin/bash
student:x:1001:1001:student,,,:/home/student:/bin/bash
guest:x:1002:1002:guest,,,:/home/guest:/bin/bash"""

        self.connected_users = [
            {
                "username": "admin",
                "terminal": "pts/0",
                "login_time": "10:30",
                "hostname": "192.168.1.100",
            },
            {
                "username": "student",
                "terminal": "pts/1",
                "login_time": "11:15",
                "hostname": "192.168.1.101",
            },
            {
                "username": "root",
                "terminal": "tty1",
                "login_time": "09:00",
                "hostname": "localhost",
            },
        ]

    def execute_ls(self, path: str = ".") -> str:
        """Simulate ls command"""
        if path == ".":
            path = "/"
        if not path.startswith("/"):
            path = "/" + path

        entries = self.file_system.get(path, [])
        if not entries:
            return f"ls: cannot access '{path}': No such file or directory"

        return " ".join(entries)

    def execute_cat_passwd(self) -> str:
        """Simulate cat /etc/passwd command"""
        return self.password_file

    def execute_who(self) -> str:
        """Simulate who command"""
        result = []
        for user in self.connected_users:
            result.append(
                f"{user['username']:<10} {user['terminal']:<10} {user['login_time']:<10} ({user['hostname']})"
            )
        return "\n".join(result)

    def execute_pwd(self) -> str:
        """Simulate pwd command"""
        return "/home/admin"

    def execute_cd(self, path: str) -> str:
        """Simulate cd command"""
        if path in self.file_system or path in ["..", "~"]:
            return f"Changed directory to {path}"
        else:
            return f"cd: {path}: No such file or directory"


class HoneypotCore:
    """Core honeypot functionality"""

    def __init__(self) -> None:
        self.fake_system = FakeSystem()
        self.suspicious_commands = [
            "rm -rf",
            "sudo",
            "passwd",
            "su",
            "wget",
            "curl",
            "nc",
            "netcat",
            "python -c",
            "bash -c",
            "sh -c",
        ]

    def process_command(self, command: str) -> tuple[str, str]:
        """Process SSH command and return response with threat level"""
        command_lower = command.strip().lower()

        # Determine threat level
        threat_level = self._analyze_threat_level(command)

        # Process command
        if command_lower.startswith("ls"):
            parts = command.split()
            path = parts[1] if len(parts) > 1 else "."
            response = self.fake_system.execute_ls(path)
        elif command == "cat /etc/passwd":
            response = self.fake_system.execute_cat_passwd()
        elif command_lower == "who":
            response = self.fake_system.execute_who()
        elif command_lower == "pwd":
            response = self.fake_system.execute_pwd()
        elif command_lower.startswith("cd"):
            parts = command.split()
            path = parts[1] if len(parts) > 1 else "~"
            response = self.fake_system.execute_cd(path)
        elif command_lower in ["help", "?"]:
            response = """Available commands:
- ls [path]: List directory contents
- cat /etc/passwd: Show password file contents
- who: Show currently logged in users
- pwd: Show current working directory
- cd [path]: Change directory
- help: Show this help message
- exit: Quit the session"""
        elif command_lower in ["exit", "quit", "logout"]:
            response = "Goodbye!"
        else:
            response = (
                f"Command not found: {command}. Type 'help' for available commands."
            )

        return response, threat_level

    def _analyze_threat_level(self, command: str) -> str:
        """Analyze command for threat level"""
        command_lower = command.lower()

        # High threat commands
        if any(cmd in command_lower for cmd in self.suspicious_commands):
            return "high"

        # Medium threat patterns
        if any(
            pattern in command_lower
            for pattern in ["chmod", "chown", "kill", "ps", "top"]
        ):
            return "medium"

        # Low threat (normal commands)
        return "low"
