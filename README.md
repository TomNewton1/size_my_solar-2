#### Description:
A website where visitors can purchase a Solar Photovoltaic drawing/quotation for their property. Users that visit the website are able to browse available drawing options, pinpoint their property on a satellite map, enter their contact and address details, select the drawing/design/quotation they would like and purchase the drawing through Stripe payment. Once a client has made a purchase, Admin users ("designers") are able to login and view available job listings. Individual admin users can then select the jobs they would like to complete and once completed (pdf quotation/drawing) send them to the client via an automated email. 


#### Frontend:
The frontend of the website uses HTML, CSS and Bootstrap. JS is used to incorporate the Google Maps functionality. 

#### Backend:
The back end is built in python using the flask framework. SQLite was used as the database and then upgraded to postgres for deployment. 

###### CRUD Functionality
Users with admin accounts ("solar PV Designers") are able to login and view any purchases made by clients. Tables auto update based on when a new purchase is made. Admin users are then able to select available projects so that they are updated in their own "selected projects page". Once a design/quotation has been completed admin users can upload pdf files which are then automatically emailed to clients. Once a pdf has been sent to the client the job is considered complete and the order will remove itself from the available projects page. 


###### User Mixin
There are various admin accounts who are able to fulfill client orders. Each admin is able to see the available orders list but within their "selected projects page" they are only able to see the projects that they originally selected. 

#### Payment Integration:
Stripe has been implemented as the payment service used to fulfill client orders. This is possible using the Stripe API which allows you to create a checkout page. The checkout page handles the product that the customer is purchasing, the costs, bank transaction details etc. 

Webhooks are used to ensure purchases have been completed successfully notifying that the payment has been received. 

#### Google Maps Integration:
The google maps API was used to incorporate an interactive satellite map. This was combined with Google's auto-address functionality to allow users to easily search for their property on the map. This feature was used so that customers could drop a pin on the property that they would like a drawing for. Lat and Lng coordinates were also extracted from the pin to ensure that the exact location of the property was obtained. 

#### Automated Emails:

Flask mail was used to send automated emails to clients. 

#### Web Hosting:

The application is hosted on Heroku. Heroku allows you to host web applications and has additional functionality such as postgres integration. 

A domain name was purchased from Google Domain names. 
