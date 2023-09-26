import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: {}'.format(notification_id))

    # TODO: Get connection to database
    conn = psycopg2.connect(
        host="project3-psql.postgres.database.azure.com",
        database="techconfdb",
        user="azureuser@project3-psql",
        password="password@123"
        )
    logging.info('Connected!')

    try:
        # TODO: Get notification message and subject from database using the notification_id
        cur = conn.cursor()
        cur.execute('select message, subject from notification where id={}'.format(notification_id))
        message, subject = cur.fetchone()

        # TODO: Get attendees email and name
        cur.execute('select first_name, email from attendee')
        attendees = cur.fetchall()

        # TODO: Loop through each attendee and send an email with a personalized subject
        count = 0
        for attendee in attendees:
            first_name = attendee[0]
            email = attendee[1]

            # Create mail
            mail = Mail(from_email="info@techconf.com", to_emails=email, subject='To {}: {}'.format(first_name, subject), html_content=message)
            # Send mail
            try:
                sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
                response = sg.send(mail)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)

            count += 1

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        status = 'Notified {} attendees'.format(count)
        cur.execute("update notification set status = '{}', completed_date = '{}' where id={}".format(status, datetime.now(), notification_id))
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        conn.close()