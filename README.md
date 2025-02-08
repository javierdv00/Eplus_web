# Eplus_web
website to connect to generate energyplus simulation

 - create app account

 what to do:
  ok - create sign in
  ok - create register (autentication by email link)
  ok - create sign out
  ok - save user in the DB
  - user can have diferent plan level (Free, Shawbox, Pbalance, etc) - (free, standar, premium, etc)

later:
  - change paswword
  - change email
  - change plan level


update in the code:
 1- the login redirect to a ramdon page, should go to home - do it without chatpgt, hsould be easy
 2- the user is create in DB before the autentification of the email, so i can not recreate with this user is the email was no autenticate.
 how can send another autentication link?