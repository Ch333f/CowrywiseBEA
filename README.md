# Cowrywise Backend Engineer (Infrastructure, API Engineer, Devops) Assessment

You have been tasked to develop an application to manage books in a library. With your application, users can browse through the catalogue of books and borrow them. You are to build 2 independent API services for this application.

1. Frontend API
This API will be used to
- Enroll users into the library using their email, firstname and lastname.
- List all available books
- Get a single book by its ID
- Filter books
   - by publishers e.g Wiley, Apress, Manning
   - by category e.g fiction, technology, science
- Borrow books by id (specify how long you want it for in days)

2. Backend/Admin API
This API will be used by an admin to:
- Add new books to the catalogue
- Remove a book from the catalogue.
- Fetch / List users enrolled in the library.
- Fetch/List users and the books they have borrowed
- Fetch/List the books that are not available for borrowing (showing the day it will be available)

# Requirements
- The endpoints need not be authenticated
- The API should be built using python flask-restx framework
- Design the models as you deem fit.
- A book that has been lent out should no longer be available in the catalogue.
- The two services should use different data stores.
- Device a way to communicate changes between the two services. i.e when the admin adds a book to the catalogue via the admin api, the frontend api should also be updated with the latest book added by the admin.
- The project should be deployed using docker containers
- Add necessary unit/integration tests.
