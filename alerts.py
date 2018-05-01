

def alert_all(temp_thresh):
    send_email('lynk.cowboy@gmail.com', temp_thresh)


def send_email(to, temp_thresh):
    import smtplib

    TO = to
    SUBJECT = 'F.I.S.H. Alert!'
    TEXT = 'Your fish tank has reached a temperature of above {} degrees F'.format(temp_thresh)

    # Gmail Sign In
    gmail_sender = 'fish.alert.manager@gmail.com'
    gmail_passwd = 'somethingisfishy'

    # You have to allow access to less secure apps or else it won't work

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)

    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', TEXT])

    try:
        server.sendmail(gmail_sender, [TO], BODY)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

    server.quit()

