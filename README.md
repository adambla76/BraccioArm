# BraccioArm
Aplikacja sterująca chwytakiem robotycznym BraccioArm


![IMG_2078](https://user-images.githubusercontent.com/17962241/168301992-3848d034-9c97-40a4-adbb-84b9eed19011.JPG)
![IMG_2079](https://user-images.githubusercontent.com/17962241/168302493-e2699732-4b82-441f-8a51-3aa093014c58.JPG)
![IMG_2059](https://user-images.githubusercontent.com/17962241/168302419-0a02c997-285a-44db-af5a-e7a33804f2fd.JPG)
![IMG_2056](https://user-images.githubusercontent.com/17962241/168302748-4f3847d8-c76e-4289-9615-794eab858bb7.JPG)



# Budowa robota BraccioArm
   Robot został skonstruowany przez włoską firmę TinkerKit jako model do składania. Szczególy tej konstrukcji można znaleźć tu -> [Braccio Quick Start Guide.pdf](https://github.com/adambla76/BraccioArm/files/8688595/Braccio.Quick.Start.Guide.pdf) Zestaw zawiera szkielet robota wraz z serwo-mechanizmami oraz shield'em do Arduino Uno. Załączony przez producenta program został napisany w Arduino C i pozwalał zaledwie na przetestowanie ruchów poszczególnych przegłubów robota.
  Powyższy projekt idzie dużo dalej - został napisany w środowisku Python3, jest oparty o platformę Raspberry PI rozbudowaną o specialny moduł sterowania serwo 16 x PWM (PCA9685). Do sterowania ramieniem robota projekt korzysta z popularnego kontrolera XBOX Wireless łączącego się z RPi za pomocą technologii Bluetooth. Kolejnym elementem dodatkowym jest wyświetlacz dot-matrix 5x 8x8led który pozwala na wyświetlanie kluczowych informacji podczas pracy urządzenia

# Sterowanie robotem z poziomu Python3
  Szczegóły dot programu sterującego ramieniem robota Braccio można znaleźć tu -> [Robomania-BraccioArm.pdf](https://github.com/adambla76/BraccioArm/files/8688789/Robomania-BraccioArm.pdf)

# Robot BraccioArm podczas akcji:
* [programowanie sekwencji za pomocą kontrolera XBOX] (https://youtu.be/3Zx2_R0rXZA)
* [zaprogramowana sekwencja ruchów - na sucho] (https://youtu.be/r5RY_0C-0PY)
* [zaprogramowana sekwencja ruchów - na mokro] (https://youtu.be/v9puDk9y0iE)
