import smtplib
import logging
import json
import getpass
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

print("=============================")
print("<< DNIF SMTP Check Utility >>")
print("=============================")
print("Please provide SMTP configuration: ")
domain = input("Domain: ")
if not domain:
    print("Domain cannot be empty")
    sys.exit(0)

sysadmin = input("Sys Admin: ")
if not sysadmin:
    print("Sys Admin cannot be empty")
    sys.exit(0)

username = input("Username: ")
if not username:
    print("Username cannot be empty")
    sys.exit(0)

password = getpass.getpass(prompt='Password: ', stream=None)
if not password:
    print("Password cannot be empty")
    sys.exit(0)

try:
    port = int(input("Port: "))
except Exception as e:
    print("Type of value for Port is invalid")
    sys.exit(0)
if not port:
    print("Port cannot be empty")
    sys.exit(0)
if not isinstance(port, int):
    print("Type of value for Port is invalid")
    sys.exit(0)

tls = input("TLS <True/False>: ")
if tls:
    if tls in ("True", "False"):
        tls = json.loads(tls.lower())
    else:
        print("Invalid value of TLS")
        sys.exit(0)
else:
    print("TLS cannot be empty")
    sys.exit(0)
if not isinstance(tls, bool):
    print("Type of value for TLS is invalid")
    sys.exit(0)

_from = input("From: ")
if not _from:
    print("From cannot be empty")
    sys.exit(0)

_from_addr = '"DNIF "<{}>'.format(_from)
if tls:
    tls = 1
else:
    tls = 0
_server = None


def connect():
    global _server
    print("=================")
    print("Connection Result")
    print("=================")
    try:
        _server = smtplib.SMTP(domain, port, timeout=5)
        if tls == 1:
            _server.starttls()
            print("Host Connected.")
        else:
            print("Host Connected!")
    except smtplib.SMTPException as e:
        logging.error("Error connecting to host")
        sys.exit(0)
    except Exception as e:
        logging.error(e)
        sys.exit(0)

    try:
        _server.login(username, password)

    except smtplib.SMTPException as e:
        logging.error("Authentication failed: {}".format(e))
        sys.exit(0)
    except Exception as e:
        logging.error(e)
        sys.exit(0)


def close():
    global _server
    if _server:
        try:
            _server.quit()
        except smtplib.SMTPException as e:
            logging.error("Error closing connection: {}".format(e))
            sys.exit(0)
        except Exception as e:
            logging.error(e)
            sys.exit(0)


def send(content_type='html', charset='UTF-8'):
    global _server
    m_message = MIMEMultipart()
    if all(["SMTP has been tested successfully", "SMTP config verification", _from_addr, sysadmin, sysadmin]):
        m_message['From'] = _from_addr

    m_message['To'] = sysadmin
    m_message['Date'] = formatdate(localtime=True)
    m_message['Subject'] = "SMTP config verification"
    m_message['X-Mailer'] = "Python X-Mailer"
    m_message.add_header('reply-to', sysadmin)
    m_message.attach(MIMEText("SMTP has been tested successfully", content_type, charset))
    msg_text = MIMEText("""<br> 
        <hr>
        <table>
            <tr>
                <td style="font-family: Helvetica Nueue, Helvetica, Arial; font-size: 15px; color: #555;">
                    <!-- <span style="color: #303F9F; font-weight: 700;">DNIF Support Center</span><br><br> -->
                    Toll Free - <a href="tel:18001233643" style="color: #3F51B5; text-decoration: none;">1800 123 3643</a><br>
                    Email - <a href="mailto:support@dnif.it" style="color: #3F51B5; text-decoration: none;">support@dnif.it</a> &#151; <a href="mailto:sales@dnif.it" style="color: #3F51B5; text-decoration: none;">sales@dnif.it</a><br>
                    Chat - <a href="https://gitter.im/dnifhq/hello" style="color: #3F51B5; text-decoration: none;">https://gitter.im/dnifhq/hello</a>
                </td>
            </tr>
        </table>
        <table>
            <tr>
                <td style="width: 170px;">
                    <a href="https://dnif.it"><img style="margin:20px 0;" src="https://dnif.it/images/signature/dnif-blue.jpg"></a>
                </td>
                <td style="font-family: Helvetica Nueue, Helvetica, Arial; font-size: 15px; color: #555;">
                    DNIF - The "Open" Big Data Platform <br>Get started for free - Use 100GB <a href="https://dnif.it/signup.html?plan=freeforever" style="color: #3F51B5; text-decoration: none;">Free Forever</a>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <a href="https://twitter.com/dnifHQ"><img style="width: 35px; margin-right: 10px;" src="https://dnif.it/images/signature/dnif-twitter.jpg"></a>
                    <a href="https://www.linkedin.com/company/25048739/"><img style="width: 35px; margin-right: 10px;" src="https://dnif.it/images/signature/dnif-linkedin.jpg"></a>
                    <a href="https://github.com/dnif"><img style="width: 35px; margin-right: 10px;" src="https://dnif.it/images/signature/dnif-github.jpg"></a>
                    <a href="https://www.youtube.com/c/dnifhq"><img style="width: 35px; margin-right: 10px;" src="https://dnif.it/images/signature/dnif-youtube.jpg"></a>

                </td>
            </tr>
            <tr>
                <td colspan="2" style="padding: 15px 0;">
                    <a href="https://www.dsci.in/aiss-2017/"><img src="https://dnif.it/images/signature/aiss-2017.jpg"></a>
                </td>
            </tr>
            <tr>
                <td colspan="2" style="font-family: Helvetica Nueue, Helvetica, Arial; font-size: 15px; color: #555;">
                    <hr>
                    The information in this email is confidential and may be legally privileged. It is intended solely for the addressee. Access to this email by anyone else is unauthorized. If you are not the intended recipient, any disclosure, copying, distribution or any action taken or omitted to be taken in reliance on it, is prohibited and may be unlawful. All
                    rights reserved by NETMONASTERY NSPL.
                </td>

            </tr>
        </table>""", 'html', 'UTF-8')
    m_message.attach(msg_text)
    smtpserver = _server
    try:
        smtpserver.sendmail(_from_addr, sysadmin, m_message.as_string())
        close()
        return True
    except smtplib.SMTPException as e:
        logging.error("Sending email failed: {}".format(e))
        return False
    except Exception as e:
        logging.error(e)
        return False


connect()
status = send()
print("=========================")
print("SMTP Configuration Result")
print("=========================")
if status:
    print("SMTP configuration tested successfully")
else:
    print("SMTP configuration tested failed")

