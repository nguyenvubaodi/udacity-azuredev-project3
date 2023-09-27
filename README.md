# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |
| ------------ | ------------ | ------------ |
| *Azure Postgres Database* | Basic, 1 vCore, 5GiB | $38.56 |
| *Azure Service Bus* | Basic | $0.05 |
| *Azure App Service* | Free (F1) | $0.00 |
| *Azure Storage* | Standard (GPv2) | $11.29 |
| *Azure Function App* | Consumption | $1.80 |

## Architecture Explanation
Separating the logical structures in the processes and then deploying them to the available Azure microservices makes scalability easier when needed. Besides, using a service bus to coordinate queues helps avoid errors related to waiting times when multiple queues arise.
And, Using Azure Database for PostgreSQL helps increase the performance of deployment, backup, and restore.
Details of the services I used to migrate from on-premises to Azure are below:
1. Azure App Service
   - With app service I can deploy simply and quickly. Additionally, it can scale without availability issues and can integrate load balancing.
   - Because it is PaaS, there is not much infrastructure management and also more peace of mind about security issues.
2. Azure Function App
   - Combined with Azure Service Bus, I separated the processing of sending notifications to attendees into a separate function. It scales automatically and you only pay for compute resources when your functions are running. It saves costs because I think submitting a new notification will be infrequent.
3. Azure Service Bus
   - As stated above, in separating the notification sending processing into a separate function and deploying it to Azure Function App, I use Service Bus Queue to put the notification sending for each attendee into the queue, and process Handled in turn by Function App, helping to resolve HTTP errors such as timeout error, ....
5. Azure Database for PostgreSQL
   - Because it is PaaS, it comes with the necessary features to operate without any worries in production. For example: high availability, backup, restore, scalable, multi-region, ...
   - Additionally, there are cost benefits from migrating from on-premises servers to Azure Database and operational savings from reduced infrastructure management
