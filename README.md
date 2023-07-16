# Car weight classification project summary

A short description and summary of my work on this project

## Task at hand

I was tasked to come up with a solution to detect if a transport coming through the checkpoint is carrying any cargo or not.

The solution needed to be solely video-based, and require no more equipment than several cameras and a processing unit.

## R-&-D

After consulting with the project manager some ideas it was decided to base determination on tire compression.

Other ways considered were:
* Ground clearance
* Acceleration and deceleration at checkpoint

## Development

### Data collection

I was provided with hours of footage of cars coming through the checkpoint with marks on which of them are empty or not. 
With the help of a basic circle detection script, I was able to extract some wheel photos and mark them based on their position (front, back, trailer). 

To clean up data script was written that discarded similar frames and found the most unique for the training process.

XML files with bounding boxes were created by hand for each frame.

Later in training filters for exposure, distortion, crop, etc. 
were applied to expand the database size and provide different case scenarios

### Model training

It was decided to split the program into two ML models, one for wheel detection and classification, 
because the basic script had proven to be ineffective, and one for weight prediction.

The idea was that the first model is going to split wheels based on their appearance into two groups, 
the ones that are suitable for the object classification model, these would be back and trailer wheels, 
and the ones that are not preferable for it, these would be front wheels.

Only back and trailer wheels were then given to the object classification model.

Retrained pre-trained models were used.

### Model testing

Below you can see the examples, bounding box represents the area that was given to the object classification model, 
if a wheel was identified as a back or trailer wheel. 

- -1 - wheel was identified as front
- 0 - wheel was identified as back or trailer and predicted to be from a transport with **no** cargo
- 1 - wheel was identified as back or trailer and predicted to be from a transport with cargo

![frame_220](https://github.com/MykhailoRp/TireProjectPrivate/assets/121835146/89ef4b4c-2c58-4461-99f1-aa102843934c)

![frame_280](https://github.com/MykhailoRp/TireProjectPrivate/assets/121835146/f7e483ce-5cea-4141-92c1-a3e2a7bd5571)

![frame_360](https://github.com/MykhailoRp/TireProjectPrivate/assets/121835146/64b0a278-c622-422c-8813-f7164c50394f)

*(This car has no cargo, however as you can see model failed to identify this)*

## Summary

Unfortunately, after several failed iterations of the object classification model, it was decided that the project required more
R&D and other ways to identify transport's load. I stopped my work on it after this.
