# Image describer

* Author: Oliver Edholm
* Download at http://www.screenreader.ai

This add-on gives descriptions of images for you by utilizing methods in Machine Learning.

Notes:
* The shortcut to get an image description of the current navigator object is NVDA+Control+I.
* If you configure another language than English, the description could have translation issues because it's automatically generated.
* The language of the descriptions that are generated are linked with the configured NVDA language. In other words, if you have Swedish configured, you will get Swedish descriptions, unless you change the language in the Image describer settings.
* Please include a sentence which describes that the user can assign a prefered gesture in NVDA’s input gesture dialog. Please name the cathegory in which the gesture can be changed in that dialog.

Security:
* The images are sent to a script hosted on the Google Cloud Platform for analysis. After the analysis the image gets removed from the server and will never be seen again.

For developers:
* If you want to fiddle with the add-on, first run the deps.py script.